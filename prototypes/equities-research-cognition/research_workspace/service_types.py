from dataclasses import dataclass


@dataclass(frozen=True)
class RunOutcome:
    run_id: str
    result_id: str
    claim_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    memory_proposal_ids: tuple[str, ...]
