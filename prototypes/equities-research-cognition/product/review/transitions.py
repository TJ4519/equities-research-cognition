from __future__ import annotations

from hashlib import sha256
import json

from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError

from .models import (
    ConsequenceDecision,
    CurrentCorrection,
    ExposureEvent,
    FirstPass,
    FutureProposal,
    QueueAssignment,
    ReviewCompletion,
    RubricEvalState,
    CONSEQUENCE_ACTIONS,
    digest,
)

LINEAGE_FIELDS = "sequence kind label availability locator content_digest artifact_id trace_id span_id producer relations".split()
PACKET_FIELDS = "question source_identity source_url source_locator exact_passage context_items rubric subject_mode packet_digest rubric_digest".split()


class LockRejected(Exception):
    pass


class CompletionRejected(Exception):
    pass


def fingerprint(session_key: str) -> str:
    return sha256(session_key.encode()).hexdigest()


def lock_first_pass(*, assignment_id: int, user: object, session_key: str, packet_digest: str,
                    rubric_digest: str, decision: str, rationale: str) -> FirstPass:
    if decision not in FirstPass.Decision.values or not rationale.strip():
        raise LockRejected("a valid decision and rationale are required")
    try:
        with transaction.atomic():
            assignment = QueueAssignment.objects.select_for_update().select_related("case", "enrollment").get(
                pk=assignment_id, enrollment__user=user, enrollment__is_active=True, is_active=True
            )
            case = assignment.case
            if (
                packet_digest != case.packet_digest
                or rubric_digest != case.rubric_digest
                or case.packet_digest != digest(case.packet_body())
                or case.rubric_digest != digest(case.rubric)
            ):
                raise LockRejected("the reviewed packet or rubric is stale")
            lineage_snapshot = []
            for record in case.lineage_records.all():
                record.full_clean()
                snapshot = {field: getattr(record, field) for field in LINEAGE_FIELDS}
                snapshot.update({
                    "kind_label": record.get_kind_display(),
                    "availability_label": record.get_availability_display(),
                })
                lineage_snapshot.append(snapshot)
            lineage_digest = digest(lineage_snapshot)
            packet_snapshot = {field: getattr(case, field) for field in PACKET_FIELDS}
            first_pass = FirstPass.objects.create(
                assignment=assignment,
                author_user=user,
                session_fingerprint=fingerprint(session_key),
                reviewer_scope_snapshot={
                    "enrollment_id": assignment.enrollment_id,
                    "scope_code": assignment.enrollment.scope_code,
                    "qualification_basis": assignment.enrollment.qualification_basis,
                    "attested_by": assignment.enrollment.attested_by,
                },
                packet_digest_snapshot=case.packet_digest,
                rubric_digest_snapshot=case.rubric_digest,
                subject_mode_snapshot=case.subject_mode,
                packet_snapshot=packet_snapshot,
                decision=decision,
                rationale=rationale.strip(),
            )
            ExposureEvent.objects.create(
                first_pass=first_pass,
                lineage_digest=lineage_digest,
                lineage_snapshot=lineage_snapshot,
            )
            return first_pass
    except (QueueAssignment.DoesNotExist, IntegrityError, ValidationError) as exc:
        raise LockRejected("case is unavailable or already locked") from exc


def _text(data: dict[str, str], key: str) -> str:
    value = data.get(key, "").strip()
    if not value:
        raise CompletionRejected(f"{key} is required")
    return value


def _validate_completion(data: dict[str, str]) -> dict[str, object]:
    try:
        first_pass_id = int(data.get("first_pass_id", ""))
    except ValueError as exc:
        raise CompletionRejected("first pass reference is invalid") from exc
    adjudicated = data.get("adjudicated_decision", "")
    if adjudicated not in FirstPass.Decision.values:
        raise CompletionRejected("adjudicated decision is invalid")
    normalized: dict[str, object] = {
        "first_pass_id": first_pass_id,
        "packet_digest": data.get("packet_digest", ""),
        "lineage_digest": data.get("lineage_digest", ""),
        "adjudicated_decision": adjudicated,
        "diagnosis": _text(data, "diagnosis"),
        "corrected_judgment": _text(data, "corrected_judgment"),
        "lanes": [],
    }
    lanes = []
    for family in ("current", "rubric", "future"):
        action = data.get(f"{family}_action", "")
        specification = CONSEQUENCE_ACTIONS[family].get(action)
        if specification is None:
            raise CompletionRejected(f"{family} consequence action is invalid")
        target, effect = specification
        payload = data.get(f"{family}_payload", "").strip()
        if bool(effect) != bool(payload):
            raise CompletionRejected(f"{family} consequence payload does not match its action")
        reversibility = data.get("future_reversibility", "").strip() if family == "future" else ""
        if family == "future" and bool(effect) != bool(reversibility):
            raise CompletionRejected("future reversibility does not match its action")
        lanes.append({
            "family": family,
            "action": action,
            "target": target,
            "effect": effect,
            "payload": payload,
            "reversibility": reversibility,
            "rationale": _text(data, f"{family}_rationale"),
        })
    normalized["lanes"] = lanes
    return normalized


def _create_decision(completion: ReviewCompletion, lane: dict[str, str]) -> None:
    ConsequenceDecision.objects.create(
        completion=completion,
        family=lane["family"],
        action=lane["action"],
        target=lane["target"],
        rationale=lane["rationale"],
        payload=lane["payload"],
    )
    effect = lane["effect"]
    if lane["family"] == "current" and effect:
        CurrentCorrection.objects.create(completion=completion, corrected_state=lane["payload"])
    elif lane["family"] == "rubric" and effect:
        RubricEvalState.objects.create(completion=completion, state_type=effect, proposed_state=lane["payload"])
    elif lane["family"] == "future" and effect:
        FutureProposal.objects.create(
            completion=completion,
            intervention_type=effect,
            proposed_change=lane["payload"],
            reversibility_plan=lane["reversibility"],
        )
def complete_review(*, user: object, session_key: str, case_id: int, data: dict[str, str]) -> ReviewCompletion:
    normalized = _validate_completion(data)
    session_fingerprint = fingerprint(session_key)
    try:
        with transaction.atomic():
            first_pass = FirstPass.objects.select_for_update(of=("self",)).select_related("assignment__enrollment", "exposure").get(
                pk=normalized["first_pass_id"], author_user=user,
                session_fingerprint=session_fingerprint,
                assignment__enrollment__user=user,
                assignment__enrollment__is_active=True,
                assignment__case_id=case_id,
            )
            if (
                normalized["packet_digest"] != first_pass.packet_digest_snapshot
                or normalized["lineage_digest"] != first_pass.exposure.lineage_digest
            ):
                raise CompletionRejected("locked review material is stale")
            completion = ReviewCompletion.objects.create(
                first_pass=first_pass,
                author_user=user,
                session_fingerprint=session_fingerprint,
                adjudicated_decision=normalized["adjudicated_decision"],
                diagnosis=normalized["diagnosis"],
                corrected_judgment=normalized["corrected_judgment"],
            )
            for lane in normalized["lanes"]:
                _create_decision(completion, lane)
            return completion
    except FirstPass.DoesNotExist as exc:
        raise CompletionRejected("locked review is unavailable to this session") from exc
    except (IntegrityError, ValidationError) as exc:
        raise CompletionRejected("review is already complete") from exc
