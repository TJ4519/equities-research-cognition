from __future__ import annotations

from .service_base import BaseServiceMixin
from .service_context import ContextServiceMixin
from .service_decisions import DecisionServiceMixin
from .service_evidence import EvidenceServiceMixin
from .service_run import RunServiceMixin
from .service_types import RunOutcome


class ResearchWorkspace(
    RunServiceMixin,
    ContextServiceMixin,
    EvidenceServiceMixin,
    DecisionServiceMixin,
    BaseServiceMixin,
):
    """Joined service for the local research workspace."""


__all__ = ["ResearchWorkspace", "RunOutcome"]
