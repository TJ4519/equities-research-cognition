from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ResearchStateTransition, WorkOrder


SCHEMA = "investor-research-state/v1"
DELTA_SCHEMA = "epistemic-delta/v1"
JOURNAL_FIELDS = (
    "source_receipts",
    "observations",
    "reasoning_updates",
    "mechanism_updates",
    "uncertainty_updates",
    "claim_updates",
    "claim_ceiling_updates",
    "route_decisions",
    "decision_updates",
)
TRANSITIONS = {"continue", "refine", "switch", "reframe", "stop"}
ACCESS_STATES = {"searched-positive", "searched-negative", "inaccessible"}
W1 = "equities/comparable-state-reconstruction/v0"
W2 = "equities/aggregate-driver-attribution/v0"
W1_FIELDS = {
    "schema_version",
    "workbench",
    "status",
    "claim_ceiling",
    "source_receipt_ids",
    "observation_ids",
    "comparable_fact_set",
    "refusal",
}
W2_FIELDS = {
    "schema_version",
    "workbench",
    "status",
    "claim_ceiling",
    "source_receipt_ids",
    "observation_ids",
    "upstream",
    "identity",
    "refusal",
}


class ResearchStateRejected(ValueError):
    pass


def _json_object(content: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResearchStateRejected(f"{label} is malformed") from exc
    if not isinstance(value, dict):
        raise ResearchStateRejected(f"{label} must be a JSON object")
    return value


def _keys(value: object, required: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != required:
        raise ResearchStateRejected(f"{label} has the wrong contract shape")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResearchStateRejected(f"{label} is required")
    return value


def _list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise ResearchStateRejected(f"{label} must be a list")
    return value


def _journal(value: object) -> dict[str, list[object]]:
    row = _keys(value, set(JOURNAL_FIELDS), "research journal")
    return {key: _list(row[key], key) for key in JOURNAL_FIELDS}


def _validate_receipts(
    rows: list[object], *, cutoff: date
) -> dict[str, str]:
    receipt_states: dict[str, str] = {}
    fields = {
        "receipt_id",
        "source_name",
        "source_kind",
        "source_origin",
        "url_or_path",
        "locator",
        "published_at",
        "as_of",
        "exact_passage",
        "access_state",
    }
    for value in rows:
        row = _keys(value, fields, "source receipt")
        receipt_id = _text(row["receipt_id"], "receipt id")
        if receipt_id in receipt_states:
            raise ResearchStateRejected("source receipt identity is duplicated")
        for key in fields - {
            "receipt_id",
            "published_at",
            "as_of",
            "exact_passage",
            "access_state",
        }:
            _text(row[key], f"source receipt {key}")
        access_state = _text(row["access_state"], "source receipt access state")
        if access_state not in ACCESS_STATES:
            raise ResearchStateRejected("source receipt access state is unknown")
        passage = row["exact_passage"]
        if (
            not isinstance(passage, str)
            or (access_state == "searched-positive" and not passage.strip())
            or (access_state != "searched-positive" and passage.strip())
        ):
            raise ResearchStateRejected("source receipt passage contradicts access state")
        try:
            as_of = date.fromisoformat(_text(row["as_of"], "as_of"))
            published_at = (
                date.fromisoformat(_text(row["published_at"], "published_at"))
                if row["published_at"] is not None
                else None
            )
        except ValueError as exc:
            raise ResearchStateRejected("source receipt date is malformed") from exc
        if access_state == "searched-positive" and published_at is None:
            raise ResearchStateRejected("positive source receipt lacks publication date")
        if (
            (published_at is not None and published_at > cutoff)
            or as_of > cutoff
        ):
            raise ResearchStateRejected("source receipt exceeds the evidence cutoff")
        receipt_states[receipt_id] = access_state
    return receipt_states


def _validate_observations(
    rows: list[object], receipt_states: dict[str, str]
) -> set[str]:
    observation_ids: set[str] = set()
    fields = {
        "observation_id",
        "statement",
        "authority",
        "source_receipt_ids",
        "payload",
    }
    for value in rows:
        row = _keys(value, fields, "observation")
        observation_id = _text(row["observation_id"], "observation id")
        if observation_id in observation_ids:
            raise ResearchStateRejected("observation identity is duplicated")
        observation_ids.add(observation_id)
        _text(row["statement"], "observation statement")
        _text(row["authority"], "observation authority")
        used = _list(row["source_receipt_ids"], "observation source receipts")
        if not used or any(
            item not in receipt_states
            or receipt_states[item] != "searched-positive"
            for item in used
        ):
            raise ResearchStateRejected("observation lacks exact source-receipt custody")
        if not isinstance(row["payload"], dict):
            raise ResearchStateRejected("observation payload must be a JSON object")
    return observation_ids


def _validate_reasoning(
    rows: list[object], selected_operators: set[str]
) -> None:
    fields = {
        "operator",
        "failure_tested",
        "realized_delta",
        "kill_result",
    }
    observed: set[str] = set()
    for value in rows:
        row = _keys(value, fields, "reasoning update")
        operator = _text(row["operator"], "reasoning operator")
        if operator not in selected_operators or operator in observed:
            raise ResearchStateRejected("reasoning update was not director-authorized")
        observed.add(operator)
        for key in fields - {"operator"}:
            _text(row[key], f"reasoning update {key}")
    if observed != selected_operators:
        raise ResearchStateRejected("selected reasoning operator has no exact result")


def _validate_status_updates(
    rows: list[object],
    *,
    kind: str,
    id_key: str,
    stable_key: str,
    observation_ids: set[str],
) -> dict[str, dict[str, object]]:
    fields = {
        id_key,
        stable_key,
        "from_status",
        "to_status",
        "because_observation_ids",
        (
            "missing_discriminator"
            if kind == "mechanism"
            else "next_discriminator"
            if kind == "uncertainty"
            else "allowed_language"
        ),
    }
    if kind == "claim":
        fields.add("forbidden_language")
    current: dict[str, dict[str, object]] = {}
    for value in rows:
        row = _keys(value, fields, f"{kind} update")
        identity = _text(row[id_key], f"{kind} id")
        stable = _text(row[stable_key], f"{kind} {stable_key}")
        previous = current.get(identity)
        expected_from = previous["to_status"] if previous else "unassessed"
        if row["from_status"] != expected_from:
            raise ResearchStateRejected(f"{kind} history does not reconcile")
        if previous and previous[stable_key] != stable:
            raise ResearchStateRejected(f"{kind} identity changed meaning")
        _text(row["to_status"], f"{kind} status")
        evidence = _list(
            row["because_observation_ids"], f"{kind} observation references"
        )
        if any(item not in observation_ids for item in evidence):
            raise ResearchStateRejected(f"{kind} update cites a missing observation")
        for key in fields - {
            id_key,
            stable_key,
            "from_status",
            "to_status",
            "because_observation_ids",
        }:
            _text(row[key], f"{kind} {key}")
        current[identity] = row
    return current


def _validate_routes(
    rows: list[object], uncertainty_ids: set[str]
) -> None:
    fields = {
        "route_id",
        "transition",
        "target_uncertainty_id",
        "rationale",
        "next_step",
        "kill_condition",
    }
    for value in rows:
        row = _keys(value, fields, "route decision")
        for key in fields:
            _text(row[key], f"route {key}")
        if row["transition"] not in TRANSITIONS:
            raise ResearchStateRejected("route transition is unknown")
        if row["target_uncertainty_id"] not in uncertainty_ids:
            raise ResearchStateRejected("route targets a missing uncertainty")


def _validate_decisions(rows: list[object]) -> None:
    fields = {
        "changed",
        "consequence",
        "no_action_condition",
        "authority_required",
    }
    for value in rows:
        row = _keys(value, fields, "decision update")
        if not isinstance(row["changed"], bool):
            raise ResearchStateRejected("decision changed flag must be boolean")
        for key in fields - {"changed"}:
            _text(row[key], f"decision {key}")


def _validate_claim_ceilings(
    rows: list[object], *, order: WorkOrder, parent_length: int
) -> None:
    fields = {"work_order_id", "workbench", "claim_ceiling"}
    for value in rows:
        row = _keys(value, fields, "claim-ceiling update")
        _text(row["work_order_id"], "claim-ceiling work order")
        _text(row["claim_ceiling"], "claim ceiling")
        if not isinstance(row["workbench"], dict):
            raise ResearchStateRejected("claim-ceiling workbench is malformed")
    appended = rows[parent_length:]
    expected = {
        "work_order_id": str(order.pk),
        "workbench": order.proposal.contract["workbenches"][0],
        "claim_ceiling": order.proposal.contract["claim_ceiling"],
    }
    if appended != [expected]:
        raise ResearchStateRejected("research state lost exact claim-ceiling history")


def _validate_workbench_result(
    order: WorkOrder,
    *,
    content: bytes,
    receipt_states: dict[str, str],
    observation_ids: set[str],
) -> dict[str, object]:
    result = _json_object(content, "workbench result")
    selected = order.proposal.contract["workbenches"][0]
    workbench_id = selected["workbench_id"]
    if workbench_id == W1:
        try:
            row = _keys(
                result,
                W1_FIELDS,
                "W1 workbench result",
            )
        except ResearchStateRejected as exc:
            raise ResearchStateRejected("W1 workbench result is malformed") from exc
        if (
            row["schema_version"] != "research-state-patch/v0"
            or row["workbench"] != selected
            or row["claim_ceiling"] != order.proposal.contract["claim_ceiling"]
            or row["status"]
            not in {"COMPARABLE", "INCOMPARABLE", "UNRECONCILED", "REJECTED"}
        ):
            raise ResearchStateRejected("W1 workbench result is malformed")
        receipts = _list(row["source_receipt_ids"], "W1 source receipts")
        observations = _list(row["observation_ids"], "W1 observations")
        if (
            not receipts
            or not observations
            or any(
                item not in receipt_states
                or receipt_states[item] != "searched-positive"
                for item in receipts
            )
            or any(item not in observation_ids for item in observations)
        ):
            raise ResearchStateRejected("W1 workbench result is detached from state")
        if row["status"] == "COMPARABLE":
            fact = _keys(
                row["comparable_fact_set"],
                {
                    "authority",
                    "original_fact_observation_id",
                    "issuer_assertion_observation_id",
                    "bridge_observation_id",
                    "derived_observation_id",
                    "residual",
                },
                "W1 comparable fact set",
            )
            if (
                row["refusal"] is not None
                or fact["authority"]
                not in {"reported", "issuer_recast", "analyst_assumption"}
                or _text(fact["residual"], "W1 residual") != "0"
                or any(
                    fact[key] not in observations
                    for key in {
                        "original_fact_observation_id",
                        "derived_observation_id",
                    }
                )
            ):
                raise ResearchStateRejected("W1 comparable fact set is invalid")
            if fact["authority"] == "issuer_recast" and any(
                fact[key] not in observations
                for key in {
                    "issuer_assertion_observation_id",
                    "bridge_observation_id",
                }
            ):
                raise ResearchStateRejected("W1 issuer recast lost its authority")
        elif row["comparable_fact_set"] is not None or not isinstance(
            row["refusal"], str
        ) or not row["refusal"].strip():
            raise ResearchStateRejected("W1 refusal is malformed")
    elif workbench_id == W2:
        try:
            row = _keys(result, W2_FIELDS, "W2 workbench result")
        except ResearchStateRejected as exc:
            raise ResearchStateRejected("W2 workbench result is malformed") from exc
        if (
            row["schema_version"] != "driver-state-patch/v0"
            or row["workbench"] != selected
            or row["claim_ceiling"] != order.proposal.contract["claim_ceiling"]
            or row["status"]
            not in {
                "IDENTITY_TIED",
                "UNDERIDENTIFIED",
                "UNDECOMPOSABLE",
                "REJECTED",
            }
        ):
            raise ResearchStateRejected("W2 workbench result is malformed")
        receipts = _list(row["source_receipt_ids"], "W2 source receipts")
        observations = _list(row["observation_ids"], "W2 observations")
        if (
            not receipts
            or not observations
            or any(
                item not in receipt_states
                or receipt_states[item] != "searched-positive"
                for item in receipts
            )
            or any(item not in observation_ids for item in observations)
        ):
            raise ResearchStateRejected("W2 workbench result is detached from state")
        parent = order.input_state
        if parent is None:
            raise ResearchStateRejected("W2 lacks its exact W1 state")
        try:
            parent_artifact = parent.workbench_artifact
            parent_result = _json_object(
                bytes(parent_artifact.content), "W1 workbench result"
            )
            parent_fact = _keys(
                parent_result["comparable_fact_set"],
                {
                    "authority",
                    "original_fact_observation_id",
                    "issuer_assertion_observation_id",
                    "bridge_observation_id",
                    "derived_observation_id",
                    "residual",
                },
                "W1 comparable fact set",
            )
        except (ResearchStateRejected, KeyError, TypeError) as exc:
            raise ResearchStateRejected("W2 upstream W1 result is unavailable") from exc
        upstream = _keys(
            row["upstream"],
            {
                "state_sha256",
                "workbench_result_sha256",
                "status",
                "original_fact_observation_id",
                "issuer_assertion_observation_id",
                "bridge_observation_id",
                "derived_observation_id",
            },
            "W2 upstream authority",
        )
        expected_upstream = {
            "state_sha256": parent.state_artifact.digest,
            "workbench_result_sha256": parent_artifact.digest,
            "status": parent_result.get("status"),
            **{
                key: parent_fact[key]
                for key in {
                    "original_fact_observation_id",
                    "issuer_assertion_observation_id",
                    "bridge_observation_id",
                    "derived_observation_id",
                }
            },
        }
        if (
            parent_result.get("status") != "COMPARABLE"
            or upstream != expected_upstream
            or any(
                upstream[key] not in observations
                for key in {
                    "original_fact_observation_id",
                    "derived_observation_id",
                }
            )
            or (
                parent_fact["authority"] == "issuer_recast"
                and any(
                    upstream[key] not in observations
                    for key in {
                        "issuer_assertion_observation_id",
                        "bridge_observation_id",
                    }
                )
            )
        ):
            raise ResearchStateRejected("W2 upstream authority does not reproduce")
        identity = _keys(
            row["identity"],
            {
                "method",
                "unit_volume",
                "price_mix",
                "interaction",
                "residual",
            },
            "W2 driver identity",
        )
        if (
            identity["method"] not in {"two_factor_pvm", "disclosed_bridge"}
            or any(
                not isinstance(identity[key], str) or not identity[key].strip()
                for key in {
                    "unit_volume",
                    "price_mix",
                    "interaction",
                    "residual",
                }
            )
            or (
                row["status"] == "IDENTITY_TIED"
                and identity["residual"] != "0"
            )
            or (
                row["status"] == "IDENTITY_TIED"
                and row["refusal"] is not None
            )
        ):
            raise ResearchStateRejected("W2 driver identity is invalid")
    return result


def validate_transition(
    order: WorkOrder,
    *,
    workbench_content: bytes,
    state_content: bytes,
    delta_content: bytes,
) -> tuple[dict[str, object], dict[str, object]]:
    workbench_id = order.proposal.contract["workbenches"][0]["workbench_id"]
    if workbench_id in {W1, W2}:
        try:
            _keys(
                _json_object(workbench_content, "workbench result"),
                W1_FIELDS if workbench_id == W1 else W2_FIELDS,
                "workbench result",
            )
        except ResearchStateRejected as exc:
            label = "W1" if workbench_id == W1 else "W2"
            raise ResearchStateRejected(
                f"{label} workbench result is malformed"
            ) from exc
    state = _json_object(state_content, "research state")
    _keys(
        state,
        {
            "schema_version",
            "campaign_id",
            "work_order_id",
            "parent_state_sha256",
            "workbench_result_sha256",
            "decision_hinge",
            "work_order_claim_ceiling",
            "evidence_cutoff",
            "produced_by",
            "journal",
        },
        "research state",
    )
    if (
        state["schema_version"] != SCHEMA
        or state["campaign_id"] != str(order.campaign_id)
        or state["work_order_id"] != str(order.pk)
        or state["workbench_result_sha256"]
        != sha256(workbench_content).hexdigest()
        or state["evidence_cutoff"] != order.campaign.evidence_cutoff.isoformat()
        or state["decision_hinge"] != order.proposal.contract["decision_hinge"]
        or state["work_order_claim_ceiling"]
        != order.proposal.contract["claim_ceiling"]
    ):
        raise ResearchStateRejected("research state does not match its work order")
    _text(state["decision_hinge"], "decision hinge")
    _text(state["work_order_claim_ceiling"], "claim ceiling")
    workbenches = order.proposal.contract.get("workbenches", [])
    if len(workbenches) != 1 or state["produced_by"] != workbenches[0]:
        raise ResearchStateRejected("research state names the wrong workbench")
    parent = order.input_state
    expected_parent = parent.state_artifact.digest if parent else None
    if state["parent_state_sha256"] != expected_parent:
        raise ResearchStateRejected("research state names the wrong parent")

    journal = _journal(state["journal"])
    parent_state = (
        _json_object(bytes(parent.state_artifact.content), "parent state")
        if parent
        else None
    )
    if parent_state and parent_state["decision_hinge"] != state["decision_hinge"]:
        raise ResearchStateRejected("research state changed the decision hinge")
    parent_journal = (
        _journal(parent_state["journal"])
        if parent_state
        else {key: [] for key in JOURNAL_FIELDS}
    )
    for key in JOURNAL_FIELDS:
        if journal[key][: len(parent_journal[key])] != parent_journal[key]:
            raise ResearchStateRejected("research state dropped accepted history")
    if any(not journal[key] for key in (
        "source_receipts",
        "observations",
        "mechanism_updates",
        "uncertainty_updates",
        "claim_updates",
        "claim_ceiling_updates",
        "route_decisions",
        "decision_updates",
    )):
        raise ResearchStateRejected("research state is not decision-complete")
    receipts = _validate_receipts(
        journal["source_receipts"], cutoff=order.campaign.evidence_cutoff
    )
    observations = _validate_observations(journal["observations"], receipts)
    _validate_workbench_result(
        order,
        content=workbench_content,
        receipt_states=receipts,
        observation_ids=observations,
    )
    selected_operators = {
        item.get("name")
        for item in order.proposal.contract.get("reasoning_operators", [])
        if isinstance(item, dict)
    }
    _validate_reasoning(
        journal["reasoning_updates"][len(parent_journal["reasoning_updates"]) :],
        selected_operators,
    )
    mechanisms = _validate_status_updates(
        journal["mechanism_updates"],
        kind="mechanism",
        id_key="mechanism_id",
        stable_key="label",
        observation_ids=observations,
    )
    if len(mechanisms) < 2:
        raise ResearchStateRejected("research state collapsed its rival mechanisms")
    uncertainties = _validate_status_updates(
        journal["uncertainty_updates"],
        kind="uncertainty",
        id_key="uncertainty_id",
        stable_key="question",
        observation_ids=observations,
    )
    _validate_status_updates(
        journal["claim_updates"],
        kind="claim",
        id_key="claim_id",
        stable_key="text",
        observation_ids=observations,
    )
    _validate_claim_ceilings(
        journal["claim_ceiling_updates"],
        order=order,
        parent_length=len(parent_journal["claim_ceiling_updates"]),
    )
    _validate_routes(journal["route_decisions"], set(uncertainties))
    _validate_decisions(journal["decision_updates"])

    delta = _json_object(delta_content, "epistemic delta")
    _keys(
        delta,
        {
            "schema_version",
            "campaign_id",
            "work_order_id",
            "parent_state_sha256",
            "after_state_sha256",
            "summary",
            "appended",
        },
        "epistemic delta",
    )
    if (
        delta["schema_version"] != DELTA_SCHEMA
        or delta["campaign_id"] != str(order.campaign_id)
        or delta["work_order_id"] != str(order.pk)
        or delta["parent_state_sha256"] != expected_parent
        or delta["after_state_sha256"] != sha256(state_content).hexdigest()
    ):
        raise ResearchStateRejected("epistemic delta does not bind exact state")
    appended = _journal(delta["appended"])
    expected_appended = {
        key: journal[key][len(parent_journal[key]) :] for key in JOURNAL_FIELDS
    }
    if appended != expected_appended:
        raise ResearchStateRejected("epistemic delta does not reconcile")
    if not any(appended.values()) or not appended["decision_updates"]:
        raise ResearchStateRejected("epistemic delta records no consequential change")
    if delta["summary"] != appended["decision_updates"][-1]["consequence"]:
        raise ResearchStateRejected("epistemic delta summary is not exact")
    return state, delta


def project_transition(transition: ResearchStateTransition) -> dict[str, object]:
    state = json.loads(bytes(transition.state_artifact.content))
    delta = json.loads(bytes(transition.delta_artifact.content))
    journal = state["journal"]

    def latest(rows: list[dict[str, object]], key: str) -> list[dict[str, object]]:
        values: dict[str, dict[str, object]] = {}
        for row in rows:
            values[row[key]] = row
        return list(values.values())

    disposition = getattr(transition, "disposition", None)
    return {
        "transition": transition,
        "state": disposition.kind if disposition else "awaiting director",
        "decision_hinge": state["decision_hinge"],
        "delta_summary": delta["summary"],
        "source_changes": delta["appended"]["source_receipts"],
        "observation_changes": delta["appended"]["observations"],
        "reasoning_changes": delta["appended"]["reasoning_updates"],
        "claim_ceiling": state["work_order_claim_ceiling"],
        "mechanisms": latest(journal["mechanism_updates"], "mechanism_id"),
        "uncertainties": latest(journal["uncertainty_updates"], "uncertainty_id"),
        "claims": latest(journal["claim_updates"], "claim_id"),
        "route": journal["route_decisions"][-1],
        "decision": journal["decision_updates"][-1],
    }
