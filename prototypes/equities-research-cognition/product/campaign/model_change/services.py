from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Mapping
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from product.campaign import services as campaign_services
from product.campaign.models import (
    AdmissibilityDecision,
    Amendment,
    ArtifactDisposition,
    ArtifactManifestVersion,
    ArtifactVersion,
    CalculationReceipt,
    ConceptualObjectVersion,
    CorrectionRecord,
    InvalidationEvent,
    ModelChangeEpisode,
    ModelChangeProposal,
    ObjectDisposition,
    Proposal,
    ProposalDisposition,
    ResearchJob,
    SourceAssertion,
    SourceDocumentVersion,
    WorkOrder,
    canonical_digest,
)

from . import adapter


PROTOCOL_VERSION = "model-change-v0/2026-08-17"
VALIDATOR_VERSION = "model-change-admissibility/v0"
NETWORK_POLICY = "closed_captured_sources"
ANNUAL_TARGET = "FY25_REVENUE_USDM"
PRELIMINARY_TARGET = "FY2025_PRELIMINARY_EARNINGS_FLASH_REVENUE"
MODEL_OUTPUT = "model-change-output.json"
ACKNOWLEDGEMENT_OUTPUT = "run-acknowledgement.json"


class ModelChangeRejected(Exception):
    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def _feature_enabled() -> None:
    if not settings.MODEL_CHANGE_V0:
        raise ModelChangeRejected("FEATURE_DISABLED", "model change work is unavailable")


def _owned(episode: ModelChangeEpisode, actor: object) -> None:
    if episode.job.owner_id != getattr(actor, "pk", None):
        raise ModelChangeRejected("NOT_FOUND", "model change episode is unavailable")


def _create(model: type, values: dict[str, object], payload: dict[str, object]):
    values["digest"] = canonical_digest(payload)
    try:
        return model.objects.create(**values)
    except (IntegrityError, ValidationError, ValueError) as exc:
        raise ModelChangeRejected(
            "CUSTODY_REJECTED", "immutable model-change custody rejected the record"
        ) from exc


