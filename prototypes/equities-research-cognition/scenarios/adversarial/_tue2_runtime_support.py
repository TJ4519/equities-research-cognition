from __future__ import annotations

from product.campaign.models import WorkOrder


def tracked_send_response(
    order: WorkOrder,
    pane: str = "2",
) -> dict[str, object]:
    return {
        "success": True,
        "send": {
            "success": True,
            "session": order.campaign.ntm_session,
            "blocked": False,
            "targets": [pane],
            "successful": [pane],
            "failed": [],
        },
        "ack": {
            "success": True,
            "session": order.campaign.ntm_session,
            "confirmations": [
                {"pane": pane, "ack_type": "output_started"}
            ],
            "pending": [],
            "failed": [],
            "timed_out": False,
        },
    }
