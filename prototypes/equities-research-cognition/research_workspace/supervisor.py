from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .branch_workspace import attempt_paths
from .errors import RuntimeFailure
from .ntm_research import NtmControl
from .service import ResearchWorkspace
from .util import read_regular_file


@dataclass(frozen=True)
class SupervisionReport:
    branch_id: str
    binding_id: str
    action: str
    object_id: str | None
    instruction_id: str | None
    state: dict[str, Any]


class BranchSupervisor:
    """Advance one persistent NTM-managed branch without an operator relay.

    The supervisor never performs research. It takes custody of worker-written
    acknowledgements, source requests, checkpoints, and results. Whenever the
    host issues a new canonical identity, the supervisor sends that receipt to
    the same Codex session through NTM and waits for semantic acknowledgement.
    """

    def __init__(
        self,
        workspace: ResearchWorkspace,
        controller: NtmControl,
    ) -> None:
        self.workspace = workspace
        self.controller = controller

    def _latest_binding(self, branch_id: str):
        binding = self.workspace._latest_binding(branch_id)
        if binding is None:
            raise RuntimeFailure("research branch has no NTM binding")
        self.workspace._require_active_binding(branch_id, binding.id)
        self.workspace._binding_control(binding.id)
        return binding

    def _ack_file_exists(self, branch_id: str, binding_id: str, instruction_id: str) -> bool:
        paths = attempt_paths(self.workspace.store, branch_id, binding_id)
        path = paths.outbox / f"acknowledgement-{instruction_id}.json"
        return path.is_file() and not path.is_symlink()

    def _existing_source_external_ids(self, branch_id: str) -> set[str]:
        result: set[str] = set()
        for relation in self.workspace.store.relations_from(branch_id, "has_source_request"):
            item = self.workspace._require_kind(relation.object_id, "source_request")
            result.add(item.payload["external_request_id"])
        return result

    def _send_receipt(
        self,
        *,
        branch_id: str,
        binding_id: str,
        instruction_kind: str,
        text: str,
        checkpoint_id: str | None = None,
    ):
        return self.workspace.send_branch_instruction(
            branch_id=branch_id,
            binding_id=binding_id,
            controller=self.controller,
            instruction_kind=instruction_kind,
            actor="system:branch-supervisor",
            instruction_text=text,
            context_ids=[],
            checkpoint_id=checkpoint_id,
        )

    def step(self, branch_id: str) -> SupervisionReport:
        binding = self._latest_binding(branch_id)
        branch_state = self.workspace.branch_state(branch_id)
        if branch_state["state"] == "completed":
            return SupervisionReport(
                branch_id=branch_id,
                binding_id=binding.id,
                action="already_completed",
                object_id=branch_state["result_id"],
                instruction_id=None,
                state=branch_state,
            )

        latest_instruction = self.workspace._latest_instruction(binding.id)
        if latest_instruction is None:
            raise RuntimeFailure("bound NTM session has no branch instruction")
        acknowledgement = self.workspace._instruction_ack(latest_instruction.id)
        if acknowledgement is None:
            if not self._ack_file_exists(branch_id, binding.id, latest_instruction.id):
                self.workspace.observe_branch_status(
                    branch_id=branch_id,
                    binding_id=binding.id,
                    controller=self.controller,
                )
                return SupervisionReport(
                    branch_id=branch_id,
                    binding_id=binding.id,
                    action="waiting_for_acknowledgement",
                    object_id=None,
                    instruction_id=latest_instruction.id,
                    state=self.workspace.branch_state(branch_id),
                )
            acknowledgement = self.workspace.collect_branch_acknowledgement(
                branch_id=branch_id,
                binding_id=binding.id,
                instruction_id=latest_instruction.id,
            )
            return SupervisionReport(
                branch_id=branch_id,
                binding_id=binding.id,
                action="acknowledgement_collected",
                object_id=acknowledgement.id,
                instruction_id=latest_instruction.id,
                state=self.workspace.branch_state(branch_id),
            )

        paths = attempt_paths(self.workspace.store, branch_id, binding.id)
        known_external_ids = self._existing_source_external_ids(branch_id)
        for path in sorted(paths.source_requests.glob("*.json")):
            if path.is_symlink() or not path.is_file():
                continue
            payload = self.workspace._json_file(
                path,
                "pending branch source request",
                max_bytes=2 * 1024 * 1024,
            )
            external_id = payload.get("external_request_id")
            if external_id in known_external_ids:
                continue
            request = self.workspace.collect_branch_source_request(
                branch_id=branch_id,
                binding_id=binding.id,
                relative_path=path.name,
            )
            receipt = self._send_receipt(
                branch_id=branch_id,
                binding_id=binding.id,
                instruction_kind="steer",
                text=(
                    "The host collected your source request. Use host source_request_id "
                    f"{request.id} for external_request_id "
                    f"{request.payload['external_request_id']} in later checkpoints. "
                    "Acknowledge this exact receipt before continuing."
                ),
            )
            return SupervisionReport(
                branch_id=branch_id,
                binding_id=binding.id,
                action="source_request_collected",
                object_id=request.id,
                instruction_id=receipt.id,
                state=self.workspace.branch_state(branch_id),
            )

        latest_checkpoint = self.workspace._latest_checkpoint(branch_id)
        next_sequence = 1 if latest_checkpoint is None else latest_checkpoint.payload["sequence"] + 1
        checkpoint_path = paths.checkpoints / f"{next_sequence:04d}.json"
        if checkpoint_path.is_file() and not checkpoint_path.is_symlink():
            checkpoint = self.workspace.collect_branch_checkpoint(
                branch_id=branch_id,
                binding_id=binding.id,
                relative_path=checkpoint_path.name,
            )
            kind = (
                "complete_request"
                if checkpoint.payload["disposition"] in {"complete", "refuse"}
                else "steer"
            )
            receipt = self._send_receipt(
                branch_id=branch_id,
                binding_id=binding.id,
                instruction_kind=kind,
                checkpoint_id=checkpoint.id,
                text=(
                    "The host collected branch checkpoint sequence "
                    f"{checkpoint.payload['sequence']} as checkpoint_id {checkpoint.id} "
                    f"with digest {checkpoint.digest}. Use this exact checkpoint_id as "
                    "the predecessor of the next checkpoint or in result.json. "
                    "Acknowledge this exact receipt before continuing."
                ),
            )
            return SupervisionReport(
                branch_id=branch_id,
                binding_id=binding.id,
                action="checkpoint_collected",
                object_id=checkpoint.id,
                instruction_id=receipt.id,
                state=self.workspace.branch_state(branch_id),
            )

        result_path = paths.outbox / "result.json"
        if result_path.is_file() and not result_path.is_symlink():
            self.workspace.observe_branch_completion(
                branch_id=branch_id,
                binding_id=binding.id,
                controller=self.controller,
            )
            outcome = self.workspace.collect_branch_result(
                branch_id=branch_id,
                binding_id=binding.id,
            )
            return SupervisionReport(
                branch_id=branch_id,
                binding_id=binding.id,
                action="result_collected",
                object_id=outcome.result_id,
                instruction_id=None,
                state=self.workspace.branch_state(branch_id),
            )

        self.workspace.observe_branch_status(
            branch_id=branch_id,
            binding_id=binding.id,
            controller=self.controller,
        )
        return SupervisionReport(
            branch_id=branch_id,
            binding_id=binding.id,
            action="waiting_for_worker_output",
            object_id=None,
            instruction_id=latest_instruction.id,
            state=self.workspace.branch_state(branch_id),
        )
