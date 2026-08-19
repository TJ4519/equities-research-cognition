from __future__ import annotations

from .service_base import BaseServiceMixin
from .service_branch_authority import AcknowledgedBranchAuthorityMixin
from .service_branches import BranchServiceMixin
from .service_context import ContextServiceMixin
from .service_decisions import DecisionServiceMixin
from .service_evidence import EvidenceServiceMixin
from .service_run import RunServiceMixin
from .service_types import BranchLaunchOutcome, BranchResultOutcome, RunOutcome


class ResearchWorkspace(
    AcknowledgedBranchAuthorityMixin,
    BranchServiceMixin,
    RunServiceMixin,
    ContextServiceMixin,
    EvidenceServiceMixin,
    DecisionServiceMixin,
    BaseServiceMixin,
):
    """Joined service for the local research workspace."""


__all__ = [
    "ResearchWorkspace",
    "RunOutcome",
    "BranchLaunchOutcome",
    "BranchResultOutcome",
]
