from __future__ import annotations

from .branch_workspace import attempt_paths, read_outbox_json
from .errors import AuthorityError, RuntimeFailure, ValidationError


class PersistentBranchPolicyMixin:
    """Guard the active NTM attempt before canonical branch state changes."""

    def _require_active_binding(self, branch_id: str, binding_id: str) -> None:
        latest = self._latest_binding(branch_id)
        if latest is None or latest.id != binding_id:
            raise AuthorityError(
                "only the latest NTM binding may advance or complete this research branch"
            )

    def collect_branch_acknowledgement(
        self,
        *,
        branch_id: str,
        binding_id: str,
        instruction_id: str,
    ):
        self._require_active_binding(branch_id, binding_id)
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        instruction = self._require_kind(instruction_id, "branch_instruction")
        if instruction.payload["binding_id"] != binding_id:
            raise ValidationError("instruction belongs to another NTM binding")
        paths = attempt_paths(self.store, branch.id, binding.id)
        payload = read_outbox_json(
            paths,
            f"acknowledgement-{instruction.id}.json",
            "branch acknowledgement",
        )
        worker = payload.get("worker")
        if not isinstance(worker, dict):
            raise RuntimeFailure("branch acknowledgement lacks worker identity")
        if worker.get("provider") != "codex":
            raise RuntimeFailure("branch acknowledgement is not from Codex")
        if worker.get("model") != binding.payload["model"]:
            raise RuntimeFailure("branch acknowledgement names the wrong Codex model")
        if worker.get("role") != binding.payload["role_name"]:
            raise RuntimeFailure("branch acknowledgement names the wrong research role")
        return super().collect_branch_acknowledgement(
            branch_id=branch_id,
            binding_id=binding_id,
            instruction_id=instruction_id,
        )

    def collect_branch_source_request(self, *, branch_id: str, binding_id: str, relative_path: str):
        self._require_active_binding(branch_id, binding_id)
        return super().collect_branch_source_request(
            branch_id=branch_id,
            binding_id=binding_id,
            relative_path=relative_path,
        )

    def collect_branch_checkpoint(self, *, branch_id: str, binding_id: str, relative_path: str):
        self._require_active_binding(branch_id, binding_id)
        return super().collect_branch_checkpoint(
            branch_id=branch_id,
            binding_id=binding_id,
            relative_path=relative_path,
        )

    def attach_branch_context_delta(self, *, branch_id: str, binding_id: str, **kwargs):
        self._require_active_binding(branch_id, binding_id)
        return super().attach_branch_context_delta(
            branch_id=branch_id,
            binding_id=binding_id,
            **kwargs,
        )

    def send_branch_instruction(self, *, branch_id: str, binding_id: str, **kwargs):
        self._require_active_binding(branch_id, binding_id)
        return super().send_branch_instruction(
            branch_id=branch_id,
            binding_id=binding_id,
            **kwargs,
        )

    def observe_branch_status(self, *, branch_id: str, binding_id: str, **kwargs):
        self._require_active_binding(branch_id, binding_id)
        return super().observe_branch_status(
            branch_id=branch_id,
            binding_id=binding_id,
            **kwargs,
        )

    def observe_branch_completion(self, *, branch_id: str, binding_id: str, **kwargs):
        self._require_active_binding(branch_id, binding_id)
        return super().observe_branch_completion(
            branch_id=branch_id,
            binding_id=binding_id,
            **kwargs,
        )

    def collect_branch_result(self, *, branch_id: str, binding_id: str):
        self._require_active_binding(branch_id, binding_id)
        return super().collect_branch_result(
            branch_id=branch_id,
            binding_id=binding_id,
        )
