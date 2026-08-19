from dataclasses import dataclass


@dataclass(frozen=True)
class RunOutcome:
    run_id: str
    result_id: str
    claim_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    memory_proposal_ids: tuple[str, ...]


@dataclass(frozen=True)
class BranchLaunchOutcome:
    branch_id: str
    binding_id: str
    instruction_id: str
    session: str
    pane: int


@dataclass(frozen=True)
class BranchResultOutcome:
    branch_id: str
    binding_id: str
    checkpoint_id: str
    run_id: str
    result_id: str
    claim_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    memory_proposal_ids: tuple[str, ...]
