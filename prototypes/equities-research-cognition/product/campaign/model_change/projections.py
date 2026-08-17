from __future__ import annotations

from product.campaign.models import ObjectDisposition


def episode_page(state: dict[str, object]) -> dict[str, object]:
    episode = state["episode"]
    current_object = state["current_object"]
    authorities = state["object_authorities"]
    decision = state["decision"]
    calculation = state["calculation"]
    disposition = state["disposition"]
    actions = {item.action for item in authorities}
    history = []
    for item in state["history"]["objects"]:
        history.append(
            {
                "when": item.created_at,
                "summary": "The bounded target meaning was recorded.",
            }
        )
    for item in state["history"]["decisions"]:
        summary = (
            "The proposed source did not satisfy the annual-target source rule."
            if item.reason_code == "BLOCK_WRONG_DOCUMENT_CLASS"
            else "The proposed change passed the bounded checks."
            if item.outcome == "PASS"
            else "The proposed change did not pass the bounded checks."
        )
        history.append({"when": item.created_at, "summary": summary})
    for item in state["history"]["amendments"]:
        history.append(
            {
                "when": item.created_at,
                "summary": "An attributed correction was appended; earlier facts were retained.",
            }
        )
    for item in state["history"]["dispositions"]:
        history.append(
            {
                "when": item.created_at,
                "summary": f"Candidate review recorded: {item.get_kind_display()}.",
            }
        )
    history.sort(key=lambda row: row["when"])
    return {
        "job": state["job"],
        "episode": episode,
        "original": episode.starting_artifact,
        "object": current_object,
        "meaning_confirmed": ObjectDisposition.Action.CONFIRM_MEANING in actions,
        "method_authorized": ObjectDisposition.Action.AUTHORIZE_METHOD in actions,
        "work_authorized": state["work_order"] is not None,
        "source_exception": decision
        if decision and decision.reason_code == "BLOCK_WRONG_DOCUMENT_CLASS"
        else None,
        "candidate": state["candidate"],
        "calculation": calculation,
        "consequences": calculation.consequences if calculation else [],
        "disposition": disposition,
        "history": history,
    }
