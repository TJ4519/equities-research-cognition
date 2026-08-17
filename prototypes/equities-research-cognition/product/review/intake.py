from __future__ import annotations

from hashlib import sha256
import json

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from product.campaign.models import ResearchCampaign
from product.campaign.services import require_director

from .models import (
    _ADMISSION_TOKEN,
    AnalystEnrollment,
    ArtifactSeal,
    JudgmentUnit,
    LineageRecord,
    PopulationAdmission,
    QueueAssignment,
    ResearchCase,
    RunRegistration,
    digest,
)


class IntakeRejected(Exception):
    pass


def _review_units(content: bytes) -> list[dict[str, object]]:
    required = {
        "unit_id",
        "question",
        "source_identity",
        "source_url",
        "source_locator",
        "exact_passage",
        "context_items",
        "rubric",
        "provisional",
        "comparison",
        "transition",
    }
    rows = []
    for line in content.splitlines():
        try:
            row = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IntakeRejected("review-unit artifact is malformed") from exc
        if (
            not isinstance(row, dict)
            or set(row) != required
            or any(
                not isinstance(row[key], str) or not row[key].strip()
                for key in (
                    "unit_id",
                    "question",
                    "source_identity",
                    "source_url",
                    "source_locator",
                    "exact_passage",
                )
            )
            or not isinstance(row["context_items"], list)
            or not isinstance(row["rubric"], list)
            or not row["rubric"]
            or any(
                not isinstance(row[key], dict)
                for key in ("provisional", "comparison", "transition")
            )
        ):
            raise IntakeRejected("review-unit artifact is malformed")
        rows.append(row)
    if not rows or len({row["unit_id"] for row in rows}) != len(rows):
        raise IntakeRejected("review population is empty or duplicated")
    return rows


def _manifest(campaign: ResearchCampaign) -> dict[str, object]:
    orders = list(campaign.work_orders.order_by("created_at"))
    links = list(
        campaign.trace_links.select_related("artifact", "work_order").order_by(
            "created_at"
        )
    )
    if not orders or len(links) != len(orders) or {
        item.work_order_id for item in links
    } != {item.pk for item in orders}:
        raise IntakeRejected("seal requires one exact provider join per work order")
    unit_artifacts = [
        item
        for item in campaign.artifacts.order_by("pk")
        if item.relative_path == "review-units.jsonl"
    ]
    if (
        len(unit_artifacts) != 1
        or not any(item.artifact_id == unit_artifacts[0].pk for item in links)
    ):
        raise IntakeRejected("seal requires one trace-linked review population")
    units = _review_units(bytes(unit_artifacts[0].content))
    return {
        "schema_version": "campaign-review-seal/v1",
        "campaign_id": str(campaign.pk),
        "commissioned_question": campaign.commissioned_question,
        "review_scope_code": "equities",
        "work_orders": [
            {
                "work_order_id": str(item.pk),
                "proposal_digest": item.proposal_digest,
                "work_order_digest": item.digest,
            }
            for item in orders
        ],
        "artifacts": [
            {
                "artifact_id": item.pk,
                "work_order_id": str(item.work_order_id),
                "kind": item.kind,
                "relative_path": item.relative_path,
                "content_digest": item.digest,
            }
            for item in campaign.artifacts.order_by("pk")
        ],
        "trace_links": [
            {
                "work_order_id": str(item.work_order_id),
                "artifact_id": item.artifact_id,
                "trace_id": item.trace_id,
                "observation_id": item.observation_id,
                "conversation_id": item.conversation_id,
                "call_id": item.call_id,
                "relation_digest": item.digest,
            }
            for item in links
        ],
        "review_artifact_id": unit_artifacts[0].pk,
        "review_artifact_digest": unit_artifacts[0].digest,
        "review_units": units,
    }


def validate_sealed_manifest(
    manifest: dict[str, object],
    registration: RunRegistration,
    manifest_digest: str,
) -> None:
    required = {
        "schema_version",
        "campaign_id",
        "commissioned_question",
        "review_scope_code",
        "work_orders",
        "artifacts",
        "trace_links",
        "review_artifact_id",
        "review_artifact_digest",
        "review_units",
    }
    if (
        not isinstance(manifest, dict)
        or set(manifest) != required
        or manifest.get("schema_version") != "campaign-review-seal/v1"
        or str(registration.run_id) != manifest.get("campaign_id")
        or registration.commissioned_question
        != manifest.get("commissioned_question")
        or registration.review_scope_code != manifest.get("review_scope_code")
        or registration.expected_unit_ids
        != sorted(row["unit_id"] for row in manifest.get("review_units", []))
        or manifest_digest != digest(manifest)
    ):
        raise IntakeRejected("campaign seal does not match its registration")


def seal_campaign(
    campaign: ResearchCampaign, requested_by: object
) -> ArtifactSeal:
    require_director(campaign, requested_by)
    manifest = _manifest(campaign)
    try:
        with transaction.atomic():
            locked = ResearchCampaign.objects.select_for_update().get(pk=campaign.pk)
            if RunRegistration.objects.filter(run_id=locked.pk).exists():
                raise IntakeRejected("campaign is already sealed")
            registration = RunRegistration.objects.create(
                run_id=locked.pk,
                artifact_root=locked.artifact_root,
                commissioned_question=locked.commissioned_question,
                review_scope_code=manifest["review_scope_code"],
                expected_unit_ids=sorted(
                    row["unit_id"] for row in manifest["review_units"]
                ),
            )
            return ArtifactSeal.objects.create(
                registration=registration,
                manifest=manifest,
                manifest_digest=digest(manifest),
            )
    except IntakeRejected:
        raise
    except (IntegrityError, ValidationError) as exc:
        raise IntakeRejected("campaign seal failed atomically") from exc