def _artifact_input(value: object) -> tuple[str, str, bytes]:
    if isinstance(value, Mapping):
        filename = value.get("filename")
        media_type = value.get("media_type")
        content = value.get("content")
    else:
        filename = getattr(value, "name", None)
        media_type = getattr(value, "content_type", None) or (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        content = value.read() if hasattr(value, "read") else None
    if (
        not isinstance(filename, str)
        or not filename
        or Path(filename).name != filename
        or not isinstance(media_type, str)
        or not media_type
        or not isinstance(content, bytes)
        or not content
        or len(content) > settings.CAMPAIGN_ARTIFACT_MAX_BYTES
    ):
        raise ModelChangeRejected("INVALID_INPUT", "starting artifact is invalid")
    return filename, media_type, content


def _episode_payload(
    *,
    episode_id: uuid.UUID,
    job: ResearchJob,
    campaign: object,
    objective: str,
    named_use: str,
    cutoff: date,
    starting_artifact: ArtifactVersion,
) -> dict[str, object]:
    return {
        "id": str(episode_id),
        "job": str(job.pk),
        "campaign": str(campaign.pk),
        "objective": objective,
        "named_use": named_use,
        "cutoff": cutoff.isoformat(),
        "starting_artifact": str(starting_artifact.pk),
        "starting_artifact_sha256": starting_artifact.digest,
        "input_revision": 1,
    }


class JobService:
    @staticmethod
    @transaction.atomic
    def begin_or_resume(
        owner: object,
        company_ref: str,
        objective: str,
        named_use: str,
        cutoff: date,
        starting_artifact: object,
    ) -> tuple[ResearchJob, ModelChangeEpisode]:
        _feature_enabled()
        filename, media_type, content = _artifact_input(starting_artifact)
        digest = sha256(content).hexdigest()
        existing = (
            ModelChangeEpisode.objects.select_related(
                "job", "campaign", "starting_artifact"
            )
            .filter(
                job__owner=owner,
                job__company_ref=company_ref,
                objective=objective,
                named_use=named_use,
                cutoff=cutoff,
                starting_artifact__digest=digest,
            )
            .first()
        )
        if existing is not None:
            if bytes(existing.starting_artifact.content) != content:
                raise ModelChangeRejected("DIGEST_COLLISION", "artifact custody is invalid")
            return existing.job, existing
        campaign = campaign_services.create_campaign(
            director=owner,
            title=f"{company_ref} model change",
            issuer_or_security=company_ref,
            equities_decision_use=named_use,
            evidence_cutoff=cutoff,
            question=objective,
        )
        artifact = ArtifactVersion.objects.create(
            campaign=campaign,
            role=ArtifactVersion.Role.STARTING_ARTIFACT,
            filename=filename,
            media_type=media_type,
            content=content,
            digest=digest,
        )
        job = ResearchJob.objects.create(owner=owner, company_ref=company_ref)
        episode_id = uuid.uuid4()
        payload = _episode_payload(
            episode_id=episode_id,
            job=job,
            campaign=campaign,
            objective=objective,
            named_use=named_use,
            cutoff=cutoff,
            starting_artifact=artifact,
        )
        episode = _create(
            ModelChangeEpisode,
            {
                "id": episode_id,
                "job": job,
                "campaign": campaign,
                "objective": objective,
                "named_use": named_use,
                "cutoff": cutoff,
                "starting_artifact": artifact,
                "input_revision": 1,
            },
            payload,
        )
        return job, episode


def _manifest_payload(
    manifest_id: uuid.UUID,
    episode: ModelChangeEpisode,
    artifact: ArtifactVersion,
    observed: Mapping[str, object],
) -> dict[str, object]:
    return {
        "id": str(manifest_id),
        "episode": str(episode.pk),
        "artifact": str(artifact.pk),
        "artifact_sha256": artifact.digest,
        "adapter_profile": observed["adapter_profile"],
        "adapter_version": observed["adapter_version"],
        "target_ref": observed["target_ref"],
        "target_address": observed["target_address"],
        "target_value": str(observed["target_value"]),
        "target_unit": observed["target_unit"],
        "allowed_operation": observed["allowed_operation"],
        "dependency_closure": observed["dependency_closure"],
        "formula_bindings": observed["formula_bindings"],
        "inspection_digest": observed["inspection_digest"],
        "support_status": ArtifactManifestVersion.Support.SUPPORTED,
        "warnings": observed["warnings"],
    }


def _object_payload(
    object_id: uuid.UUID,
    episode: ModelChangeEpisode,
    *,
    parent: ConceptualObjectVersion | None,
    manifest: ArtifactManifestVersion | None,
    binding_status: str,
    economic_meaning: dict[str, object],
    method_policy: dict[str, object],
    claim_ceiling: str,
) -> dict[str, object]:
    return {
        "id": str(object_id),
        "episode": str(episode.pk),
        "parent": str(parent.pk) if parent else None,
        "manifest": str(manifest.pk) if manifest else None,
        "manifest_sha256": manifest.digest if manifest else None,
        "binding_status": binding_status,
        "economic_meaning": economic_meaning,
        "method_policy": method_policy,
        "claim_ceiling": claim_ceiling,
    }


class ObjectService:
    @staticmethod
    @transaction.atomic
    def inspect(
        episode: ModelChangeEpisode,
        artifact: ArtifactVersion,
        adapter_profile: Mapping[str, object],
    ) -> tuple[ArtifactManifestVersion, ConceptualObjectVersion]:
        _feature_enabled()
        if artifact.pk != episode.starting_artifact_id:
            raise ModelChangeRejected("WRONG_ARTIFACT", "artifact is outside the episode")
        observed = adapter.inspect(bytes(artifact.content), adapter_profile)
        manifest_id = uuid.uuid4()
        manifest = _create(
            ArtifactManifestVersion,
            {
                "id": manifest_id,
                "episode": episode,
                "artifact": artifact,
                "adapter_profile": observed["adapter_profile"],
                "adapter_version": observed["adapter_version"],
                "target_ref": observed["target_ref"],
                "target_address": observed["target_address"],
                "target_value": observed["target_value"],
                "target_unit": observed["target_unit"],
                "allowed_operation": observed["allowed_operation"],
                "dependency_closure": observed["dependency_closure"],
                "formula_bindings": observed["formula_bindings"],
                "inspection_digest": observed["inspection_digest"],
                "support_status": ArtifactManifestVersion.Support.SUPPORTED,
                "warnings": observed["warnings"],
            },
            _manifest_payload(manifest_id, episode, artifact, observed),
        )
        object_id = uuid.uuid4()
        economic_meaning = {
            "target": manifest.target_ref,
            "description": "FY2025 revenue in USD millions",
            "period": "FY2025",
            "unit": manifest.target_unit,
        }
        method_policy = {
            "method": "reported_value",
            "source_rule": "filed_annual_report_for_annual_target",
        }
        claim_ceiling = "Synthetic candidate for review; no reliance permitted."
        conceptual = _create(
            ConceptualObjectVersion,
            {
                "id": object_id,
                "episode": episode,
                "manifest": manifest,
                "binding_status": ConceptualObjectVersion.BindingStatus.PROPOSED,
                "economic_meaning": economic_meaning,
                "method_policy": method_policy,
                "claim_ceiling": claim_ceiling,
            },
            _object_payload(
                object_id,
                episode,
                parent=None,
                manifest=manifest,
                binding_status=ConceptualObjectVersion.BindingStatus.PROPOSED,
                economic_meaning=economic_meaning,
                method_policy=method_policy,
                claim_ceiling=claim_ceiling,
            ),
        )
        return manifest, conceptual

    @staticmethod
    @transaction.atomic
    def disposition(
        actor: object,
        object_version: ConceptualObjectVersion,
        action: str,
        bounded_payload: Mapping[str, object],
    ) -> ObjectDisposition | tuple[Amendment, ConceptualObjectVersion]:
        _owned(object_version.episode, actor)
        if _invalidated(InvalidationEvent.DescendantType.OBJECT, object_version.pk):
            raise ModelChangeRejected("STALE_OBJECT", "object meaning is historical")
        payload = dict(bounded_payload)
        if action in {
            ObjectDisposition.Action.CONFIRM_MEANING,
            ObjectDisposition.Action.AUTHORIZE_METHOD,
        }:
            disposition_id = uuid.uuid4()
            identity = {
                "id": str(disposition_id),
                "object_version": str(object_version.pk),
                "object_sha256": object_version.digest,
                "actor": actor.pk,
                "action": action,
                "bounded_payload": payload,
            }
            return _create(
                ObjectDisposition,
                {
                    "id": disposition_id,
                    "object_version": object_version,
                    "actor": actor,
                    "action": action,
                    "bounded_payload": payload,
                },
                identity,
            )
        if action != ObjectDisposition.Action.AMEND_MEANING:
            raise ModelChangeRejected("INVALID_ACTION", "object action is unavailable")
        amendment, replacement, _ = InvalidationService.amend(
            actor, object_version, payload
        )
        return amendment, replacement


class EvidenceService:
    @staticmethod
    @transaction.atomic
    def capture(
        document_bytes: bytes,
        identity: Mapping[str, object],
        access_context: Mapping[str, object],
    ) -> SourceDocumentVersion:
        _feature_enabled()
        required = {"episode_id", "filename", "document_class", "filing_date", "issuer"}
        if set(identity) != required or not isinstance(document_bytes, bytes) or not document_bytes:
            raise ModelChangeRejected("INVALID_CAPTURE", "captured document is malformed")
        try:
            episode = ModelChangeEpisode.objects.get(pk=identity["episode_id"])
        except (ModelChangeEpisode.DoesNotExist, ValueError) as exc:
            raise ModelChangeRejected("UNKNOWN_EPISODE", "episode is unavailable") from exc
        filename = identity["filename"]
        if not isinstance(filename, str) or Path(filename).name != filename:
            raise ModelChangeRejected("INVALID_CAPTURE", "captured filename is unsafe")
        artifact = ArtifactVersion.objects.create(
            campaign=episode.campaign,
            role=ArtifactVersion.Role.SOURCE,
            filename=filename,
            media_type="text/plain",
            content=document_bytes,
            digest=sha256(document_bytes).hexdigest(),
        )
        document_id = uuid.uuid4()
        public_identity = {key: value for key, value in identity.items() if key != "episode_id"}
        payload = {
            "id": str(document_id),
            "episode": str(episode.pk),
            "artifact": str(artifact.pk),
            "artifact_sha256": artifact.digest,
            "document_class": identity["document_class"],
            "identity": public_identity,
            "access_context": dict(access_context),
        }
        return _create(
            SourceDocumentVersion,
            {
                "id": document_id,
                "episode": episode,
                "artifact": artifact,
                "document_class": identity["document_class"],
                "identity": public_identity,
                "access_context": dict(access_context),
            },
            payload,
        )

    @staticmethod
    def assert_value(
        document_version: SourceDocumentVersion,
        locator: str,
        value: object,
        dimensions: Mapping[str, object],
    ) -> SourceAssertion:
        assertion_id = uuid.uuid4()
        unit = str(dimensions.get("unit", ""))
        bounded_dimensions = dict(dimensions)
        payload = {
            "id": str(assertion_id),
            "document_version": str(document_version.pk),
            "document_sha256": document_version.digest,
            "locator": locator,
            "value": str(value),
            "unit": unit,
            "dimensions": bounded_dimensions,
        }
        return _create(
            SourceAssertion,
            {
                "id": assertion_id,
                "document_version": document_version,
                "locator": locator,
                "value": value,
                "unit": unit,
                "dimensions": bounded_dimensions,
            },
            payload,
        )

    assert_ = assert_value


def current_closure(
    episode: ModelChangeEpisode,
    current_object: ConceptualObjectVersion,
    manifest: ArtifactManifestVersion,
    assertions: list[SourceAssertion],
) -> str:
    dispositions = list(
        ObjectDisposition.objects.filter(object_version=current_object)
        .order_by("created_at", "pk")
        .values_list("digest", flat=True)
    )
    return canonical_digest(
        {
            "episode": episode.digest,
            "input_revision": episode.input_revision,
            "object": current_object.digest,
            "manifest": manifest.digest,
            "assertions": sorted(item.digest for item in assertions),
            "human_authorities": dispositions,
        }
    )


def canonical_model_change_packet(
    *,
    episode: ModelChangeEpisode,
    proposal: Proposal,
    order_id: uuid.UUID,
    logical_role_id: uuid.UUID,
    current_object: ConceptualObjectVersion,
    manifest: ArtifactManifestVersion,
    assertions: list[SourceAssertion],
) -> dict[str, object]:
    artifacts = [episode.starting_artifact] + [
        item.document_version.artifact for item in assertions
    ]
    by_id = {str(item.pk): item for item in artifacts}
    input_files = []
    for artifact_id in sorted(by_id):
        item = by_id[artifact_id]
        suffix = Path(item.filename).suffix or ".bin"
        input_files.append(
            {
                "id": str(item.pk),
                "role": item.role,
                "filename": item.filename,
                "media_type": item.media_type,
                "sha256": item.digest,
                "materialized_path": str(
                    Path(episode.campaign.artifact_root)
                    / "dispatches"
                    / f"{order_id}.inputs"
                    / f"{item.pk}-{item.digest}{suffix}"
                ),
            }
        )
    closure = current_closure(episode, current_object, manifest, assertions)
    return {
        "schema_version": "research-work-order/v1",
        "campaign_id": str(episode.campaign_id),
        "research_case_id": str(episode.campaign_id),
        "work_order_id": str(order_id),
        "logical_role_id": str(logical_role_id),
        "proposal_id": str(proposal.pk),
        "proposal_digest": proposal.digest,
        "protocol": "model_change_v0",
        "decision_use": episode.named_use,
        "evidence_cutoff": episode.cutoff.isoformat(),
        "task": proposal.task,
        "contract": proposal.contract,
        "output_contract": campaign_services._output_contract(
            episode.campaign, order_id, "model_change_v0"
        ),
        "required_read_policy": (
            "Read the exact protocol and captured inputs; fail if any digest differs."
        ),
        "required_reads": campaign_services._required_reads(proposal),
        "inputs": [],
        "research_state_input": {"basis": WorkOrder.StateBasis.COMMISSION},
        "supporting_research_states": [],
        "network_policy": NETWORK_POLICY,
        "episode": {
            "id": str(episode.pk),
            "sha256": episode.digest,
            "input_revision": episode.input_revision,
        },
        "conceptual_object": {
            "id": str(current_object.pk),
            "sha256": current_object.digest,
            "economic_meaning": current_object.economic_meaning,
            "method_policy": current_object.method_policy,
            "claim_ceiling": current_object.claim_ceiling,
        },
        "starting_artifact": {
            "id": str(episode.starting_artifact_id),
            "sha256": episode.starting_artifact.digest,
        },
        "manifest": {
            "id": str(manifest.pk),
            "sha256": manifest.digest,
            "target_ref": manifest.target_ref,
            "target_address": manifest.target_address,
            "target_value": str(manifest.target_value),
            "target_unit": manifest.target_unit,
            "allowed_operation": manifest.allowed_operation,
            "dependency_closure": manifest.dependency_closure,
            "formula_bindings": manifest.formula_bindings,
        },
        "source_assertions": [
            {
                "id": str(item.pk),
                "sha256": item.digest,
                "document_id": str(item.document_version_id),
                "document_sha256": item.document_version.digest,
                "document_class": item.document_version.document_class,
                "locator": item.locator,
                "value": str(item.value),
                "unit": item.unit,
                "dimensions": item.dimensions,
                "materialized_path": next(
                    row["materialized_path"]
                    for row in input_files
                    if row["id"] == str(item.document_version.artifact_id)
                ),
            }
            for item in sorted(assertions, key=lambda item: str(item.pk))
        ],
        "closure_digest": closure,
        "protocol_version": PROTOCOL_VERSION,
        "job_inputs": [
            {"id": item["id"], "sha256": item["sha256"]} for item in input_files
        ],
        "job_input_files": input_files,
        "outcome_authority": "provisional_only",
    }


def canonical_model_change_packet_for_order(order: WorkOrder) -> dict[str, object]:
    """Re-derive an approved packet exclusively from canonical database facts."""
    try:
        episode = ModelChangeEpisode.objects.select_related(
            "campaign", "job__owner", "starting_artifact"
        ).get(pk=order.packet["episode"]["id"], campaign=order.campaign)
        conceptual = ConceptualObjectVersion.objects.get(
            pk=order.packet["conceptual_object"]["id"], episode=episode
        )
        manifest = ArtifactManifestVersion.objects.get(
            pk=order.packet["manifest"]["id"], episode=episode
        )
        assertion_ids = [row["id"] for row in order.packet["source_assertions"]]
        assertions = list(
            SourceAssertion.objects.select_related(
                "document_version__artifact"
            ).filter(pk__in=assertion_ids, document_version__episode=episode)
        )
    except (KeyError, TypeError, ValueError, ModelChangeEpisode.DoesNotExist) as exc:
        raise ModelChangeRejected("STALE_PACKET", "model change packet is unavailable") from exc
    if len(assertions) != len(assertion_ids):
        raise ModelChangeRejected("STALE_PACKET", "model change packet is unavailable")
    return canonical_model_change_packet(
        episode=episode,
        proposal=order.proposal,
        order_id=order.pk,
        logical_role_id=order.logical_role_id,
        current_object=conceptual,
        manifest=manifest,
        assertions=assertions,
    )


class WorkCompiler:
    @staticmethod
    @transaction.atomic
    def compile(
        episode: ModelChangeEpisode,
        current_object: ConceptualObjectVersion,
        current_authority: list[ObjectDisposition],
        manifest: ArtifactManifestVersion,
        captured_assertions: list[SourceAssertion],
        protocol_version: str,
    ) -> WorkOrder:
        _feature_enabled()
        if protocol_version != PROTOCOL_VERSION:
            raise ModelChangeRejected("STALE_PROTOCOL", "protocol version is unavailable")
        actions = {item.action for item in current_authority}
        if actions != {
            ObjectDisposition.Action.CONFIRM_MEANING,
            ObjectDisposition.Action.AUTHORIZE_METHOD,
        } or any(item.object_version_id != current_object.pk for item in current_authority):
            raise ModelChangeRejected(
                "MISSING_AUTHORITY", "meaning and method require separate confirmation"
            )
        if (
            current_object.episode_id != episode.pk
            or manifest.episode_id != episode.pk
            or len(captured_assertions) != 2
            or any(item.document_version.episode_id != episode.pk for item in captured_assertions)
            or _invalidated(InvalidationEvent.DescendantType.OBJECT, current_object.pk)
        ):
            raise ModelChangeRejected("CROSS_SCOPE", "work inputs cross episode custody")
        contract = {
            "workbenches": [],
            "reasoning_operators": [],
            "network_policy": NETWORK_POLICY,
            "protocol_version": PROTOCOL_VERSION,
            "authority": "provisional_only",
        }
        proposal = campaign_services.record_proposal(
            campaign=episode.campaign,
            author=Proposal.Author.DIRECTOR,
            author_user=episode.job.owner,
            protocol="model_change_v0",
            title="Propose the reported value change",
            task=(
                "Using only the captured documents, propose one typed numeric change "
                "to the inspected target or return a bounded refusal."
            ),
            contract=contract,
        )
        campaign_services._disposition(
            proposal,
            user=episode.job.owner,
            kind=ProposalDisposition.Kind.APPROVED,
        )
        order_id, logical_role_id = uuid.uuid4(), uuid.uuid4()
        packet = canonical_model_change_packet(
            episode=episode,
            proposal=proposal,
            order_id=order_id,
            logical_role_id=logical_role_id,
            current_object=current_object,
            manifest=manifest,
            assertions=captured_assertions,
        )
        identity = {
            "id": str(order_id),
            "campaign": str(episode.campaign_id),
            "proposal": str(proposal.pk),
            "logical_role_id": str(logical_role_id),
            "protocol": "model_change_v0",
            "proposal_digest": proposal.digest,
            "input_artifact_ids": [],
            "state_basis": WorkOrder.StateBasis.COMMISSION,
            "input_state": None,
            "packet": packet,
        }
        return _create(
            WorkOrder,
            {
                "id": order_id,
                "campaign": episode.campaign,
                "proposal": proposal,
                "logical_role_id": logical_role_id,
                "protocol": "model_change_v0",
                "proposal_digest": proposal.digest,
                "input_artifact_ids": [],
                "state_basis": WorkOrder.StateBasis.COMMISSION,
                "packet": packet,
            },
            identity,
        )


def _load_worker_value(worker_output: bytes | Mapping[str, object]) -> dict[str, object]:
    try:
        value = json.loads(worker_output) if isinstance(worker_output, bytes) else dict(worker_output)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ModelChangeRejected("MALFORMED_OUTPUT", "worker output is malformed") from exc
    if not isinstance(value, dict):
        raise ModelChangeRejected("MALFORMED_OUTPUT", "worker output is malformed")
    return value


class ProposalParser:
    @staticmethod
    @transaction.atomic
    def parse(
        worker_output: bytes | Mapping[str, object], exact_packet: Mapping[str, object]
    ) -> ModelChangeProposal | dict[str, object]:
        value = _load_worker_value(worker_output)
        if value.get("schema") == "model-change-refusal/v0":
            if set(value) != {"schema", "episode_id", "reason"} or value.get(
                "episode_id"
            ) != exact_packet["episode"]["id"]:
                raise ModelChangeRejected("MALFORMED_REFUSAL", "worker refusal is malformed")
            return value
        required = {
            "schema",
            "episode_id",
            "episode_digest",
            "input_revision",
            "conceptual_object_id",
            "conceptual_object_digest",
            "starting_artifact_id",
            "starting_artifact_digest",
            "source_assertion_id",
            "operation",
            "claim_ceiling",
        }
        if set(value) != required or value.get("schema") != "model-change-proposal/v0":
            raise ModelChangeRejected("MALFORMED_OUTPUT", "worker proposal is malformed")
        bindings = {
            "episode_id": exact_packet["episode"]["id"],
            "episode_digest": exact_packet["episode"]["sha256"],
            "input_revision": exact_packet["episode"]["input_revision"],
            "conceptual_object_id": exact_packet["conceptual_object"]["id"],
            "conceptual_object_digest": exact_packet["conceptual_object"]["sha256"],
            "starting_artifact_id": exact_packet["starting_artifact"]["id"],
            "starting_artifact_digest": exact_packet["starting_artifact"]["sha256"],
            "claim_ceiling": exact_packet["conceptual_object"]["claim_ceiling"],
        }
        if any(value.get(key) != expected for key, expected in bindings.items()):
            raise ModelChangeRejected("INVENTED_OR_STALE_IDENTITY", "proposal identity is unavailable")
        assertion_rows = {row["id"]: row for row in exact_packet["source_assertions"]}
        assertion_row = assertion_rows.get(value.get("source_assertion_id"))
        if assertion_row is None:
            raise ModelChangeRejected("UNKNOWN_SOURCE_ASSERTION", "source assertion is unavailable")
        operation = value.get("operation")
        if (
            not isinstance(operation, dict)
            or set(operation) != {"kind", "target_ref", "value", "unit"}
            or operation.get("kind") != exact_packet["manifest"]["allowed_operation"]
            or operation.get("target_ref") != exact_packet["manifest"]["target_ref"]
            or str(operation.get("value")) != assertion_row["value"]
            or operation.get("unit") != assertion_row["unit"]
        ):
            raise ModelChangeRejected("INVALID_OPERATION", "proposal operation is unavailable")
        order = WorkOrder.objects.get(pk=exact_packet["work_order_id"])
        episode = ModelChangeEpisode.objects.get(pk=bindings["episode_id"])
        conceptual = ConceptualObjectVersion.objects.get(pk=bindings["conceptual_object_id"])
        manifest = ArtifactManifestVersion.objects.get(pk=exact_packet["manifest"]["id"])
        assertion = SourceAssertion.objects.get(pk=value["source_assertion_id"])
        proposal_id = uuid.uuid4()
        payload = {
            "id": str(proposal_id),
            "episode": str(episode.pk),
            "parent": None,
            "work_order": str(order.pk),
            "proposer_kind": ModelChangeProposal.ProposerKind.MODEL,
            "conceptual_object": str(conceptual.pk),
            "starting_artifact": str(episode.starting_artifact_id),
            "source_assertion": str(assertion.pk),
            "manifest": str(manifest.pk),
            "input_revision": episode.input_revision,
            "operation": operation,
            "protocol_version": PROTOCOL_VERSION,
            "claim_ceiling": value["claim_ceiling"],
            "closure_digest": exact_packet["closure_digest"],
        }
        return _create(
            ModelChangeProposal,
            {
                "id": proposal_id,
                "episode": episode,
                "work_order": order,
                "proposer_kind": ModelChangeProposal.ProposerKind.MODEL,
                "conceptual_object": conceptual,
                "starting_artifact": episode.starting_artifact,
                "source_assertion": assertion,
                "manifest": manifest,
                "input_revision": episode.input_revision,
                "operation": operation,
                "protocol_version": PROTOCOL_VERSION,
                "claim_ceiling": value["claim_ceiling"],
                "closure_digest": exact_packet["closure_digest"],
            },
            payload,
        )


class RunService:
    @staticmethod
    def run(
        actor: object, order: WorkOrder
    ) -> tuple[ModelChangeProposal | dict[str, object], AdmissibilityDecision | None]:
        """Run one closed, synchronous NTM/Codex unit and admit only after custody."""
        _owned(order.campaign.model_change_episode, actor)
        if order.protocol != "model_change_v0":
            raise ModelChangeRejected("WRONG_PROTOCOL", "work order is unavailable")
        try:
            campaign_services.launch_role(order, actor)
            ready = False
            for attempt in range(settings.MODEL_CHANGE_RUNTIME_READY_SECONDS + 1):
                campaign_services.refresh_status(order, actor)
                try:
                    campaign_services._target_index(order)
                except campaign_services.CampaignRejected:
                    time.sleep(1)
                    continue
                if attempt < settings.MODEL_CHANGE_RUNTIME_READY_SECONDS:
                    time.sleep(1)
                    continue
                ready = True
            if not ready:
                raise ModelChangeRejected(
                    "RUNTIME_NOT_READY", "the model change worker did not become ready"
                )
            campaign_services.send_dispatch(order, actor)
            completed = False
            expected_outputs = {
                MODEL_OUTPUT,
                ACKNOWLEDGEMENT_OUTPUT,
                order.packet["output_contract"]["attestation_path"],
            }
            for _ in range(settings.MODEL_CHANGE_RUNTIME_POLL_LIMIT):
                campaign_services.refresh_status(order, actor)
                output_root = campaign_services._output_root(order)
                observed_outputs = (
                    {item.name for item in output_root.iterdir()}
                    if output_root.is_dir() and not output_root.is_symlink()
                    else set()
                )
                if (
                    campaign_services._completion_observed(order)
                    and observed_outputs == expected_outputs
                ):
                    completed = True
                    break
                time.sleep(1)
            if not completed:
                raise ModelChangeRejected(
                    "RUNTIME_IN_PROGRESS",
                    "work is still running; its recorded state is preserved",
                )
            campaign_services.collect_artifacts(order.campaign, actor)
        except campaign_services.CampaignRejected as exc:
            raise ModelChangeRejected("RUNTIME_FAILED", str(exc)) from exc
        output = order.artifacts.get(relative_path=MODEL_OUTPUT)
        result = ProposalParser.parse(bytes(output.content), order.packet)
        if isinstance(result, dict):
            return result, None
        return result, AdmissibilityGate.evaluate(
            result, str(order.packet["closure_digest"])
        )


def _invalidated(kind: str, identity: uuid.UUID) -> bool:
    return InvalidationEvent.objects.filter(
        descendant_type=kind, descendant_id=identity
    ).exists()


class AdmissibilityGate:
    @staticmethod
    @transaction.atomic
    def evaluate(
        proposal: ModelChangeProposal, current_closure_digest: str
    ) -> AdmissibilityDecision:
        if proposal.closure_digest != current_closure_digest or _invalidated(
            InvalidationEvent.DescendantType.PROPOSAL, proposal.pk
        ):
            outcome, reason = (
                AdmissibilityDecision.Outcome.BLOCK,
                "BLOCK_STALE_CLOSURE",
            )
        else:
            document_class = proposal.source_assertion.document_version.document_class
            target = proposal.operation.get("target_ref")
            expected = {
                "kind": proposal.manifest.allowed_operation,
                "target_ref": proposal.manifest.target_ref,
                "value": str(proposal.source_assertion.value),
                "unit": proposal.source_assertion.unit,
            }
            observed = {**proposal.operation, "value": str(proposal.operation.get("value"))}
            if observed != expected:
                outcome, reason = AdmissibilityDecision.Outcome.BLOCK, "BLOCK_INVALID_OPERATION"
            elif (
                target == ANNUAL_TARGET
                and document_class == SourceDocumentVersion.DocumentClass.EARNINGS_RELEASE_8K
            ):
                outcome, reason = (
                    AdmissibilityDecision.Outcome.BLOCK,
                    "BLOCK_WRONG_DOCUMENT_CLASS",
                )
            elif (
                target == ANNUAL_TARGET
                and document_class == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
            ) or (
                target == PRELIMINARY_TARGET
                and document_class == SourceDocumentVersion.DocumentClass.EARNINGS_RELEASE_8K
            ):
                outcome, reason = AdmissibilityDecision.Outcome.PASS, "PASS_EXACT_CLOSURE"
            else:
                outcome, reason = AdmissibilityDecision.Outcome.UNSUPPORTED, "UNSUPPORTED_TARGET_SOURCE_PAIR"
        decision_id = uuid.uuid4()
        payload = {
            "id": str(decision_id),
            "proposal": str(proposal.pk),
            "proposal_sha256": proposal.digest,
            "validator_version": VALIDATOR_VERSION,
            "outcome": outcome,
            "reason_code": reason,
            "closure_digest": proposal.closure_digest,
        }
        return _create(
            AdmissibilityDecision,
            {
                "id": decision_id,
                "proposal": proposal,
                "validator_version": VALIDATOR_VERSION,
                "outcome": outcome,
                "reason_code": reason,
                "closure_digest": proposal.closure_digest,
            },
            payload,
        )


def _proposal_payload(
    proposal_id: uuid.UUID,
    parent: ModelChangeProposal,
    assertion: SourceAssertion,
    closure_digest: str,
) -> tuple[dict[str, object], dict[str, object]]:
    operation = {
        "kind": parent.manifest.allowed_operation,
        "target_ref": parent.manifest.target_ref,
        "value": str(assertion.value),
        "unit": assertion.unit,
    }
    payload = {
        "id": str(proposal_id),
        "episode": str(parent.episode_id),
        "parent": str(parent.pk),
        "work_order": None,
        "proposer_kind": ModelChangeProposal.ProposerKind.HOST_DERIVED,
        "conceptual_object": str(parent.conceptual_object_id),
        "starting_artifact": str(parent.starting_artifact_id),
        "source_assertion": str(assertion.pk),
        "manifest": str(parent.manifest_id),
        "input_revision": parent.input_revision,
        "operation": operation,
        "protocol_version": parent.protocol_version,
        "claim_ceiling": parent.claim_ceiling,
        "closure_digest": closure_digest,
    }
    return operation, payload


class InvalidationService:
    @staticmethod
    @transaction.atomic
    def repair_wrong_source(
        actor: object,
        blocked: AdmissibilityDecision,
        annual_assertion: SourceAssertion,
    ) -> tuple[Amendment, ModelChangeProposal, AdmissibilityDecision]:
        episode = blocked.proposal.episode
        _owned(episode, actor)
        if (
            blocked.reason_code != "BLOCK_WRONG_DOCUMENT_CLASS"
            or annual_assertion.document_version.episode_id != episode.pk
            or annual_assertion.document_version.document_class
            != SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        ):
            raise ModelChangeRejected("INVALID_REPAIR", "filed-report repair is unavailable")
        replacement_closure = canonical_digest(
            {
                "prior_closure": blocked.proposal.closure_digest,
                "actor": actor.pk,
                "action": Amendment.Action.USE_FILED_ANNUAL_REPORT,
                "source_assertion": annual_assertion.digest,
            }
        )
        proposal_id = uuid.uuid4()
        operation, proposal_payload = _proposal_payload(
            proposal_id,
            blocked.proposal,
            annual_assertion,
            replacement_closure,
        )
        replacement = _create(
            ModelChangeProposal,
            {
                "id": proposal_id,
                "episode": episode,
                "parent": blocked.proposal,
                "proposer_kind": ModelChangeProposal.ProposerKind.HOST_DERIVED,
                "conceptual_object": blocked.proposal.conceptual_object,
                "starting_artifact": blocked.proposal.starting_artifact,
                "source_assertion": annual_assertion,
                "manifest": blocked.proposal.manifest,
                "input_revision": blocked.proposal.input_revision,
                "operation": operation,
                "protocol_version": blocked.proposal.protocol_version,
                "claim_ceiling": blocked.proposal.claim_ceiling,
                "closure_digest": replacement_closure,
            },
            proposal_payload,
        )
        amendment_id = uuid.uuid4()
        bounded = {
            "action_label": "Create a candidate using the filed annual report",
            "from_source_assertion": str(blocked.proposal.source_assertion_id),
            "to_source_assertion": str(annual_assertion.pk),
        }
        amendment_payload = {
            "id": str(amendment_id),
            "episode": str(episode.pk),
            "actor": actor.pk,
            "object_version": None,
            "blocked_decision": str(blocked.pk),
            "action": Amendment.Action.USE_FILED_ANNUAL_REPORT,
            "bounded_change": bounded,
            "rationale": "Use the captured filed annual report for the annual target.",
            "replacement_object": None,
            "replacement_proposal": str(replacement.pk),
        }
        amendment = _create(
            Amendment,
            {
                "id": amendment_id,
                "episode": episode,
                "actor": actor,
                "blocked_decision": blocked,
                "action": Amendment.Action.USE_FILED_ANNUAL_REPORT,
                "bounded_change": bounded,
                "rationale": amendment_payload["rationale"],
                "replacement_proposal": replacement,
            },
            amendment_payload,
        )
        for kind, item in (
            (InvalidationEvent.DescendantType.PROPOSAL, blocked.proposal),
            (InvalidationEvent.DescendantType.DECISION, blocked),
        ):
            event_id = uuid.uuid4()
            event_payload = {
                "id": str(event_id),
                "amendment": str(amendment.pk),
                "descendant_type": kind,
                "descendant_id": str(item.pk),
                "descendant_digest": item.digest,
                "reason": "captured source selection was replaced",
                "closure_digest": replacement_closure,
            }
            _create(
                InvalidationEvent,
                {
                    "id": event_id,
                    "amendment": amendment,
                    "descendant_type": kind,
                    "descendant_id": item.pk,
                    "descendant_digest": item.digest,
                    "reason": event_payload["reason"],
                    "closure_digest": replacement_closure,
                },
                event_payload,
            )
        passed = AdmissibilityGate.evaluate(replacement, replacement.closure_digest)
        return amendment, replacement, passed

    @staticmethod
    @transaction.atomic
    def amend(
        actor: object,
        exact_ancestor: ConceptualObjectVersion,
        bounded_change: Mapping[str, object],
    ) -> tuple[Amendment, ConceptualObjectVersion, list[InvalidationEvent]]:
        episode = exact_ancestor.episode
        _owned(episode, actor)
        meaning = {**exact_ancestor.economic_meaning, **dict(bounded_change)}
        object_id = uuid.uuid4()
        replacement = _create(
            ConceptualObjectVersion,
            {
                "id": object_id,
                "episode": episode,
                "parent": exact_ancestor,
                "manifest": exact_ancestor.manifest,
                "binding_status": ConceptualObjectVersion.BindingStatus.PROPOSED,
                "economic_meaning": meaning,
                "method_policy": exact_ancestor.method_policy,
                "claim_ceiling": exact_ancestor.claim_ceiling,
            },
            _object_payload(
                object_id,
                episode,
                parent=exact_ancestor,
                manifest=exact_ancestor.manifest,
                binding_status=ConceptualObjectVersion.BindingStatus.PROPOSED,
                economic_meaning=meaning,
                method_policy=exact_ancestor.method_policy,
                claim_ceiling=exact_ancestor.claim_ceiling,
            ),
        )
        amendment_id = uuid.uuid4()
        amendment_payload = {
            "id": str(amendment_id),
            "episode": str(episode.pk),
            "actor": actor.pk,
            "object_version": str(exact_ancestor.pk),
            "blocked_decision": None,
            "action": Amendment.Action.AMEND_MEANING,
            "bounded_change": dict(bounded_change),
            "rationale": "Attributed change to the bounded object meaning.",
            "replacement_object": str(replacement.pk),
            "replacement_proposal": None,
        }
        amendment = _create(
            Amendment,
            {
                "id": amendment_id,
                "episode": episode,
                "actor": actor,
                "object_version": exact_ancestor,
                "action": Amendment.Action.AMEND_MEANING,
                "bounded_change": dict(bounded_change),
                "rationale": amendment_payload["rationale"],
                "replacement_object": replacement,
            },
            amendment_payload,
        )
        descendants: list[tuple[str, object]] = [
            (InvalidationEvent.DescendantType.OBJECT, exact_ancestor)
        ]
        for proposal in episode.model_change_proposals.filter(conceptual_object=exact_ancestor):
            descendants.append((InvalidationEvent.DescendantType.PROPOSAL, proposal))
            decision = getattr(proposal, "admissibility_decision", None)
            if decision:
                descendants.append((InvalidationEvent.DescendantType.DECISION, decision))
                for candidate in decision.candidate_artifacts.all():
                    descendants.append((InvalidationEvent.DescendantType.CANDIDATE, candidate))
                    receipt = getattr(candidate, "calculation_receipt", None)
                    if receipt:
                        descendants.append((InvalidationEvent.DescendantType.CALCULATION, receipt))
                        descendants.extend(
                            (InvalidationEvent.DescendantType.DISPOSITION, item)
                            for item in receipt.artifact_dispositions.all()
                        )
        events = []
        for kind, item in descendants:
            event_id = uuid.uuid4()
            digest = getattr(item, "digest")
            payload = {
                "id": str(event_id),
                "amendment": str(amendment.pk),
                "descendant_type": kind,
                "descendant_id": str(item.pk),
                "descendant_digest": digest,
                "reason": "material ancestor amendment",
                "closure_digest": canonical_digest(
                    {"amendment": amendment.digest, "descendant": digest}
                ),
            }
            events.append(
                _create(
                    InvalidationEvent,
                    {
                        "id": event_id,
                        "amendment": amendment,
                        "descendant_type": kind,
                        "descendant_id": item.pk,
                        "descendant_digest": digest,
                        "reason": payload["reason"],
                        "closure_digest": payload["closure_digest"],
                    },
                    payload,
                )
            )
        return amendment, replacement, events


class CandidateService:
    @staticmethod
    @transaction.atomic
    def create(
        pass_decision: AdmissibilityDecision,
        exact_parent: ArtifactVersion,
        adapter_profile: Mapping[str, object],
    ) -> tuple[ArtifactVersion, dict[str, object], CalculationReceipt]:
        proposal = pass_decision.proposal
        if (
            pass_decision.outcome != AdmissibilityDecision.Outcome.PASS
            or exact_parent.pk != proposal.starting_artifact_id
            or _invalidated(InvalidationEvent.DescendantType.PROPOSAL, proposal.pk)
            or _invalidated(InvalidationEvent.DescendantType.DECISION, pass_decision.pk)
        ):
            raise ModelChangeRejected("PASS_REQUIRED", "current exact pass is required")
        patched, operation_receipt = adapter.apply(
            bytes(exact_parent.content),
            [proposal.operation],
            proposal.manifest.digest,
            adapter_profile,
            expected_inspection_digest=proposal.manifest.inspection_digest,
        )
        calculated, engine = adapter.calculate(patched, adapter_profile)
        consequences = adapter.compare(
            bytes(exact_parent.content),
            calculated,
            proposal.manifest.dependency_closure,
            adapter_profile,
        )
        candidate = ArtifactVersion.objects.create(
            campaign=proposal.episode.campaign,
            role=ArtifactVersion.Role.CANDIDATE,
            filename="synthetic-model-change-candidate.xlsx",
            media_type=exact_parent.media_type,
            content=calculated,
            digest=sha256(calculated).hexdigest(),
            parent=exact_parent,
            candidate_from_pass=pass_decision,
        )
        receipt_id = uuid.uuid4()
        receipt_payload = {
            "id": str(receipt_id),
            "episode": str(proposal.episode_id),
            "candidate": str(candidate.pk),
            "candidate_sha256": candidate.digest,
            "pass_decision": str(pass_decision.pk),
            "manifest": str(proposal.manifest_id),
            "adapter_version": adapter.ADAPTER_VERSION,
            "adapter_profile": adapter_profile["profile_id"],
            "engine_identity": engine["engine_identity"],
            "engine_version": engine["engine_version"],
            "timeout_seconds": engine["timeout_seconds"],
            "environment": engine["environment"],
            "operation_receipt": operation_receipt,
            "input_digest": exact_parent.digest,
            "output_digest": candidate.digest,
            "consequences": consequences,
            "warnings": engine["warnings"],
            "formula_errors": engine["formula_errors"],
            "closure_digest": proposal.closure_digest,
        }
        receipt = _create(
            CalculationReceipt,
            {
                "id": receipt_id,
                "episode": proposal.episode,
                "candidate": candidate,
                "pass_decision": pass_decision,
                "manifest": proposal.manifest,
                "adapter_version": adapter.ADAPTER_VERSION,
                "adapter_profile": adapter_profile["profile_id"],
                "engine_identity": engine["engine_identity"],
                "engine_version": engine["engine_version"],
                "timeout_seconds": engine["timeout_seconds"],
                "environment": engine["environment"],
                "operation_receipt": operation_receipt,
                "input_digest": exact_parent.digest,
                "output_digest": candidate.digest,
                "consequences": consequences,
                "warnings": engine["warnings"],
                "formula_errors": engine["formula_errors"],
                "closure_digest": proposal.closure_digest,
            },
            receipt_payload,
        )
        return candidate, operation_receipt, receipt


class DispositionService:
    @staticmethod
    def record(
        actor: object,
        candidate: ArtifactVersion,
        named_use: str,
        kind: str,
        rationale: str = "",
    ) -> ArtifactDisposition:
        receipt = candidate.calculation_receipt
        episode = receipt.episode
        _owned(episode, actor)
        if kind not in ArtifactDisposition.Kind.values:
            raise ModelChangeRejected("INVALID_ACTION", "candidate action is unavailable")
        if _invalidated(InvalidationEvent.DescendantType.CANDIDATE, candidate.pk):
            raise ModelChangeRejected("STALE_CANDIDATE", "candidate is historical")
        disposition_id = uuid.uuid4()
        payload = {
            "id": str(disposition_id),
            "episode": str(episode.pk),
            "candidate": str(candidate.pk),
            "calculation_receipt": str(receipt.pk),
            "actor": actor.pk,
            "named_use": named_use,
            "kind": kind,
            "rationale": rationale,
            "closure_digest": receipt.closure_digest,
        }
        return _create(
            ArtifactDisposition,
            {
                "id": disposition_id,
                "episode": episode,
                "candidate": candidate,
                "calculation_receipt": receipt,
                "actor": actor,
                "named_use": named_use,
                "kind": kind,
                "rationale": rationale,
                "closure_digest": receipt.closure_digest,
            },
            payload,
        )


class CorrectionService:
    @staticmethod
    def seed(
        block: AdmissibilityDecision,
        amendment: Amendment,
        replacement: ModelChangeProposal,
        candidate: ArtifactVersion,
        versions: Mapping[str, str],
    ) -> CorrectionRecord:
        if set(versions) != {"protocol", "adapter_profile"}:
            raise ModelChangeRejected("INVALID_SEED", "correction versions are malformed")
        record_id = uuid.uuid4()
        source_assertions = [
            {"id": str(item.pk), "sha256": item.digest}
            for item in (block.proposal.source_assertion, replacement.source_assertion)
        ]
        payload = {
            "id": str(record_id),
            "episode": str(block.proposal.episode_id),
            "blocked_decision": str(block.pk),
            "amendment": str(amendment.pk),
            "replacement_proposal": str(replacement.pk),
            "source_assertions": source_assertions,
            "candidate": str(candidate.pk),
            "protocol_version": versions["protocol"],
            "adapter_profile_version": versions["adapter_profile"],
            "reason_code": block.reason_code,
        }
        return _create(
            CorrectionRecord,
            {
                "id": record_id,
                "episode": block.proposal.episode,
                "blocked_decision": block,
                "amendment": amendment,
                "replacement_proposal": replacement,
                "source_assertions": source_assertions,
                "candidate": candidate,
                "protocol_version": versions["protocol"],
                "adapter_profile_version": versions["adapter_profile"],
                "reason_code": block.reason_code,
            },
            payload,
        )


class ProjectionService:
    @staticmethod
    def resume(
        owner: object, job_id: uuid.UUID | str, episode_id: uuid.UUID | str
    ) -> dict[str, object]:
        _feature_enabled()
        try:
            episode = ModelChangeEpisode.objects.select_related(
                "job", "campaign", "starting_artifact"
            ).get(pk=episode_id, job_id=job_id, job__owner=owner)
        except (ModelChangeEpisode.DoesNotExist, ValueError) as exc:
            raise ModelChangeRejected("NOT_FOUND", "model change episode is unavailable") from exc
        invalid = {
            (item.descendant_type, item.descendant_id)
            for item in InvalidationEvent.objects.filter(amendment__episode=episode)
        }
        objects = list(episode.conceptual_objects.order_by("created_at", "pk"))
        current_object = next(
            (
                item
                for item in reversed(objects)
                if (InvalidationEvent.DescendantType.OBJECT, item.pk) not in invalid
            ),
            None,
        )
        proposals = list(
            episode.model_change_proposals.select_related(
                "source_assertion__document_version"
            ).order_by("created_at", "pk")
        )
        current_proposal = next(
            (
                item
                for item in reversed(proposals)
                if (InvalidationEvent.DescendantType.PROPOSAL, item.pk) not in invalid
            ),
            None,
        )
        decision = (
            getattr(current_proposal, "admissibility_decision", None)
            if current_proposal
            else None
        )
        if decision and (InvalidationEvent.DescendantType.DECISION, decision.pk) in invalid:
            decision = None
        candidates = list(
            ArtifactVersion.objects.filter(
                campaign=episode.campaign,
                role=ArtifactVersion.Role.CANDIDATE,
                candidate_from_pass__proposal__episode=episode,
            ).order_by("created_at", "pk")
        )
        candidate = next(
            (
                item
                for item in reversed(candidates)
                if (InvalidationEvent.DescendantType.CANDIDATE, item.pk) not in invalid
            ),
            None,
        )
        calculation = getattr(candidate, "calculation_receipt", None) if candidate else None
        if calculation and (
            InvalidationEvent.DescendantType.CALCULATION,
            calculation.pk,
        ) in invalid:
            calculation = None
        disposition = None
        if calculation:
            disposition = next(
                (
                    item
                    for item in reversed(
                        list(calculation.artifact_dispositions.order_by("created_at", "pk"))
                    )
                    if (InvalidationEvent.DescendantType.DISPOSITION, item.pk) not in invalid
                ),
                None,
            )
        return {
            "job": episode.job,
            "episode": episode,
            "manifest": episode.artifact_manifests.order_by("created_at", "pk").last(),
            "current_object": current_object,
            "object_authorities": list(
                ObjectDisposition.objects.filter(object_version=current_object).order_by(
                    "created_at", "pk"
                )
            )
            if current_object
            else [],
            "work_order": episode.campaign.work_orders.filter(
                protocol="model_change_v0"
            ).order_by("created_at", "pk").last(),
            "proposal": current_proposal,
            "decision": decision,
            "candidate": candidate,
            "calculation": calculation,
            "disposition": disposition,
            "history": {
                "objects": objects,
                "proposals": proposals,
                "decisions": list(
                    AdmissibilityDecision.objects.filter(
                        proposal__episode=episode
                    ).order_by("created_at", "pk")
                ),
                "amendments": list(episode.amendments.order_by("created_at", "pk")),
                "invalidations": list(
                    InvalidationEvent.objects.filter(amendment__episode=episode).order_by(
                        "created_at", "pk"
                    )
                ),
                "dispositions": list(
                    episode.artifact_dispositions.order_by("created_at", "pk")
                ),
            },
        }
