from __future__ import annotations

from typing import Any

from .errors import RuntimeFailure, ValidationError
from .util import require_string_list, require_text, safe_relative_path


BRANCH_KINDS = {"lead", "research", "challenge", "artifact", "rederivation"}
INSTRUCTION_KINDS = {
    "start",
    "resume",
    "context_delta",
    "steer",
    "challenge",
    "complete_request",
}
CHECKPOINT_DISPOSITIONS = {"continue", "complete", "refuse", "blocked"}
SOURCE_REQUEST_KINDS = {"search", "url", "local_path", "licensed_connector"}


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return value


def _optional_text(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return require_text(value, label)


def _validate_relations(
    value: Any,
    *,
    label: str,
    included_assertion_ids: set[str],
    professional_object_ids: set[str],
    allowed_support_pairs: set[tuple[str, str]],
    support_required: bool,
) -> list[dict[str, str]]:
    if not isinstance(value, list) or (support_required and not value):
        qualifier = "non-empty " if support_required else ""
        raise RuntimeFailure(f"{label} must be a {qualifier}list")
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw in value:
        item = _object(raw, label)
        assertion_id = require_text(item.get("assertion_id"), f"{label} assertion")
        object_id = require_text(
            item.get("professional_object_id"),
            f"{label} professional object",
        )
        pair = (assertion_id, object_id)
        if pair in seen:
            raise RuntimeFailure(f"{label} contains a duplicate relation")
        seen.add(pair)
        if assertion_id not in included_assertion_ids:
            raise RuntimeFailure(
                f"{label} cites an assertion outside the branch context: {assertion_id}"
            )
        if object_id not in professional_object_ids:
            raise RuntimeFailure(
                f"{label} names a professional object outside the branch context: {object_id}"
            )
        if support_required and pair not in allowed_support_pairs:
            raise RuntimeFailure(
                f"{label} uses an unpermitted assertion-to-object relation: "
                f"{assertion_id} -> {object_id}"
            )
        result.append(
            {
                "assertion_id": assertion_id,
                "professional_object_id": object_id,
            }
        )
    return result


def validate_claims(
    value: Any,
    *,
    included_assertion_ids: set[str],
    professional_object_ids: set[str],
    allowed_support_pairs: set[tuple[str, str]],
    allow_empty: bool,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "non-empty " if not allow_empty else ""
        raise RuntimeFailure(f"claims must be a {qualifier}list")
    result: list[dict[str, Any]] = []
    claim_ids: set[str] = set()
    for raw in value:
        claim = _object(raw, "claim")
        claim_id = require_text(claim.get("claim_id"), "claim id")
        if claim_id in claim_ids:
            raise RuntimeFailure("claim identifiers must be unique")
        claim_ids.add(claim_id)
        support = _validate_relations(
            claim.get("support_relations", []),
            label="claim support relations",
            included_assertion_ids=included_assertion_ids,
            professional_object_ids=professional_object_ids,
            allowed_support_pairs=allowed_support_pairs,
            support_required=True,
        )
        contradictions = _validate_relations(
            claim.get("contradiction_relations", []),
            label="claim contradiction relations",
            included_assertion_ids=included_assertion_ids,
            professional_object_ids=professional_object_ids,
            allowed_support_pairs=allowed_support_pairs,
            support_required=False,
        )
        uncertainty = require_string_list(
            claim.get("uncertainty", []),
            "claim uncertainty",
            allow_empty=True,
        )
        result.append(
            {
                "claim_id": claim_id,
                "text": require_text(claim.get("text"), "claim text"),
                "support_relations": support,
                "contradiction_relations": contradictions,
                "supporting_assertion_ids": sorted(
                    {item["assertion_id"] for item in support}
                ),
                "professional_object_ids": sorted(
                    {item["professional_object_id"] for item in support + contradictions}
                ),
                "uncertainty": uncertainty,
                "scope": _object(claim.get("scope", {}), "claim scope"),
            }
        )
    return result


def validate_acknowledgement(
    value: Any,
    *,
    branch_id: str,
    binding_id: str,
    instruction_id: str,
    instruction_digest: str,
    context_ids: list[str],
    authority_ceiling: str,
) -> dict[str, Any]:
    payload = _object(value, "branch acknowledgement")
    if payload.get("schema") != "research-branch-acknowledgement/v1":
        raise RuntimeFailure("branch acknowledgement has the wrong schema")
    expected = {
        "branch_id": branch_id,
        "binding_id": binding_id,
        "instruction_id": instruction_id,
        "instruction_digest": instruction_digest,
        "context_ids": context_ids,
        "authority_ceiling": authority_ceiling,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            raise RuntimeFailure(f"branch acknowledgement disagrees on {key}")
    worker = _object(payload.get("worker"), "acknowledgement worker")
    require_text(worker.get("provider"), "worker provider")
    require_text(worker.get("model"), "worker model")
    require_text(worker.get("role"), "worker role")
    require_text(payload.get("protocol_version"), "acknowledgement protocol version")
    return payload


def validate_source_request(
    value: Any,
    *,
    branch_id: str,
    binding_id: str,
    available_object_ids: set[str],
) -> dict[str, Any]:
    payload = _object(value, "source request")
    if payload.get("schema") != "research-source-request/v1":
        raise RuntimeFailure("source request has the wrong schema")
    if payload.get("branch_id") != branch_id or payload.get("binding_id") != binding_id:
        raise RuntimeFailure("source request names the wrong branch binding")
    request_kind = require_text(payload.get("request_kind"), "source request kind")
    if request_kind not in SOURCE_REQUEST_KINDS:
        raise RuntimeFailure("source request kind is unsupported")
    locator = require_text(payload.get("locator"), "source request locator")
    object_ids = require_string_list(
        payload.get("professional_object_ids", []),
        "source request professional objects",
        allow_empty=True,
    )
    unknown = set(object_ids) - available_object_ids
    if unknown:
        raise RuntimeFailure(
            "source request names an object outside the branch: "
            + ", ".join(sorted(unknown))
        )
    return {
        "schema": "research-source-request/v1",
        "branch_id": branch_id,
        "binding_id": binding_id,
        "external_request_id": require_text(
            payload.get("external_request_id"), "external source request id"
        ),
        "request_kind": request_kind,
        "locator": locator,
        "source_class": require_text(payload.get("source_class"), "source class"),
        "purpose": require_text(payload.get("purpose"), "source request purpose"),
        "rationale": require_text(payload.get("rationale"), "source request rationale"),
        "professional_object_ids": object_ids,
        "rights_needed": _object(payload.get("rights_needed", {}), "source rights needed"),
    }


def validate_checkpoint(
    value: Any,
    *,
    branch_id: str,
    binding_id: str,
    latest_sequence: int,
    predecessor_id: str | None,
    included_assertion_ids: set[str],
    professional_object_ids: set[str],
    allowed_support_pairs: set[tuple[str, str]],
    known_source_request_ids: set[str],
) -> dict[str, Any]:
    payload = _object(value, "branch checkpoint")
    if payload.get("schema") != "research-branch-checkpoint/v1":
        raise RuntimeFailure("branch checkpoint has the wrong schema")
    if payload.get("branch_id") != branch_id or payload.get("binding_id") != binding_id:
        raise RuntimeFailure("branch checkpoint names the wrong binding")
    sequence = payload.get("sequence")
    if not isinstance(sequence, int) or sequence != latest_sequence + 1:
        raise RuntimeFailure("branch checkpoint sequence is not the next exact value")
    if payload.get("predecessor_id") != predecessor_id:
        raise RuntimeFailure("branch checkpoint names the wrong predecessor")
    disposition = require_text(payload.get("disposition"), "checkpoint disposition")
    if disposition not in CHECKPOINT_DISPOSITIONS:
        raise RuntimeFailure("checkpoint disposition is unsupported")
    claims = validate_claims(
        payload.get("candidate_claims", []),
        included_assertion_ids=included_assertion_ids,
        professional_object_ids=professional_object_ids,
        allowed_support_pairs=allowed_support_pairs,
        allow_empty=disposition in {"continue", "blocked", "refuse"},
    )
    source_request_ids = require_string_list(
        payload.get("source_request_ids", []),
        "checkpoint source requests",
        allow_empty=True,
    )
    unknown_requests = set(source_request_ids) - known_source_request_ids
    if unknown_requests:
        raise RuntimeFailure(
            "checkpoint names an unknown source request: "
            + ", ".join(sorted(unknown_requests))
        )
    refusal = _optional_text(payload.get("refusal"), "checkpoint refusal")
    if disposition == "refuse" and refusal is None:
        raise RuntimeFailure("a refusing checkpoint requires a reason")
    return {
        "schema": "research-branch-checkpoint/v1",
        "branch_id": branch_id,
        "binding_id": binding_id,
        "sequence": sequence,
        "predecessor_id": predecessor_id,
        "candidate_claims": claims,
        "rivals": payload.get("rivals", []),
        "source_request_ids": source_request_ids,
        "artifact_proposals": payload.get("artifact_proposals", []),
        "unresolved_questions": require_string_list(
            payload.get("unresolved_questions", []),
            "checkpoint unresolved questions",
            allow_empty=True,
        ),
        "next_action": _optional_text(payload.get("next_action"), "checkpoint next action"),
        "disposition": disposition,
        "refusal": refusal,
    }


def validate_branch_result(
    value: Any,
    *,
    branch_id: str,
    binding_id: str,
    checkpoint_id: str,
    included_assertion_ids: set[str],
    professional_object_ids: set[str],
    allowed_support_pairs: set[tuple[str, str]],
    available_artifact_paths: set[str],
) -> dict[str, Any]:
    payload = _object(value, "branch result")
    if payload.get("schema") != "research-branch-result/v1":
        raise RuntimeFailure("branch result has the wrong schema")
    expected = {
        "branch_id": branch_id,
        "binding_id": binding_id,
        "checkpoint_id": checkpoint_id,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            raise RuntimeFailure(f"branch result disagrees on {key}")
    refusal = _optional_text(payload.get("refusal"), "branch result refusal")
    claims = validate_claims(
        payload.get("claims", []),
        included_assertion_ids=included_assertion_ids,
        professional_object_ids=professional_object_ids,
        allowed_support_pairs=allowed_support_pairs,
        allow_empty=refusal is not None,
    )
    artifacts: list[dict[str, str]] = []
    raw_artifacts = payload.get("artifacts", [])
    if not isinstance(raw_artifacts, list):
        raise RuntimeFailure("branch result artifacts must be a list")
    for raw in raw_artifacts:
        item = _object(raw, "branch result artifact")
        path = safe_relative_path(
            require_text(item.get("path"), "branch result artifact path")
        ).as_posix()
        if path not in available_artifact_paths:
            raise RuntimeFailure(f"declared branch artifact is missing: {path}")
        artifacts.append(
            {
                "path": path,
                "kind": require_text(item.get("kind"), "branch artifact kind"),
                "title": require_text(item.get("title"), "branch artifact title"),
                "media_type": require_text(
                    item.get("media_type", "application/octet-stream"),
                    "branch artifact media type",
                ),
            }
        )
    memory_proposals = payload.get("memory_proposals", [])
    if not isinstance(memory_proposals, list):
        raise RuntimeFailure("branch memory proposals must be a list")
    normalised_memory: list[dict[str, Any]] = []
    for raw in memory_proposals:
        item = _object(raw, "branch memory proposal")
        normalised_memory.append(
            {
                "content": require_text(item.get("content"), "memory proposal content"),
                "scope": _object(item.get("scope", {}), "memory proposal scope"),
                "reason": require_text(item.get("reason"), "memory proposal reason"),
            }
        )
    if not claims and not artifacts and refusal is None:
        raise RuntimeFailure("branch result contains no claim, artifact, or refusal")
    return {
        "schema": "research-branch-result/v1",
        "branch_id": branch_id,
        "binding_id": binding_id,
        "checkpoint_id": checkpoint_id,
        "summary": require_text(payload.get("summary"), "branch result summary"),
        "claims": claims,
        "artifacts": artifacts,
        "memory_proposals": normalised_memory,
        "unresolved_questions": require_string_list(
            payload.get("unresolved_questions", []),
            "branch result unresolved questions",
            allow_empty=True,
        ),
        "refusal": refusal,
    }
