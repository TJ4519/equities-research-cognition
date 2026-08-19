from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .codex_session import build_codex_session_control, verify_codex_session_control
from .errors import IntegrityError
from .ntm_research import NtmControl


class MachineOwnedCodexLaunchMixin:
    """Generate and verify the Codex launch used by every NTM binding."""

    def _search_enabled_for_branch(self, branch_id: str) -> bool:
        contexts = [
            self._require_kind(context_id, "context")
            for context_id in self._branch_context_ids(branch_id)
        ]
        kinds = {
            context.payload.get("context_kind", "support")
            for context in contexts
        }
        requested = any(
            "codex_search" in context.payload.get("allowed_tools", [])
            for context in contexts
        )
        if requested and kinds != {"discovery"}:
            raise IntegrityError(
                "Codex search may be granted only to a pure discovery branch"
            )
        return requested

    def _binding_control(self, binding_id: str):
        binding = self._require_kind(binding_id, "ntm_binding")
        events = [
            self._require_kind(relation.object_id, "branch_event")
            for relation in self.store.relations_from(binding_id, "has_event")
        ]
        controls = [
            event
            for event in events
            if event.payload["event_kind"] == "codex_launch_bound"
        ]
        if len(controls) != 1:
            raise IntegrityError("NTM binding lacks one exact Codex launch record")
        control = verify_codex_session_control(controls[0].payload["details"])
        if control is None:
            raise IntegrityError("Codex launch verification returned no control")
        if binding.payload["model"] != control.model:
            raise IntegrityError("NTM binding model disagrees with its Codex launch")
        if binding.payload["config_path"] != control.ntm_config_path:
            raise IntegrityError("NTM binding config path disagrees with its Codex launch")
        if binding.payload["config_digest"] != control.ntm_config_digest:
            raise IntegrityError("NTM binding config digest disagrees with its Codex launch")
        expected_search = self._search_enabled_for_branch(binding.payload["branch_id"])
        if control.search_enabled != expected_search:
            raise IntegrityError("Codex launch search policy no longer matches the branch")
        return control

    def launch_research_branch(
        self,
        *,
        branch_id: str,
        controller: NtmControl,
        codex_binary: Path,
        model: str,
        role_name: str,
        actor: str,
        session: str | None = None,
        pane: int = 1,
        environment: Mapping[str, str] | None = None,
        resume_checkpoint_id: str | None = None,
    ):
        control = build_codex_session_control(
            self.store,
            codex_binary=codex_binary,
            model=model,
            search_enabled=self._search_enabled_for_branch(branch_id),
        )
        outcome = super().launch_research_branch(
            branch_id=branch_id,
            controller=controller,
            config=Path(control.ntm_config_path),
            model=control.model,
            role_name=role_name,
            actor=actor,
            session=session,
            pane=pane,
            environment=environment,
            resume_checkpoint_id=resume_checkpoint_id,
        )
        self._store_ntm_event(
            branch_id=branch_id,
            binding_id=outcome.binding_id,
            event_kind="codex_launch_bound",
            actor="system:host",
            details=control.payload(),
        )
        self._binding_control(outcome.binding_id)
        return outcome

    def collect_branch_acknowledgement(self, *, branch_id: str, binding_id: str, instruction_id: str):
        self._binding_control(binding_id)
        return super().collect_branch_acknowledgement(
            branch_id=branch_id,
            binding_id=binding_id,
            instruction_id=instruction_id,
        )

    def send_branch_instruction(self, *, branch_id: str, binding_id: str, controller: NtmControl, **kwargs):
        control = self._binding_control(binding_id)
        return super().send_branch_instruction(
            branch_id=branch_id,
            binding_id=binding_id,
            controller=controller,
            config=Path(control.ntm_config_path),
            **kwargs,
        )

    def attach_branch_context_delta(self, *, branch_id: str, binding_id: str, controller: NtmControl, **kwargs):
        control = self._binding_control(binding_id)
        return super().attach_branch_context_delta(
            branch_id=branch_id,
            binding_id=binding_id,
            controller=controller,
            config=Path(control.ntm_config_path),
            **kwargs,
        )

    def observe_branch_status(self, *, branch_id: str, binding_id: str, controller: NtmControl, **kwargs):
        control = self._binding_control(binding_id)
        return super().observe_branch_status(
            branch_id=branch_id,
            binding_id=binding_id,
            controller=controller,
            config=Path(control.ntm_config_path),
            **kwargs,
        )

    def observe_branch_completion(self, *, branch_id: str, binding_id: str, controller: NtmControl, **kwargs):
        control = self._binding_control(binding_id)
        return super().observe_branch_completion(
            branch_id=branch_id,
            binding_id=binding_id,
            controller=controller,
            config=Path(control.ntm_config_path),
            **kwargs,
        )

    def stop_research_branch(self, *, branch_id: str, binding_id: str, controller: NtmControl, **kwargs):
        control = self._binding_control(binding_id)
        return super().stop_research_branch(
            branch_id=branch_id,
            binding_id=binding_id,
            controller=controller,
            config=Path(control.ntm_config_path),
            **kwargs,
        )

    def collect_branch_checkpoint(self, *, branch_id: str, binding_id: str, relative_path: str):
        self._binding_control(binding_id)
        return super().collect_branch_checkpoint(
            branch_id=branch_id,
            binding_id=binding_id,
            relative_path=relative_path,
        )

    def collect_branch_source_request(self, *, branch_id: str, binding_id: str, relative_path: str):
        self._binding_control(binding_id)
        return super().collect_branch_source_request(
            branch_id=branch_id,
            binding_id=binding_id,
            relative_path=relative_path,
        )

    def collect_branch_result(self, *, branch_id: str, binding_id: str):
        self._binding_control(binding_id)
        return super().collect_branch_result(
            branch_id=branch_id,
            binding_id=binding_id,
        )
