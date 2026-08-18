from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Mapping
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction

from product.campaign import services as campaign_services
from product.campaign.models import (
    AdmissibilityDecision,
    Amendment,
    Artifact,
    ArtifactDisposition,
    ArtifactManifestVersion,
    ArtifactVersion,
    CalculationReceipt,
    ConceptualObjectVersion,
    CorrectionRecord,
    InvalidationEvent,
    ModelChangeEpisode,
    ModelChangeOutcome,
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
VALIDATOR_VERSION = "model-change-admissibility/v1"
NETWORK_POLICY = "closed_captured_sources"
ANNUAL_TARGET = "FY25_REVENUE_USDM"
PRELIMINARY_TARGET = "FY2025_PRELIMINARY_EARNINGS_FLASH_REVENUE"
MODEL_OUTPUT = "model-change-output.json"
ACKNOWLEDGEMENT_OUTPUT = "run-acknowledgement.json"


class ModelChangeRejected(Exception):
    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


@dataclass(frozen=True)
class RepairResult:
    amendment: Amendment | None = None
    replacement_proposal: ModelChangeProposal | None = None
    pass_decision: AdmissibilityDecision | None = None
    candidate: ArtifactVersion | None = None
    calculation_receipt: CalculationReceipt | None = None
    outcome: ModelChangeOutcome | None = None
    created_or_existing: str = "created"


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
        _feature_enabled()
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
        _feature_enabled()
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
        _feature_enabled()
        value = _load_worker_value(worker_output)
        if value.get("schema") == "model-change-refusal/v0":
            if set(value) != {"schema", "episode_id", "reason"} or value.get(
                "episode_id"
            ) != exact_packet["episode"]["id"] or not isinstance(
                value.get("reason"), str
            ) or not value["reason"].strip() or len(value["reason"]) > 1000:
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
        if ModelChangeOutcome.objects.filter(work_order=order).exists():
            raise ModelChangeRejected(
                "STALE_WORKER_OUTPUT",
                "the worker output belongs to a completed attempt",
            )
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


class OutcomeService:
    @staticmethod
    def _record(
        *,
        episode: ModelChangeEpisode,
        stage: str,
        reason_code: str,
        public_message: str,
        next_action: str,
        closure_digest: str,
        attempt_key: str,
        protocol_version: str,
        technical_details: Mapping[str, object],
        work_order: WorkOrder | None = None,
        blocked_decision: AdmissibilityDecision | None = None,
    ) -> ModelChangeOutcome:
        _feature_enabled()
        existing = ModelChangeOutcome.objects.filter(
            stage=stage, attempt_key=attempt_key
        ).first()
        if existing is not None:
            return existing
        outcome_id = uuid.uuid4()
        details = dict(technical_details)
        payload = {
            "id": str(outcome_id),
            "episode": str(episode.pk),
            "work_order": str(work_order.pk) if work_order else None,
            "blocked_decision": (
                str(blocked_decision.pk) if blocked_decision else None
            ),
            "stage": stage,
            "reason_code": reason_code,
            "public_message": public_message,
            "next_action": next_action,
            "closure_digest": closure_digest,
            "attempt_key": attempt_key,
            "protocol_version": protocol_version,
            "technical_details": details,
        }
        try:
            return _create(
                ModelChangeOutcome,
                {
                    "id": outcome_id,
                    "episode": episode,
                    "work_order": work_order,
                    "blocked_decision": blocked_decision,
                    "stage": stage,
                    "reason_code": reason_code,
                    "public_message": public_message,
                    "next_action": next_action,
                    "closure_digest": closure_digest,
                    "attempt_key": attempt_key,
                    "protocol_version": protocol_version,
                    "technical_details": details,
                },
                payload,
            )
        except ModelChangeRejected:
            existing = ModelChangeOutcome.objects.filter(
                stage=stage, attempt_key=attempt_key
            ).first()
            if existing is not None:
                return existing
            raise

    @staticmethod
    def record_runtime_failure(
        order: WorkOrder, reason_code: str
    ) -> ModelChangeOutcome:
        episode = order.campaign.model_change_episode
        return OutcomeService._record(
            episode=episode,
            work_order=order,
            stage=ModelChangeOutcome.Stage.RUNTIME_FAILURE,
            reason_code=reason_code,
            public_message=(
                "The work could not be completed safely. No workbook changed."
            ),
            next_action=ModelChangeOutcome.NextAction.RETRY_WORK,
            closure_digest=str(order.packet["closure_digest"]),
            attempt_key=canonical_digest(
                {"stage": "runtime", "work_order": str(order.pk)}
            ),
            protocol_version=str(order.packet["protocol_version"]),
            technical_details={"failure_stage": reason_code},
        )

    @staticmethod
    def record_worker_refusal(
        order: WorkOrder, refusal: Mapping[str, object]
    ) -> ModelChangeOutcome:
        episode = order.campaign.model_change_episode
        reason = str(refusal["reason"]).strip()
        return OutcomeService._record(
            episode=episode,
            work_order=order,
            stage=ModelChangeOutcome.Stage.WORKER_REFUSAL,
            reason_code="WORKER_REFUSED_BOUNDED_WORK",
            public_message=(
                f"The worker could not produce a bounded proposal: {reason} "
                "No workbook changed."
            ),
            next_action=ModelChangeOutcome.NextAction.RETRY_WORK,
            closure_digest=str(order.packet["closure_digest"]),
            attempt_key=canonical_digest(
                {"stage": "refusal", "work_order": str(order.pk)}
            ),
            protocol_version=str(order.packet["protocol_version"]),
            technical_details={
                "reason": reason,
                "protocol_version": str(order.packet["protocol_version"]),
            },
        )

    @staticmethod
    def record_calculation_failure(
        blocked_decision: AdmissibilityDecision,
        *,
        repair_key: str,
        reason_code: str,
        adapter_profile: str,
    ) -> ModelChangeOutcome:
        return OutcomeService._record(
            episode=blocked_decision.proposal.episode,
            blocked_decision=blocked_decision,
            stage=ModelChangeOutcome.Stage.CALCULATION_FAILURE,
            reason_code=reason_code,
            public_message=(
                "The candidate could not be calculated safely. "
                "The original workbook remains unchanged."
            ),
            next_action=ModelChangeOutcome.NextAction.RETRY_CANDIDATE,
            closure_digest=blocked_decision.proposal.closure_digest,
            attempt_key=repair_key,
            protocol_version=blocked_decision.proposal.protocol_version,
            technical_details={
                "failure_stage": reason_code,
                "adapter_profile": adapter_profile,
            },
        )


def _collect_model_change_artifacts(order: WorkOrder, actor: object) -> int:
    """Collect only this finalized attempt; failed predecessors remain evidence."""
    campaign_services.require_director(order.campaign, actor)
    if order.protocol != "model_change_v0":
        raise ModelChangeRejected("WRONG_PROTOCOL", "work order is unavailable")
    if order.artifacts.exists():
        campaign_services._stored_attestation(order)
        return order.artifacts.count()
    if not campaign_services._completion_observed(order):
        raise campaign_services.CampaignRejected(
            "observe exact work-order completion before collecting outputs"
        )
    campaign_services._verify_materialized_bound_inputs(order)
    root = campaign_services._seal_output_root(order)
    if root is None:
        raise campaign_services.CampaignRejected(
            "work-order output root is unavailable"
        )
    contract = order.packet["output_contract"]
    files = campaign_services._output_files(
        root,
        exact_paths=set(contract["required_paths"]) | {contract["attestation_path"]},
    )
    attestation = files.pop(contract["attestation_path"], None)
    if attestation is None:
        raise campaign_services.CampaignRejected(
            "work order lacks its final artifact attestation"
        )
    campaign_services._validate_artifact_attestation(order, attestation, files)
    files[contract["attestation_path"]] = attestation
    with transaction.atomic():
        for relative, content in sorted(files.items()):
            Artifact.objects.create(
                campaign=order.campaign,
                work_order=order,
                kind=Path(relative).stem,
                relative_path=relative,
                version=1,
                media_type="application/json",
                content=content,
                digest=sha256(content).hexdigest(),
            )
    return len(files)


class RunService:
    @staticmethod
    def run(
        actor: object, order: WorkOrder
    ) -> tuple[ModelChangeProposal | dict[str, object], AdmissibilityDecision | None]:
        """Run one closed, synchronous NTM/Codex unit and admit only after custody."""
        _feature_enabled()
        _owned(order.campaign.model_change_episode, actor)
        if order.protocol != "model_change_v0":
            raise ModelChangeRejected("WRONG_PROTOCOL", "work order is unavailable")
        if order.model_change_outcomes.exists():
            raise ModelChangeRejected(
                "ATTEMPT_FINAL", "this work attempt is already complete"
            )
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
            _collect_model_change_artifacts(order, actor)
        except campaign_services.CampaignRejected as exc:
            return OutcomeService.record_runtime_failure(order, "RUNTIME_FAILED"), None
        except (OSError, ValueError):
            return OutcomeService.record_runtime_failure(order, "RUNTIME_FAILED"), None
        except ModelChangeRejected as exc:
            return OutcomeService.record_runtime_failure(order, exc.reason_code), None
        output = order.artifacts.get(relative_path=MODEL_OUTPUT)
        result = ProposalParser.parse(bytes(output.content), order.packet)
        if isinstance(result, dict):
            return OutcomeService.record_worker_refusal(order, result), None
        return result, AdmissibilityGate.evaluate(
            result, str(order.packet["closure_digest"])
        )


def _invalidated(kind: str, identity: uuid.UUID) -> bool:
    return InvalidationEvent.objects.filter(
        descendant_type=kind, descendant_id=identity
    ).exists()


class AdmissibilityGate:
    @staticmethod
    def expected(proposal: ModelChangeProposal) -> dict[str, str]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT validator_version, outcome, reason_code, closure_digest
                FROM campaign_model_change_expected_admission_v1(%s)
                """,
                [proposal.pk],
            )
            row = cursor.fetchone()
        if row is None or any(value is None for value in row):
            raise ModelChangeRejected(
                "CANONICAL_ADMISSION_UNAVAILABLE",
                "the canonical admission result is unavailable",
            )
        return {
            "validator_version": str(row[0]),
            "outcome": str(row[1]),
            "reason_code": str(row[2]),
            "closure_digest": str(row[3]),
        }

    @staticmethod
    @transaction.atomic
    def evaluate(
        proposal: ModelChangeProposal, current_closure_digest: str
    ) -> AdmissibilityDecision:
        _feature_enabled()
        expected = AdmissibilityGate.expected(proposal)
        decision_id = uuid.uuid4()
        payload = {
            "id": str(decision_id),
            "proposal": str(proposal.pk),
            "proposal_sha256": proposal.digest,
            **expected,
        }
        return _create(
            AdmissibilityDecision,
            {
                "id": decision_id,
                "proposal": proposal,
                **expected,
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


def _repair_key(
    *,
    blocked: AdmissibilityDecision,
    annual_assertion: SourceAssertion,
    actor: object,
    adapter_profile: str,
    idempotency_key: str,
) -> str:
    material = "|".join(
        (
            "repair-v1",
            str(blocked.pk),
            str(annual_assertion.pk),
            str(getattr(actor, "pk", "")),
            Amendment.Action.USE_FILED_ANNUAL_REPORT,
            blocked.proposal.closure_digest,
            adapter_profile,
            idempotency_key,
        )
    )
    return sha256(material.encode("utf-8")).hexdigest()


class InvalidationService:
    @staticmethod
    @transaction.atomic
    def _repair_wrong_source(
        actor: object,
        blocked: AdmissibilityDecision,
        annual_assertion: SourceAssertion,
        *,
        repair_key: str,
        adapter_profile: str,
        idempotency_key: str,
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
        replacement_closure = repair_key
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
            "adapter_profile": adapter_profile,
            "idempotency_key": idempotency_key,
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
            "repair_key": repair_key,
            "adapter_profile": adapter_profile,
            "idempotency_key": idempotency_key,
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
                "repair_key": repair_key,
                "adapter_profile": adapter_profile,
                "idempotency_key": idempotency_key,
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
        _feature_enabled()
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
        _feature_enabled()
        proposal = pass_decision.proposal
        if (
            pass_decision.outcome != AdmissibilityDecision.Outcome.PASS
            or exact_parent.pk != proposal.starting_artifact_id
            or _invalidated(InvalidationEvent.DescendantType.PROPOSAL, proposal.pk)
            or _invalidated(InvalidationEvent.DescendantType.DECISION, pass_decision.pk)
        ):
            raise ModelChangeRejected("PASS_REQUIRED", "current exact pass is required")
        existing = ArtifactVersion.objects.filter(
            role=ArtifactVersion.Role.CANDIDATE,
            candidate_from_pass=pass_decision,
        ).first()
        if existing is not None:
            receipt = getattr(existing, "calculation_receipt", None)
            if (
                receipt is None
                or existing.parent_id != exact_parent.pk
                or receipt.adapter_profile != adapter_profile.get("profile_id")
                or receipt.closure_digest != proposal.closure_digest
                or receipt.formula_errors
            ):
                raise ModelChangeRejected(
                    "INCONSISTENT_CANDIDATE",
                    "the existing candidate is incomplete or inconsistent",
                )
            return existing, dict(receipt.operation_receipt), receipt
        patched, operation_receipt = adapter.apply(
            bytes(exact_parent.content),
            [proposal.operation],
            proposal.manifest.digest,
            adapter_profile,
            expected_inspection_digest=proposal.manifest.inspection_digest,
        )
        calculated, engine = adapter.calculate(patched, adapter_profile)
        if engine["formula_errors"]:
            raise adapter.AdapterRejected(
                "FORMULA_ERRORS",
                "the calculation engine returned formula errors",
            )
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


class RepairService:
    @staticmethod
    def _existing_result(
        *,
        actor: object,
        blocked: AdmissibilityDecision,
        annual_assertion: SourceAssertion,
        adapter_profile: str,
        idempotency_key: str,
    ) -> RepairResult | None:
        amendment = (
            Amendment.objects.select_related("replacement_proposal")
            .filter(
                blocked_decision=blocked,
                action=Amendment.Action.USE_FILED_ANNUAL_REPORT,
            )
            .first()
        )
        if amendment is None:
            return None
        bounded = amendment.bounded_change
        if (
            amendment.actor_id != getattr(actor, "pk", None)
            or bounded.get("to_source_assertion") != str(annual_assertion.pk)
            or amendment.adapter_profile != adapter_profile
            or amendment.idempotency_key != idempotency_key
        ):
            raise ModelChangeRejected(
                "CONFLICTING_REPAIR",
                "a different filed-report repair already completed",
            )
        replacement = amendment.replacement_proposal
        passed = getattr(replacement, "admissibility_decision", None)
        candidate = (
            passed.candidate_artifacts.filter(
                role=ArtifactVersion.Role.CANDIDATE
            ).first()
            if passed is not None
            else None
        )
        receipt = getattr(candidate, "calculation_receipt", None) if candidate else None
        if (
            passed is None
            or passed.outcome != AdmissibilityDecision.Outcome.PASS
            or candidate is None
            or receipt is None
            or receipt.formula_errors
        ):
            raise ModelChangeRejected(
                "INCONSISTENT_REPAIR",
                "the existing filed-report repair is incomplete",
            )
        return RepairResult(
            amendment=amendment,
            replacement_proposal=replacement,
            pass_decision=passed,
            candidate=candidate,
            calculation_receipt=receipt,
            created_or_existing="existing",
        )

    @staticmethod
    def _current_block(blocked: AdmissibilityDecision) -> bool:
        episode = blocked.proposal.episode
        if (
            blocked.outcome != AdmissibilityDecision.Outcome.BLOCK
            or blocked.reason_code != "BLOCK_WRONG_DOCUMENT_CLASS"
            or _invalidated(InvalidationEvent.DescendantType.PROPOSAL, blocked.proposal_id)
            or _invalidated(InvalidationEvent.DescendantType.DECISION, blocked.pk)
        ):
            return False
        invalid_proposals = set(
            InvalidationEvent.objects.filter(
                amendment__episode=episode,
                descendant_type=InvalidationEvent.DescendantType.PROPOSAL,
            ).values_list("descendant_id", flat=True)
        )
        current = next(
            (
                proposal
                for proposal in reversed(
                    list(
                        episode.model_change_proposals.order_by("created_at", "pk")
                    )
                )
                if proposal.pk not in invalid_proposals
            ),
            None,
        )
        return current is not None and current.pk == blocked.proposal_id

    @staticmethod
    def create_candidate_using_filed_report(
        actor: object,
        blocked_decision: AdmissibilityDecision,
        annual_assertion: SourceAssertion,
        adapter_profile: Mapping[str, object],
        idempotency_key: str,
    ) -> RepairResult:
        _feature_enabled()
        profile_id = adapter_profile.get("profile_id")
        if (
            not isinstance(profile_id, str)
            or not profile_id
            or not isinstance(idempotency_key, str)
            or not idempotency_key
            or len(idempotency_key) > 120
        ):
            raise ModelChangeRejected(
                "INVALID_REPAIR_COMMAND", "the filed-report repair is malformed"
            )
        repair_key = _repair_key(
            blocked=blocked_decision,
            annual_assertion=annual_assertion,
            actor=actor,
            adapter_profile=profile_id,
            idempotency_key=idempotency_key,
        )
        try:
            with transaction.atomic():
                ModelChangeEpisode.objects.select_for_update().get(
                    pk=blocked_decision.proposal.episode_id
                )
                blocked = AdmissibilityDecision.objects.select_for_update().select_related(
                    "proposal__episode__job",
                    "proposal__source_assertion__document_version",
                ).get(pk=blocked_decision.pk)
                existing = RepairService._existing_result(
                    actor=actor,
                    blocked=blocked,
                    annual_assertion=annual_assertion,
                    adapter_profile=profile_id,
                    idempotency_key=idempotency_key,
                )
                if existing is not None:
                    return existing
                _owned(blocked.proposal.episode, actor)
                if not RepairService._current_block(blocked):
                    raise ModelChangeRejected(
                        "STALE_REPAIR", "the source exception is no longer current"
                    )
                if (
                    annual_assertion.document_version.episode_id
                    != blocked.proposal.episode_id
                    or annual_assertion.document_version.document_class
                    != SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
                ):
                    raise ModelChangeRejected(
                        "INVALID_REPAIR",
                        "the captured filed annual report is unavailable",
                    )
                amendment, replacement, passed = (
                    InvalidationService._repair_wrong_source(
                        actor,
                        blocked,
                        annual_assertion,
                        repair_key=repair_key,
                        adapter_profile=profile_id,
                        idempotency_key=idempotency_key,
                    )
                )
                if passed.outcome != AdmissibilityDecision.Outcome.PASS:
                    raise ModelChangeRejected(
                        "REPAIR_BLOCKED",
                        "the filed-report replacement did not pass",
                    )
                candidate, _, receipt = CandidateService.create(
                    passed,
                    blocked.proposal.episode.starting_artifact,
                    adapter_profile,
                )
                return RepairResult(
                    amendment=amendment,
                    replacement_proposal=replacement,
                    pass_decision=passed,
                    candidate=candidate,
                    calculation_receipt=receipt,
                    created_or_existing="created",
                )
        except adapter.AdapterRejected as exc:
            blocked = AdmissibilityDecision.objects.select_related(
                "proposal__episode"
            ).get(pk=blocked_decision.pk)
            outcome = OutcomeService.record_calculation_failure(
                blocked,
                repair_key=repair_key,
                reason_code=exc.reason_code,
                adapter_profile=profile_id,
            )
            return RepairResult(
                outcome=outcome,
                created_or_existing="failure",
            )


class DispositionService:
    @staticmethod
    def record(
        actor: object,
        candidate: ArtifactVersion,
        named_use: str,
        kind: str,
        rationale: str = "",
    ) -> ArtifactDisposition:
        _feature_enabled()
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
        _feature_enabled()
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
        work_order = episode.campaign.work_orders.filter(
            protocol="model_change_v0"
        ).order_by("created_at", "pk").last()
        outcomes = list(
            episode.model_change_outcomes.select_related(
                "work_order", "blocked_decision"
            ).order_by("created_at", "pk")
        )
        technical_outcome = None
        for item in reversed(outcomes):
            if (
                item.stage == ModelChangeOutcome.Stage.CALCULATION_FAILURE
                and candidate is None
                and decision is not None
                and item.blocked_decision_id == decision.pk
            ):
                technical_outcome = item
                break
            if (
                item.stage
                in {
                    ModelChangeOutcome.Stage.RUNTIME_FAILURE,
                    ModelChangeOutcome.Stage.WORKER_REFUSAL,
                }
                and work_order is not None
                and item.work_order_id == work_order.pk
                and not ModelChangeProposal.objects.filter(
                    work_order=work_order
                ).exists()
            ):
                technical_outcome = item
                break
        next_action = (
            technical_outcome.next_action
            if technical_outcome is not None
            else ModelChangeOutcome.NextAction.NONE
        )
        next_action_key = None
        if (
            decision is not None
            and decision.reason_code == "BLOCK_WRONG_DOCUMENT_CLASS"
            and candidate is None
        ):
            basis = (
                {"outcome": technical_outcome.digest, "action": "retry-candidate"}
                if technical_outcome
                and technical_outcome.stage
                == ModelChangeOutcome.Stage.CALCULATION_FAILURE
                else {"block": decision.digest, "action": "filed-report"}
            )
            next_action_key = canonical_digest(basis)
        candidate_source = (
            candidate.candidate_from_pass.proposal.source_assertion
            if candidate is not None
            else None
        )
        historical_block = (
            AdmissibilityDecision.objects.select_related(
                "proposal__source_assertion__document_version__artifact"
            )
            .filter(
                proposal__episode=episode,
                reason_code="BLOCK_WRONG_DOCUMENT_CLASS",
            )
            .order_by("created_at", "pk")
            .first()
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
            "work_order": work_order,
            "proposal": current_proposal,
            "decision": decision,
            "candidate": candidate,
            "calculation": calculation,
            "disposition": disposition,
            "candidate_source": candidate_source,
            "blocked_source": (
                historical_block.proposal.source_assertion
                if historical_block
                else None
            ),
            "technical_outcome": technical_outcome,
            "next_action": next_action,
            "next_action_key": next_action_key,
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
                "outcomes": outcomes,
            },
        }
