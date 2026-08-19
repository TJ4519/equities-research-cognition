from __future__ import annotations

from typing import Any

from .errors import ValidationError
from .util import require_string_list, require_text


SUPPORTED_KINDS = {
    "mandate",
    "perspective",
    "episode",
    "commission",
    "source",
    "assertion",
    "professional_object",
    "evidence_decision",
    "method",
    "context",
    "research_branch",
    "ntm_binding",
    "branch_instruction",
    "branch_event",
    "branch_ack",
    "branch_checkpoint",
    "source_request",
    "run",
    "claim",
    "result",
    "artifact",
    "decision",
    "correction",
    "memory",
    "evaluation_case",
    "replay",
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return value


def _optional_text(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if value is not None:
        require_text(value, key)


def _require_positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or value < 1:
        raise ValidationError(f"{label} must be a positive integer")
    return value


def validate_payload(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    if kind not in SUPPORTED_KINDS:
        raise ValidationError(f"unsupported object kind: {kind}")
    payload = _require_dict(payload, f"{kind} payload")
    expected_schema = f"research-{kind.replace('_', '-')}/v1"
    if payload.get("schema") != expected_schema:
        raise ValidationError(f"{kind} payload requires schema {expected_schema}")

    if kind == "mandate":
        require_text(payload.get("title"), "mandate title")
        require_text(payload.get("decision_use"), "mandate decision use")
        _require_dict(payload.get("policy", {}), "mandate policy")
        require_text(payload.get("actor"), "mandate actor")

    elif kind == "perspective":
        require_text(payload.get("mandate_id"), "perspective mandate")
        require_text(payload.get("label"), "perspective label")
        require_string_list(payload.get("item_ids", []), "perspective items", allow_empty=True)
        _optional_text(payload, "parent_id")

    elif kind == "episode":
        require_text(payload.get("mandate_id"), "episode mandate")
        require_text(payload.get("title"), "episode title")
        require_text(payload.get("original_request"), "episode original request")
        require_text(payload.get("evidence_cutoff"), "episode evidence cutoff")
        require_text(payload.get("intended_use"), "episode intended use")
        _optional_text(payload, "prior_perspective_id")

    elif kind == "commission":
        require_text(payload.get("episode_id"), "commission episode")
        require_text(payload.get("actor"), "commission actor")
        require_text(payload.get("purpose"), "commission purpose")
        require_string_list(payload.get("subject_ids", []), "commission subjects", allow_empty=True)
        require_string_list(payload.get("method_ids", []), "commission methods", allow_empty=True)
        require_string_list(payload.get("output_kinds", []), "commission outputs")
        require_string_list(payload.get("unresolved_questions", []), "commission unresolved questions", allow_empty=True)
        _require_dict(payload.get("limits", {}), "commission limits")

    elif kind == "source":
        require_text(payload.get("mandate_id"), "source mandate")
        require_text(payload.get("filename"), "source filename")
        require_text(payload.get("media_type"), "source media type")
        require_text(payload.get("blob_digest"), "source blob digest")
        require_text(payload.get("source_class"), "source class")
        _require_dict(payload.get("rights", {}), "source rights")
        _require_dict(payload.get("metadata", {}), "source metadata")
        _optional_text(payload, "published_at")

    elif kind == "assertion":
        require_text(payload.get("source_id"), "assertion source")
        require_text(payload.get("locator"), "assertion locator")
        require_text(payload.get("content"), "assertion content")
        _require_dict(payload.get("attributes", {}), "assertion attributes")
        require_text(payload.get("proposed_by"), "assertion proposer")

    elif kind == "professional_object":
        require_text(payload.get("mandate_id"), "professional-object mandate")
        require_text(payload.get("kind"), "professional-object kind")
        require_text(payload.get("label"), "professional-object label")
        _require_dict(payload.get("attributes", {}), "professional-object attributes")
        _require_dict(payload.get("binding", {}), "professional-object binding")
        if payload.get("authority") not in {"model_proposed", "human_confirmed", "policy"}:
            raise ValidationError("professional-object authority is invalid")
        require_text(payload.get("actor"), "professional-object actor")

    elif kind == "evidence_decision":
        require_text(payload.get("episode_id"), "evidence-decision episode")
        require_text(payload.get("assertion_id"), "evidence-decision assertion")
        require_text(payload.get("professional_object_id"), "evidence-decision object")
        require_text(payload.get("intended_use"), "evidence-decision intended use")
        require_string_list(payload.get("permitted_actions", []), "evidence-decision actions", allow_empty=True)
        if payload.get("decision") not in {"admit", "quarantine", "reject"}:
            raise ValidationError("evidence decision must be admit, quarantine, or reject")
        require_text(payload.get("rationale"), "evidence-decision rationale")
        require_text(payload.get("actor"), "evidence-decision actor")
        _optional_text(payload, "effective_until")

    elif kind == "method":
        require_text(payload.get("name"), "method name")
        require_text(payload.get("version"), "method version")
        require_text(payload.get("purpose"), "method purpose")
        require_string_list(payload.get("output_kinds", []), "method outputs")
        require_string_list(payload.get("required_actions", []), "method required actions", allow_empty=True)
        _require_dict(payload.get("runtime", {}), "method runtime")
        _require_dict(payload.get("limits", {}), "method limits")

    elif kind == "context":
        require_text(payload.get("episode_id"), "context episode")
        require_text(payload.get("commission_id"), "context commission")
        require_text(payload.get("method_id"), "context method")
        require_text(payload.get("purpose"), "context purpose")
        require_text(payload.get("intended_use"), "context intended use")
        require_string_list(payload.get("professional_object_ids", []), "context professional objects")
        require_string_list(payload.get("included_assertion_ids", []), "context included assertions", allow_empty=True)
        exclusions = payload.get("excluded_assertions", [])
        if not isinstance(exclusions, list):
            raise ValidationError("context exclusions must be a list")
        for item in exclusions:
            item = _require_dict(item, "context exclusion")
            require_text(item.get("assertion_id"), "excluded assertion")
            require_text(item.get("reason"), "exclusion reason")
        require_string_list(payload.get("memory_entry_ids", []), "context memory", allow_empty=True)
        require_string_list(payload.get("allowed_tools", []), "context tools", allow_empty=True)
        require_text(payload.get("relative_directory"), "context directory")
        require_text(payload.get("manifest_digest"), "context manifest digest")

    elif kind == "research_branch":
        require_text(payload.get("episode_id"), "branch episode")
        require_text(payload.get("commission_id"), "branch commission")
        require_text(payload.get("method_id"), "branch method")
        if payload.get("branch_kind") not in {"lead", "research", "challenge", "artifact", "rederivation"}:
            raise ValidationError("branch kind is unsupported")
        require_text(payload.get("title"), "branch title")
        require_text(payload.get("question"), "branch question")
        require_string_list(payload.get("expected_outputs", []), "branch expected outputs")
        require_text(payload.get("authority_ceiling"), "branch authority ceiling")
        require_text(payload.get("created_by"), "branch creator")
        require_string_list(payload.get("context_ids", []), "branch contexts", allow_empty=True)
        require_string_list(payload.get("input_object_ids", []), "branch input objects", allow_empty=True)
        _optional_text(payload, "parent_branch_id")

    elif kind == "ntm_binding":
        require_text(payload.get("branch_id"), "binding branch")
        require_text(payload.get("session"), "binding session")
        _require_positive_int(payload.get("pane"), "binding pane")
        require_text(payload.get("role_name"), "binding role")
        require_text(payload.get("model"), "binding model")
        require_text(payload.get("config_path"), "binding config path")
        require_text(payload.get("config_digest"), "binding config digest")
        require_text(payload.get("working_directory"), "binding working directory")
        require_text(payload.get("attempt_manifest_digest"), "binding attempt manifest digest")
        require_string_list(payload.get("context_ids", []), "binding contexts", allow_empty=True)
        _optional_text(payload, "predecessor_binding_id")
        _optional_text(payload, "resume_checkpoint_id")

    elif kind == "branch_instruction":
        require_text(payload.get("branch_id"), "instruction branch")
        require_text(payload.get("binding_id"), "instruction binding")
        _require_positive_int(payload.get("sequence"), "instruction sequence")
        if payload.get("instruction_kind") not in {
            "start", "resume", "context_delta", "steer", "challenge", "complete_request"
        }:
            raise ValidationError("branch instruction kind is unsupported")
        require_text(payload.get("actor"), "instruction actor")
        require_text(payload.get("message_path"), "instruction message path")
        require_text(payload.get("message_digest"), "instruction message digest")
        require_string_list(payload.get("context_ids", []), "instruction contexts", allow_empty=True)
        _optional_text(payload, "checkpoint_id")

    elif kind == "branch_event":
        require_text(payload.get("branch_id"), "event branch")
        require_text(payload.get("event_kind"), "branch event kind")
        require_text(payload.get("actor"), "branch event actor")
        _require_dict(payload.get("details", {}), "branch event details")
        _optional_text(payload, "binding_id")
        _optional_text(payload, "instruction_id")

    elif kind == "branch_ack":
        require_text(payload.get("branch_id"), "acknowledgement branch")
        require_text(payload.get("binding_id"), "acknowledgement binding")
        require_text(payload.get("instruction_id"), "acknowledgement instruction")
        require_text(payload.get("instruction_digest"), "acknowledgement instruction digest")
        require_string_list(payload.get("context_ids", []), "acknowledgement contexts", allow_empty=True)
        require_text(payload.get("authority_ceiling"), "acknowledgement authority ceiling")
        _require_dict(payload.get("worker", {}), "acknowledgement worker")
        require_text(payload.get("protocol_version"), "acknowledgement protocol version")

    elif kind == "branch_checkpoint":
        require_text(payload.get("branch_id"), "checkpoint branch")
        require_text(payload.get("binding_id"), "checkpoint binding")
        _require_positive_int(payload.get("sequence"), "checkpoint sequence")
        _optional_text(payload, "predecessor_id")
        _optional_text(payload, "acknowledgement_id")
        if not isinstance(payload.get("candidate_claims", []), list):
            raise ValidationError("checkpoint candidate claims must be a list")
        if not isinstance(payload.get("rivals", []), list):
            raise ValidationError("checkpoint rivals must be a list")
        require_string_list(payload.get("source_request_ids", []), "checkpoint source requests", allow_empty=True)
        if not isinstance(payload.get("artifact_proposals", []), list):
            raise ValidationError("checkpoint artifact proposals must be a list")
        require_string_list(payload.get("unresolved_questions", []), "checkpoint unresolved questions", allow_empty=True)
        if payload.get("disposition") not in {"continue", "complete", "refuse", "blocked"}:
            raise ValidationError("checkpoint disposition is unsupported")
        _optional_text(payload, "next_action")
        _optional_text(payload, "refusal")

    elif kind == "source_request":
        require_text(payload.get("branch_id"), "source request branch")
        require_text(payload.get("binding_id"), "source request binding")
        require_text(payload.get("external_request_id"), "external source request id")
        require_text(payload.get("request_kind"), "source request kind")
        require_text(payload.get("locator"), "source request locator")
        require_text(payload.get("source_class"), "source request class")
        require_text(payload.get("purpose"), "source request purpose")
        require_text(payload.get("rationale"), "source request rationale")
        require_string_list(payload.get("professional_object_ids", []), "source request objects", allow_empty=True)
        _require_dict(payload.get("rights_needed", {}), "source request rights")

    elif kind == "run":
        require_text(payload.get("context_id"), "run context")
        require_text(payload.get("adapter"), "run adapter")
        if not isinstance(payload.get("argv"), list) or not payload["argv"]:
            raise ValidationError("run argv must be a non-empty list")
        require_text(payload.get("working_directory"), "run working directory")
        if payload.get("status") not in {"succeeded", "failed", "timed_out"}:
            raise ValidationError("run status is invalid")
        require_text(payload.get("stdout_digest"), "run stdout digest")
        require_text(payload.get("stderr_digest"), "run stderr digest")
        _require_dict(payload.get("output_manifest", {}), "run output manifest")

    elif kind == "claim":
        require_text(payload.get("episode_id"), "claim episode")
        require_text(payload.get("run_id"), "claim run")
        require_text(payload.get("text"), "claim text")
        require_string_list(payload.get("supporting_assertion_ids", []), "claim supporting assertions")
        require_string_list(payload.get("professional_object_ids", []), "claim professional objects")
        require_string_list(payload.get("uncertainty", []), "claim uncertainty", allow_empty=True)

    elif kind == "result":
        require_text(payload.get("episode_id"), "result episode")
        require_text(payload.get("run_id"), "result run")
        require_text(payload.get("summary"), "result summary")
        require_string_list(payload.get("claim_ids", []), "result claims", allow_empty=True)
        require_string_list(payload.get("artifact_ids", []), "result artifacts", allow_empty=True)
        require_string_list(payload.get("memory_proposal_ids", []), "result memory proposals", allow_empty=True)

    elif kind == "artifact":
        require_text(payload.get("mandate_id"), "artifact mandate")
        require_text(payload.get("episode_id"), "artifact episode")
        require_text(payload.get("kind"), "artifact kind")
        require_text(payload.get("filename"), "artifact filename")
        require_text(payload.get("blob_digest"), "artifact blob digest")
        _require_dict(payload.get("metadata", {}), "artifact metadata")
        _optional_text(payload, "parent_id")

    elif kind == "decision":
        require_text(payload.get("episode_id"), "decision episode")
        require_text(payload.get("target_id"), "decision target")
        require_text(payload.get("action"), "decision action")
        require_text(payload.get("purpose"), "decision purpose")
        require_text(payload.get("actor"), "decision actor")
        _require_dict(payload.get("grant", {}), "decision grant")

    elif kind == "correction":
        require_text(payload.get("episode_id"), "correction episode")
        require_text(payload.get("target_id"), "correction target")
        require_text(payload.get("actor"), "correction actor")
        require_text(payload.get("reason"), "correction reason")
        _require_dict(payload.get("replacement", {}), "correction replacement")
        _require_dict(payload.get("scope", {}), "correction scope")

    elif kind == "memory":
        require_text(payload.get("mandate_id"), "memory mandate")
        require_text(payload.get("actor"), "memory actor")
        require_text(payload.get("content"), "memory content")
        _require_dict(payload.get("scope", {}), "memory scope")
        require_text(payload.get("authority"), "memory authority")
        _optional_text(payload, "source_correction_id")
        _optional_text(payload, "effective_until")

    elif kind == "evaluation_case":
        require_text(payload.get("mandate_id"), "evaluation mandate")
        require_text(payload.get("episode_id"), "evaluation episode")
        require_text(payload.get("name"), "evaluation name")
        require_text(payload.get("baseline_run_id"), "evaluation baseline run")
        require_text(payload.get("baseline_result_id"), "evaluation baseline result")
        _require_dict(payload.get("expected", {}), "evaluation expected result")

    elif kind == "replay":
        require_text(payload.get("evaluation_case_id"), "replay evaluation case")
        require_text(payload.get("mode"), "replay mode")
        if payload.get("status") not in {"pass", "fail", "limited"}:
            raise ValidationError("replay status is invalid")
        require_text(payload.get("grade"), "replay grade")
        _require_dict(payload.get("checks", {}), "replay checks")
        _require_dict(payload.get("comparison", {}), "replay comparison")

    return payload
