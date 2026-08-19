from __future__ import annotations

from dataclasses import dataclass
import json
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
    """Advance one persistent NTM branch without a person relaying host IDs."""

    def __init__(
        self,
        workspace: ResearchWorkspace,
        controller: NtmControl,
    ) -> None:
        self.workspace = workspace
        self.controller = controller

    @staticmethod
    def _json(path: Path, label: str) -> dict[str, Any]:
        try:
            value = json.loads(read_regular_file(path, max_bytes=2 * 1024 * 1024))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeFailure(f"{label} is not valid UTF-8 JSON") from exc
        if not isinstance(value, dict):
            raise RuntimeFailure(f"{label} must contain one JSON object")
        return value

    def _latest_binding(self, branch_id: str):
        binding = self.workspace._latest_binding(branch_id)
        if binding is None:
            raise RuntimeFailure("research branch has no NTM binding")
        self.workspace._require_active_binding(branch_id, binding.id)
        self.workspace._binding_control(binding.id)
        return binding

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
        kind: str,
        text: str,
        checkpoint_id: str | None = None,
    ):
        return self.workspace.send_branch_instruction(
            branch_id=branch_id,
            binding_id=binding_id,
            controller=self.controller,
            instruction_kind=kind,
            actor="system:branch-supervisor",
            instruction_text=text,
            context_ids=[],
            checkpoint_id=checkpoint_id,
        )

    def step(self, branch_id: str) -> SupervisionReport:
        binding = self._latest_binding(branch_id)
        state = self.workspace.branch_state(branch_id)
        if state["state"] == "completed":
            return SupervisionReport(
                branch_id,
                binding.id,
                "already_completed",
                state["result_id"],
                None,
                state,
            )

        instruction = self.workspace._latest_instruction(binding.id)
        if instruction is None:
            raise RuntimeFailure("bound NTM session has no branch instruction")
        acknowledgement = self.workspace._instruction_ack(instruction.id)
        paths = attempt_paths(self.workspace.store, branch_id, binding.id)
        if acknowledgement is None:
            path = paths.outbox / f"acknowledgement-{instruction.id}.json"
            if not path.is_file() or path.is_symlink():
                self.workspace.observe_branch_status(
                    branch_id=branch_id,
                    binding_id=binding.id,
                    controller=self.controller,
                )
                return SupervisionReport(
                    branch_id,
                    binding.id,
                    "waiting_for_acknowledgement",
                    None,
                    instruction.id,
                    self.workspace.branch_state(branch_id),
                )
            acknowledgement = self.workspace.collect_branch_acknowledgement(
                branch_id=branch_id,
                binding_id=binding.id,
                instruction_id=instruction.id,
            )
            return SupervisionReport(
                branch_id,
                binding.id,
                "acknowledgement_collected",
                acknowledgement.id,
                instruction.id,
                self.workspace.branch_state(branch_id),
            )

        known_requests = self._existing_source_external_ids(branch_id)
        for path in sorted(paths.source_requests.glob("*.json")):
            if path.is_symlink() or not path.is_file():
                continue
            payload = self._json(path, "pending source request")
            external_id = payload.get("external_request_id")
            if external_id in known_requests:
                continue
            request = self.workspace.collect_branch_source_request(
                branch_id=branch_id,
                binding_id=binding.id,
                relative_path=path.name,
            )
            receipt = self._send_receipt(
                branch_id=branch_id,
                binding_id=binding.id,
                kind="steer",
                text=(
                    "The host collected source request external_request_id "
                    f"{request.payload['external_request_id']} as source_request_id "
                    f"{request.id}. Use that exact host ID in later checkpoints. "
                    "Acknowledge this receipt before continuing."
                ),
            )
            return SupervisionReport(
                branch_id,
                binding.id,
                "source_request_collected",
                request.id,
                receipt.id,
                self.workspace.branch_state(branch_id),
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
            receipt = self._send_receipt(
                branch_id=branch_id,
                binding_id=binding.id,
                kind=(
                    "complete_request"
                    if checkpoint.payload["disposition"] in {"complete", "refuse"}
                    else "steer"
                ),
                checkpoint_id=checkpoint.id,
                text=(
                    "The host collected checkpoint sequence "
                    f"{checkpoint.payload['sequence']} as checkpoint_id {checkpoint.id} "
                    f"with digest {checkpoint.digest}. Use that ID as the next "
                    "predecessor or in result.json. Acknowledge this receipt before "
                    "continuing."
                ),
            )
            return SupervisionReport(
                branch_id,
                binding.id,
                "checkpoint_collected",
                checkpoint.id,
                receipt.id,
                self.workspace.branch_state(branch_id),
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
                branch_id,
                binding.id,
                "result_collected",
                outcome.result_id,
                None,
                self.workspace.branch_state(branch_id),
            )

        self.workspace.observe_branch_status(
            branch_id=branch_id,
            binding_id=binding.id,
            controller=self.controller,
        )
        return SupervisionReport(
            branch_id,
            binding.id,
            "waiting_for_worker_output",
            None,
            instruction.id,
            self.workspace.branch_state(branch_id),
        )