def admit_population(
    seal: ArtifactSeal,
    *,
    requested_by: object,
    idempotency_key: str,
) -> PopulationAdmission:
    if (
        not isinstance(idempotency_key, str)
        or not idempotency_key.strip()
        or len(idempotency_key.strip()) > 64
    ):
        raise IntakeRejected("admission requires an idempotency key")
    manifest = seal.manifest
    validate_sealed_manifest(manifest, seal.registration, seal.manifest_digest)
    runtime = {
        "schema_version": "campaign-runtime-evidence/v1",
        "evidence_mode": ResearchCase.SubjectMode.LANGFUSE_OBSERVED_RUN,
        "trace_links": manifest["trace_links"],
    }
    request = {
        "seal": seal.manifest_digest,
        "requested_by": getattr(requested_by, "pk", None),
        "idempotency_key": idempotency_key.strip(),
        "runtime": digest(runtime),
    }
    try:
        with transaction.atomic():
            locked = ArtifactSeal.objects.select_for_update().get(pk=seal.pk)
            admission = PopulationAdmission(
                artifact_seal=locked,
                requested_by=requested_by,
                idempotency_key=idempotency_key.strip(),
                request_digest=digest(request),
                evidence_mode=runtime["evidence_mode"],
                runtime_receipt=runtime,
                runtime_digest=digest(runtime),
            )
            admission.save(_admission_token=_ADMISSION_TOKEN)
            artifact_digest = manifest["review_artifact_digest"]
            for row in manifest["review_units"]:
                case = ResearchCase(
                    external_id=f"{manifest['campaign_id']}:{row['unit_id']}",
                    subject_mode=ResearchCase.SubjectMode.LANGFUSE_OBSERVED_RUN,
                    question=row["question"],
                    source_identity=row["source_identity"],
                    source_url=row["source_url"],
                    source_locator=row["source_locator"],
                    exact_passage=row["exact_passage"],
                    context_items=row["context_items"],
                    rubric=row["rubric"],
                    custody_tree_digest=locked.manifest_digest,
                    source_artifact_digest=artifact_digest,
                    evidence_artifact_digest=artifact_digest,
                    projection_version=manifest["schema_version"],
                    artifact_seal=locked,
                    population_admission=admission,
                )
                case.save(_admission_token=_ADMISSION_TOKEN)
                _lineage(case, manifest)
                unit = JudgmentUnit(
                    population_admission=admission,
                    case=case,
                    unit_id=row["unit_id"],
                    provisional=row["provisional"],
                    comparison=row["comparison"],
                    transition=row["transition"],
                )
                unit.save(_admission_token=_ADMISSION_TOKEN)
            return admission
    except (IntegrityError, ValidationError, KeyError, TypeError) as exc:
        raise IntakeRejected("population admission failed atomically") from exc


def _lineage(case: ResearchCase, manifest: dict[str, object]) -> None:
    sequence = 1
    for item in manifest["artifacts"]:
        record = LineageRecord(
            case=case,
            sequence=sequence,
            kind=LineageRecord.Kind.ARTIFACT,
            label=item["relative_path"],
            availability=LineageRecord.Availability.EXACT,
            locator=item["relative_path"],
            content="",
            content_digest=item["content_digest"],
            artifact_id=str(item["artifact_id"]),
            producer=item["work_order_id"],
            relations=[],
        )
        record.save(_admission_token=_ADMISSION_TOKEN)
        sequence += 1
    for item in manifest["trace_links"]:
        record = LineageRecord(
            case=case,
            sequence=sequence,
            kind=LineageRecord.Kind.RUNTIME,
            label="Exact Langfuse observation",
            availability=LineageRecord.Availability.EXACT,
            locator=f"langfuse:{item['observation_id']}",
            content="",
            content_digest=item["relation_digest"],
            artifact_id=str(item["artifact_id"]),
            trace_id=item["trace_id"],
            span_id=item["observation_id"],
            producer=item["work_order_id"],
            relations=[],
        )
        record.save(_admission_token=_ADMISSION_TOKEN)
        sequence += 1


def assign_case(
    *, case: ResearchCase, enrollment: AnalystEnrollment
) -> QueueAssignment:
    if (
        not enrollment.is_active
        or case.population_admission_id is None
        or enrollment.scope_code
        != case.population_admission.artifact_seal.registration.review_scope_code
    ):
        raise IntakeRejected("analyst is not eligible for this admitted case")
    try:
        assignment = QueueAssignment(
            enrollment=enrollment,
            case=case,
            population_admission=case.population_admission,
        )
        assignment.save(_admission_token=_ADMISSION_TOKEN)
        return assignment
    except (IntegrityError, ValidationError) as exc:
        raise IntakeRejected("analyst assignment failed closed") from exc
