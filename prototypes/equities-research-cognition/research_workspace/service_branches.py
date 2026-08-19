from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Mapping

from .branch_contract import (
    BRANCH_KINDS,
    INSTRUCTION_KINDS,
    validate_acknowledgement,
    validate_branch_result,
    validate_checkpoint,
    validate_source_request,
)
from .branch_workspace import (
    add_context_snapshot,
    artifact_population,
    attempt_paths,
    create_attempt_workspace,
    read_outbox_json,
    verify_attempt_workspace,
    write_instruction,
)
from .errors import AuthorityError, IntegrityError, RuntimeFailure, ValidationError
from .integrity import load_and_verify_context
from .ntm_research import NtmControl, NtmReceipt
from .service_types import BranchLaunchOutcome, BranchResultOutcome
from .store import StoredObject
from .util import (
    canonical_json,
    digest_bytes,
    digest_json,
    new_id,
    read_regular_file,
    require_string_list,
    require_text,
    safe_relative_path,
    utc_now,
)


class BranchServiceMixin:
    """Durable research branches executed in persistent NTM Codex sessions."""

    MAX_ARTIFACT_BYTES = 10 * 1024 * 1024

    def create_research_branch(
        self,
        *,
        episode_id: str,
        commission_id: str,
        method_id: str,
        branch_kind: str,
        title: str,
        question: str,
        context_ids: list[str],
        expected_outputs: list[str],
        authority_ceiling: str,
        created_by: str,
        input_object_ids: list[str] | None = None,
        parent_branch_id: str | None = None,
    ) -> StoredObject:
        episode = self._require_kind(episode_id, "episode")
        commission = self._require_kind(commission_id, "commission")
        method = self._require_kind(method_id, "method")
        mandate = self._require_kind(episode.payload["mandate_id"], "mandate")
        self._require_authorised_actor(mandate, created_by, "create a research branch")
        if commission.payload["episode_id"] != episode_id:
            raise ValidationError("branch commission does not belong to episode")
        if method_id not in commission.payload["method_ids"]:
            raise AuthorityError("branch method is not permitted by the confirmed commission")
        if branch_kind not in BRANCH_KINDS:
            raise ValidationError("branch kind is unsupported")
        context_ids = require_string_list(context_ids, "branch contexts")
        expected_outputs = require_string_list(
            expected_outputs, "branch expected outputs"
        )
        input_object_ids = require_string_list(
            input_object_ids or [], "branch input objects", allow_empty=True
        )
        for context_id in context_ids:
            context = self._require_kind(context_id, "context")
            if context.payload["episode_id"] != episode_id:
                raise ValidationError("branch context crosses episode")
            if context.payload["commission_id"] != commission_id:
                raise ValidationError("branch context uses another commission")
            if context.payload["method_id"] != method_id:
                raise ValidationError("branch context uses another method")
            load_and_verify_context(self.store, context)
        for object_id in input_object_ids:
            item = self.store.get_object(object_id)
            item_episode = item.payload.get("episode_id")
            if item_episode is not None and item_episode != episode_id:
                raise ValidationError("branch input crosses episode")
        if parent_branch_id is not None:
            parent = self._require_kind(parent_branch_id, "research_branch")
            if parent.payload["episode_id"] != episode_id:
                raise ValidationError("parent branch crosses episode")
        branch = self.store.put_object(
            "research_branch",
            {
                "schema": "research-research-branch/v1",
                "episode_id": episode_id,
                "commission_id": commission_id,
                "method_id": method_id,
                "branch_kind": branch_kind,
                "title": title,
                "question": question,
                "context_ids": context_ids,
                "input_object_ids": input_object_ids,
                "expected_outputs": expected_outputs,
                "authority_ceiling": authority_ceiling,
                "created_by": created_by,
                "parent_branch_id": parent_branch_id,
            },
        )
        self.store.put_relation(episode_id, "has_research_branch", branch.id)
        self.store.put_relation(branch.id, "uses_commission", commission_id)
        self.store.put_relation(branch.id, "uses_method", method_id)
        for context_id in context_ids:
            self.store.put_relation(branch.id, "has_context", context_id)
        for object_id in input_object_ids:
            self.store.put_relation(branch.id, "has_input", object_id)
        if parent_branch_id is not None:
            self.store.put_relation(parent_branch_id, "spawned_branch", branch.id)
        return branch

    @staticmethod
    def _validate_session_name(session: str) -> str:
        session = require_text(session, "NTM session")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", session) is None:
            raise ValidationError("NTM session name is invalid")
        return session

    @staticmethod
    def _validate_role_name(role_name: str) -> str:
        role_name = require_text(role_name, "NTM role name")
        if re.fullmatch(r"[a-z][a-z_]{0,31}", role_name) is None:
            raise ValidationError("NTM role name is invalid")
        return role_name

    def _branch_bindings(self, branch_id: str) -> list[StoredObject]:
        bindings = [
            self._require_kind(relation.object_id, "ntm_binding")
            for relation in self.store.relations_from(branch_id, "has_ntm_binding")
        ]
        return sorted(bindings, key=lambda item: (item.created_at, item.id))

    def _latest_binding(self, branch_id: str) -> StoredObject | None:
        bindings = self._branch_bindings(branch_id)
        return bindings[-1] if bindings else None

    def _branch_context_ids(self, branch_id: str) -> list[str]:
        branch = self._require_kind(branch_id, "research_branch")
        result = list(branch.payload["context_ids"])
        for relation in self.store.relations_from(branch_id, "has_context"):
            if relation.object_id not in result:
                result.append(relation.object_id)
        return result

    def _branch_authority(
        self,
        branch_id: str,
    ) -> tuple[set[str], set[str], set[tuple[str, str]]]:
        assertions: set[str] = set()
        objects: set[str] = set()
        pairs: set[tuple[str, str]] = set()
        for context_id in self._branch_context_ids(branch_id):
            context = self._require_kind(context_id, "context")
            _, manifest = load_and_verify_context(self.store, context)
            assertions.update(manifest["included_assertion_ids"])
            objects.update(manifest["professional_object_ids"])
            pairs.update(
                (item["assertion_id"], item["professional_object_id"])
                for item in manifest["allowed_support_pairs"]
            )
        return assertions, objects, pairs

    def _binding_events(self, binding_id: str) -> list[StoredObject]:
        events = [
            self._require_kind(relation.object_id, "branch_event")
            for relation in self.store.relations_from(binding_id, "has_event")
        ]
        return sorted(events, key=lambda item: (item.created_at, item.id))

    def _latest_instruction(self, binding_id: str) -> StoredObject | None:
        items = [
            self._require_kind(relation.object_id, "branch_instruction")
            for relation in self.store.relations_from(binding_id, "has_instruction")
        ]
        return max(items, key=lambda item: item.payload["sequence"], default=None)

    def _instruction_ack(self, instruction_id: str) -> StoredObject | None:
        relations = self.store.relations_from(instruction_id, "acknowledged_by")
        if not relations:
            return None
        return self._require_kind(relations[-1].object_id, "branch_ack")

    def _latest_checkpoint(self, branch_id: str) -> StoredObject | None:
        checkpoints = [
            self._require_kind(relation.object_id, "branch_checkpoint")
            for relation in self.store.relations_from(branch_id, "has_checkpoint")
        ]
        return max(checkpoints, key=lambda item: item.payload["sequence"], default=None)

    def _store_ntm_event(
        self,
        *,
        branch_id: str,
        binding_id: str | None,
        event_kind: str,
        actor: str,
        receipt: NtmReceipt | None = None,
        instruction_id: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> StoredObject:
        event_details = dict(details or {})
        if receipt is not None:
            stdout = self.store.put_blob(receipt.stdout, media_type="text/plain")
            stderr = self.store.put_blob(receipt.stderr, media_type="text/plain")
            event_details.update(
                {
                    "action": receipt.action,
                    "argv": list(receipt.argv),
                    "exit_code": receipt.exit_code,
                    "timed_out": receipt.timed_out,
                    "response": receipt.response,
                    "stdout_digest": stdout.digest,
                    "stderr_digest": stderr.digest,
                }
            )
        event = self.store.put_object(
            "branch_event",
            {
                "schema": "research-branch-event/v1",
                "branch_id": branch_id,
                "binding_id": binding_id,
                "instruction_id": instruction_id,
                "event_kind": event_kind,
                "actor": actor,
                "details": event_details,
            },
        )
        self.store.put_relation(branch_id, "has_event", event.id)
        if binding_id is not None:
            self.store.put_relation(binding_id, "has_event", event.id)
        if instruction_id is not None:
            self.store.put_relation(instruction_id, "has_event", event.id)
        return event

    @staticmethod
    def _require_ntm_success(receipt: NtmReceipt, action: str) -> None:
        if not receipt.succeeded:
            reason = "timed out" if receipt.timed_out else f"exit {receipt.exit_code}"
            raise RuntimeFailure(f"NTM {action} failed: {reason}")

    def launch_research_branch(
        self,
        *,
        branch_id: str,
        controller: NtmControl,
        config: Path,
        model: str,
        role_name: str,
        actor: str,
        session: str | None = None,
        pane: int = 1,
        environment: Mapping[str, str] | None = None,
        resume_checkpoint_id: str | None = None,
    ) -> BranchLaunchOutcome:
        branch = self._require_kind(branch_id, "research_branch")
        episode = self._require_kind(branch.payload["episode_id"], "episode")
        mandate = self._require_kind(episode.payload["mandate_id"], "mandate")
        self._require_authorised_actor(mandate, actor, "launch a research branch")
        if not isinstance(pane, int) or pane < 1:
            raise ValidationError("NTM pane must be a positive integer")
        config = config.expanduser()
        if config.is_symlink() or not config.is_file():
            raise ValidationError("NTM config must be one exact regular file")
        config = config.resolve()
        config_bytes = read_regular_file(config, max_bytes=2 * 1024 * 1024)
        model = require_text(model, "Codex model")
        role_name = self._validate_role_name(role_name)
        session = self._validate_session_name(
            session or f"research-{branch.id.split('_', 1)[-1][:20]}"
        )
        predecessor = self._latest_binding(branch_id)
        if resume_checkpoint_id is not None:
            checkpoint = self._require_kind(resume_checkpoint_id, "branch_checkpoint")
            if checkpoint.payload["branch_id"] != branch_id:
                raise ValidationError("resume checkpoint belongs to another branch")
        binding_id = new_id("ntm_binding")
        context_ids = self._branch_context_ids(branch_id)
        paths, manifest_digest = create_attempt_workspace(
            self.store,
            branch=branch,
            binding_id=binding_id,
            context_ids=context_ids,
            input_object_ids=branch.payload["input_object_ids"],
            resume_checkpoint_id=resume_checkpoint_id,
        )
        binding = self.store.put_object(
            "ntm_binding",
            {
                "schema": "research-ntm-binding/v1",
                "branch_id": branch_id,
                "session": session,
                "pane": pane,
                "role_name": role_name,
                "model": model,
                "config_path": str(config),
                "config_digest": digest_bytes(config_bytes),
                "working_directory": str(paths.root),
                "attempt_manifest_digest": manifest_digest,
                "context_ids": context_ids,
                "predecessor_binding_id": predecessor.id if predecessor else None,
                "resume_checkpoint_id": resume_checkpoint_id,
            },
            object_id=binding_id,
        )
        self.store.put_relation(branch_id, "has_ntm_binding", binding.id)
        if predecessor is not None:
            self.store.put_relation(predecessor.id, "superseded_by", binding.id)
        if resume_checkpoint_id is not None:
            self.store.put_relation(binding.id, "resumes_from", resume_checkpoint_id)

        receipt = controller.spawn(
            session=session,
            working_directory=paths.root,
            role_name=role_name,
            config=config,
            environment=environment,
        )
        self._store_ntm_event(
            branch_id=branch_id,
            binding_id=binding.id,
            event_kind="ntm_spawn_returned",
            actor="system:ntm",
            receipt=receipt,
        )
        self._require_ntm_success(receipt, "spawn")
        kind = "resume" if resume_checkpoint_id is not None else "start"
        instruction = self._send_branch_instruction(
            branch=branch,
            binding=binding,
            controller=controller,
            config=config,
            instruction_kind=kind,
            actor=actor,
            context_ids=context_ids,
            checkpoint_id=resume_checkpoint_id,
            instruction_text=(
                "Resume this durable research branch from the supplied checkpoint."
                if resume_checkpoint_id is not None
                else "Begin this durable research branch from the confirmed commission."
            ),
            environment=environment,
        )
        return BranchLaunchOutcome(
            branch_id=branch.id,
            binding_id=binding.id,
            instruction_id=instruction.id,
            session=session,
            pane=pane,
        )

    def _send_branch_instruction(
        self,
        *,
        branch: StoredObject,
        binding: StoredObject,
        controller: NtmControl,
        config: Path,
        instruction_kind: str,
        actor: str,
        context_ids: list[str],
        checkpoint_id: str | None,
        instruction_text: str,
        environment: Mapping[str, str] | None,
        satisfies_source_request_ids: list[str] | None = None,
    ) -> StoredObject:
        if instruction_kind not in INSTRUCTION_KINDS:
            raise ValidationError("instruction kind is unsupported")
        paths, _ = verify_attempt_workspace(
            self.store,
            branch=branch,
            binding=binding,
        )
        previous = self._latest_instruction(binding.id)
        sequence = 1 if previous is None else previous.payload["sequence"] + 1
        instruction_id = new_id("branch_instruction")
        context_rows = [
            add_context_snapshot(self.store, paths, context_id)
            for context_id in context_ids
        ]
        payload = {
            "schema": "research-branch-instruction/v1",
            "instruction_id": instruction_id,
            "branch_id": branch.id,
            "binding_id": binding.id,
            "sequence": sequence,
            "instruction_kind": instruction_kind,
            "instruction": require_text(instruction_text, "branch instruction"),
            "branch": {
                "kind": branch.payload["branch_kind"],
                "title": branch.payload["title"],
                "question": branch.payload["question"],
                "authority_ceiling": branch.payload["authority_ceiling"],
                "expected_outputs": branch.payload["expected_outputs"],
            },
            "context_snapshots": context_rows,
            "resume_checkpoint_id": checkpoint_id,
            "satisfies_source_request_ids": satisfies_source_request_ids or [],
            "required_outputs": {
                "acknowledgement": f"outbox/acknowledgement-{instruction_id}.json",
                "checkpoints": "outbox/checkpoints/<sequence>.json",
                "source_requests": "outbox/source-requests/<request>.json",
                "result": "outbox/result.json",
                "artifacts": "outbox/artifacts/",
            },
            "rules": [
                "Use host-issued assertion and professional-object identifiers.",
                "New sources return as source requests and acquire no authority until the host admits them.",
                "Checkpoint after a consequential state change and before branch completion.",
                "A result remains provisional and cannot grant its own use or memory authority.",
                "Do not invoke codex exec or create another Codex runtime.",
            ],
        }
        message_path, message_digest = write_instruction(
            paths,
            sequence=sequence,
            kind=instruction_kind,
            payload=payload,
        )
        instruction = self.store.put_object(
            "branch_instruction",
            {
                "schema": "research-branch-instruction/v1",
                "branch_id": branch.id,
                "binding_id": binding.id,
                "sequence": sequence,
                "instruction_kind": instruction_kind,
                "actor": actor,
                "message_path": str(message_path),
                "message_digest": message_digest,
                "context_ids": context_ids,
                "checkpoint_id": checkpoint_id,
            },
            object_id=instruction_id,
        )
        self.store.put_relation(binding.id, "has_instruction", instruction.id)
        self.store.put_relation(branch.id, "has_instruction", instruction.id)
        receipt = controller.send(
            session=binding.payload["session"],
            pane=binding.payload["pane"],
            message=message_path,
            config=config,
            environment=environment,
        )
        self._store_ntm_event(
            branch_id=branch.id,
            binding_id=binding.id,
            instruction_id=instruction.id,
            event_kind="ntm_tracked_send_returned",
            actor="system:ntm",
            receipt=receipt,
        )
        self._require_ntm_success(receipt, "tracked send")
        return instruction

    def send_branch_instruction(
        self,
        *,
        branch_id: str,
        binding_id: str,
        controller: NtmControl,
        config: Path,
        instruction_kind: str,
        actor: str,
        instruction_text: str,
        context_ids: list[str] | None = None,
        checkpoint_id: str | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> StoredObject:
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        if binding.payload["branch_id"] != branch_id:
            raise ValidationError("NTM binding belongs to another branch")
        episode = self._require_kind(branch.payload["episode_id"], "episode")
        mandate = self._require_kind(episode.payload["mandate_id"], "mandate")
        self._require_authorised_actor(mandate, actor, "steer a research branch")
        return self._send_branch_instruction(
            branch=branch,
            binding=binding,
            controller=controller,
            config=config.resolve(),
            instruction_kind=instruction_kind,
            actor=actor,
            context_ids=context_ids or [],
            checkpoint_id=checkpoint_id,
            instruction_text=instruction_text,
            environment=environment,
        )

    def attach_branch_context_delta(
        self,
        *,
        branch_id: str,
        binding_id: str,
        context_id: str,
        controller: NtmControl,
        config: Path,
        actor: str,
        satisfies_source_request_ids: list[str] | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> StoredObject:
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        context = self._require_kind(context_id, "context")
        if binding.payload["branch_id"] != branch_id:
            raise ValidationError("binding belongs to another branch")
        if context.payload["episode_id"] != branch.payload["episode_id"]:
            raise ValidationError("context delta crosses episode")
        if context.payload["commission_id"] != branch.payload["commission_id"]:
            raise ValidationError("context delta uses another commission")
        if context.payload["method_id"] != branch.payload["method_id"]:
            raise ValidationError("context delta uses another method")
        load_and_verify_context(self.store, context)
        request_ids = require_string_list(
            satisfies_source_request_ids or [],
            "satisfied source requests",
            allow_empty=True,
        )
        for request_id in request_ids:
            request = self._require_kind(request_id, "source_request")
            if request.payload["branch_id"] != branch_id:
                raise ValidationError("context delta satisfies another branch request")
        if context_id not in self._branch_context_ids(branch_id):
            self.store.put_relation(branch_id, "has_context", context_id)
        for request_id in request_ids:
            self.store.put_relation(request_id, "satisfied_by", context_id)
        return self._send_branch_instruction(
            branch=branch,
            binding=binding,
            controller=controller,
            config=config.resolve(),
            instruction_kind="context_delta",
            actor=actor,
            context_ids=[context_id],
            checkpoint_id=self._latest_checkpoint(branch_id).id
            if self._latest_checkpoint(branch_id)
            else None,
            instruction_text=(
                "Continue the branch using this newly captured and purpose-admitted context delta."
            ),
            environment=environment,
            satisfies_source_request_ids=request_ids,
        )

    def collect_branch_acknowledgement(
        self,
        *,
        branch_id: str,
        binding_id: str,
        instruction_id: str,
    ) -> StoredObject:
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        instruction = self._require_kind(instruction_id, "branch_instruction")
        if binding.payload["branch_id"] != branch_id:
            raise ValidationError("binding belongs to another branch")
        if instruction.payload["binding_id"] != binding_id:
            raise ValidationError("instruction belongs to another binding")
        paths, _ = verify_attempt_workspace(
            self.store,
            branch=branch,
            binding=binding,
        )
        relative = f"acknowledgement-{instruction.id}.json"
        payload = read_outbox_json(paths, relative, "branch acknowledgement")
        acknowledged = validate_acknowledgement(
            payload,
            branch_id=branch.id,
            binding_id=binding.id,
            instruction_id=instruction.id,
            instruction_digest=instruction.payload["message_digest"],
            context_ids=instruction.payload["context_ids"],
            authority_ceiling=branch.payload["authority_ceiling"],
        )
        existing = self._instruction_ack(instruction.id)
        if existing is not None:
            if existing.payload != acknowledged:
                raise IntegrityError("instruction acknowledgement changed after custody")
            return existing
        ack = self.store.put_object(
            "branch_ack",
            {
                "schema": "research-branch-ack/v1",
                **{
                    key: acknowledged[key]
                    for key in (
                        "branch_id",
                        "binding_id",
                        "instruction_id",
                        "instruction_digest",
                        "context_ids",
                        "authority_ceiling",
                        "worker",
                        "protocol_version",
                    )
                },
            },
        )
        self.store.put_relation(instruction.id, "acknowledged_by", ack.id)
        self.store.put_relation(binding.id, "has_acknowledgement", ack.id)
        self._store_ntm_event(
            branch_id=branch.id,
            binding_id=binding.id,
            instruction_id=instruction.id,
            event_kind="semantic_acknowledgement_collected",
            actor="system:host",
            details={"acknowledgement_id": ack.id},
        )
        return ack

    def collect_branch_source_request(
        self,
        *,
        branch_id: str,
        binding_id: str,
        relative_path: str,
    ) -> StoredObject:
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        if binding.payload["branch_id"] != branch_id:
            raise ValidationError("binding belongs to another branch")
        paths, _ = verify_attempt_workspace(
            self.store,
            branch=branch,
            binding=binding,
        )
        request_path = (Path("source-requests") / safe_relative_path(relative_path)).as_posix()
        payload = read_outbox_json(paths, request_path, "branch source request")
        _, professional_objects, _ = self._branch_authority(branch_id)
        validated = validate_source_request(
            payload,
            branch_id=branch_id,
            binding_id=binding_id,
            available_object_ids=professional_objects,
        )
        for item in self.store.list_objects("source_request"):
            if (
                item.payload["branch_id"] == branch_id
                and item.payload["external_request_id"]
                == validated["external_request_id"]
            ):
                if item.payload != validated:
                    raise IntegrityError("source request changed after custody")
                return item
        request = self.store.put_object("source_request", validated)
        self.store.put_relation(branch_id, "has_source_request", request.id)
        self.store.put_relation(binding_id, "produced_source_request", request.id)
        self._store_ntm_event(
            branch_id=branch_id,
            binding_id=binding_id,
            event_kind="source_request_collected",
            actor="system:host",
            details={"source_request_id": request.id},
        )
        return request

    def collect_branch_checkpoint(
        self,
        *,
        branch_id: str,
        binding_id: str,
        relative_path: str,
    ) -> StoredObject:
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        if binding.payload["branch_id"] != branch_id:
            raise ValidationError("binding belongs to another branch")
        latest_instruction = self._latest_instruction(binding_id)
        if latest_instruction is None:
            raise RuntimeFailure("branch has no sent instruction")
        acknowledgement = self._instruction_ack(latest_instruction.id)
        if acknowledgement is None:
            raise RuntimeFailure("latest branch instruction lacks semantic acknowledgement")
        paths, _ = verify_attempt_workspace(
            self.store,
            branch=branch,
            binding=binding,
        )
        checkpoint_path = (Path("checkpoints") / safe_relative_path(relative_path)).as_posix()
        payload = read_outbox_json(paths, checkpoint_path, "branch checkpoint")
        previous = self._latest_checkpoint(branch_id)
        assertion_ids, object_ids, allowed_pairs = self._branch_authority(branch_id)
        known_requests = {
            relation.object_id
            for relation in self.store.relations_from(branch_id, "has_source_request")
        }
        validated = validate_checkpoint(
            payload,
            branch_id=branch_id,
            binding_id=binding_id,
            latest_sequence=previous.payload["sequence"] if previous else 0,
            predecessor_id=previous.id if previous else None,
            included_assertion_ids=assertion_ids,
            professional_object_ids=object_ids,
            allowed_support_pairs=allowed_pairs,
            known_source_request_ids=known_requests,
        )
        if validated["disposition"] == "complete":
            unresolved_requests = [
                request_id
                for request_id in validated["source_request_ids"]
                if not self.store.relations_from(request_id, "satisfied_by")
            ]
            if unresolved_requests:
                raise RuntimeFailure(
                    "completing checkpoint retains unsatisfied source requests: "
                    + ", ".join(unresolved_requests)
                )
        checkpoint = self.store.put_object(
            "branch_checkpoint",
            {
                "schema": "research-branch-checkpoint/v1",
                **validated,
                "acknowledgement_id": acknowledgement.id,
            },
        )
        self.store.put_relation(branch_id, "has_checkpoint", checkpoint.id)
        self.store.put_relation(binding_id, "produced_checkpoint", checkpoint.id)
        self.store.put_relation(acknowledgement.id, "licensed_checkpoint", checkpoint.id)
        if previous is not None:
            self.store.put_relation(previous.id, "superseded_by", checkpoint.id)
        self._store_ntm_event(
            branch_id=branch_id,
            binding_id=binding_id,
            event_kind="checkpoint_collected",
            actor="system:host",
            details={
                "checkpoint_id": checkpoint.id,
                "sequence": checkpoint.payload["sequence"],
                "disposition": checkpoint.payload["disposition"],
            },
        )
        return checkpoint

    def observe_branch_status(
        self,
        *,
        branch_id: str,
        binding_id: str,
        controller: NtmControl,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> StoredObject:
        binding = self._require_kind(binding_id, "ntm_binding")
        if binding.payload["branch_id"] != branch_id:
            raise ValidationError("binding belongs to another branch")
        receipt = controller.status(
            session=binding.payload["session"],
            config=config.resolve(),
            environment=environment,
        )
        event = self._store_ntm_event(
            branch_id=branch_id,
            binding_id=binding_id,
            event_kind="ntm_status_returned",
            actor="system:ntm",
            receipt=receipt,
        )
        self._require_ntm_success(receipt, "status")
        return event

    def observe_branch_completion(
        self,
        *,
        branch_id: str,
        binding_id: str,
        controller: NtmControl,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> StoredObject:
        binding = self._require_kind(binding_id, "ntm_binding")
        if binding.payload["branch_id"] != branch_id:
            raise ValidationError("binding belongs to another branch")
        receipt = controller.completion(
            session=binding.payload["session"],
            pane=binding.payload["pane"],
            config=config.resolve(),
            environment=environment,
        )
        event = self._store_ntm_event(
            branch_id=branch_id,
            binding_id=binding_id,
            event_kind="ntm_completion_returned",
            actor="system:ntm",
            receipt=receipt,
        )
        self._require_ntm_success(receipt, "completion observation")
        return event

    def stop_research_branch(
        self,
        *,
        branch_id: str,
        binding_id: str,
        controller: NtmControl,
        config: Path,
        actor: str,
        reason: str,
        environment: Mapping[str, str] | None = None,
    ) -> StoredObject:
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        episode = self._require_kind(branch.payload["episode_id"], "episode")
        mandate = self._require_kind(episode.payload["mandate_id"], "mandate")
        self._require_authorised_actor(mandate, actor, "stop a research branch")
        receipt = controller.stop(
            session=binding.payload["session"],
            config=config.resolve(),
            environment=environment,
        )
        event = self._store_ntm_event(
            branch_id=branch_id,
            binding_id=binding_id,
            event_kind="ntm_stop_returned",
            actor=actor,
            receipt=receipt,
            details={"reason": require_text(reason, "stop reason")},
        )
        self._require_ntm_success(receipt, "stop")
        return event

    def _has_completion_observation(self, binding_id: str) -> bool:
        return any(
            event.payload["event_kind"] == "ntm_completion_returned"
            and event.payload["details"].get("exit_code") == 0
            and not event.payload["details"].get("timed_out")
            for event in self._binding_events(binding_id)
        )

    def collect_branch_result(
        self,
        *,
        branch_id: str,
        binding_id: str,
    ) -> BranchResultOutcome:
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        if binding.payload["branch_id"] != branch_id:
            raise ValidationError("binding belongs to another branch")
        if not self._has_completion_observation(binding_id):
            raise RuntimeFailure("NTM completion has not been observed for this binding")
        instruction = self._latest_instruction(binding_id)
        if instruction is None or self._instruction_ack(instruction.id) is None:
            raise RuntimeFailure("latest branch instruction lacks semantic acknowledgement")
        checkpoint = self._latest_checkpoint(branch_id)
        if checkpoint is None or checkpoint.payload["binding_id"] != binding_id:
            raise RuntimeFailure("branch result lacks a checkpoint from this binding")
        if checkpoint.payload["disposition"] not in {"complete", "refuse"}:
            raise RuntimeFailure("latest checkpoint does not license branch completion")
        paths, _ = verify_attempt_workspace(
            self.store,
            branch=branch,
            binding=binding,
        )
        artifacts = artifact_population(paths)
        result_payload = read_outbox_json(paths, "result.json", "branch result")
        assertions, objects, pairs = self._branch_authority(branch_id)
        validated = validate_branch_result(
            result_payload,
            branch_id=branch_id,
            binding_id=binding_id,
            checkpoint_id=checkpoint.id,
            included_assertion_ids=assertions,
            professional_object_ids=objects,
            allowed_support_pairs=pairs,
            available_artifact_paths=set(artifacts),
        )
        if checkpoint.payload["disposition"] == "refuse" and validated["refusal"] is None:
            raise RuntimeFailure("refusing checkpoint requires a refusing result")

        events = self._binding_events(binding_id)
        event_bytes = canonical_json(
            [
                {
                    "id": event.id,
                    "digest": event.digest,
                    "payload": event.payload,
                }
                for event in events
            ]
        ).encode("utf-8")
        stdout_blob = self.store.put_blob(event_bytes, media_type="application/json")
        stderr_blob = self.store.put_blob(b"", media_type="text/plain")
        spawn_argv = next(
            (
                event.payload["details"].get("argv", [])
                for event in events
                if event.payload["event_kind"] == "ntm_spawn_returned"
            ),
            ["ntm", binding.payload["session"]],
        )
        output_manifest = {
            "schema": "research-branch-output-population/v1",
            "result_digest": digest_json(validated),
            "artifact_files": [
                {
                    "path": path,
                    "sha256": digest_bytes(
                        read_regular_file(file_path, max_bytes=self.MAX_ARTIFACT_BYTES)
                    ),
                    "size": file_path.stat().st_size,
                }
                for path, file_path in sorted(artifacts.items())
            ],
            "checkpoint_id": checkpoint.id,
            "branch_event_ids": [event.id for event in events],
        }
        context_id = self._branch_context_ids(branch_id)[-1]
        run = self.store.put_object(
            "run",
            {
                "schema": "research-run/v1",
                "context_id": context_id,
                "adapter": "ntm-persistent-codex/v1",
                "argv": spawn_argv or ["ntm", binding.payload["session"]],
                "working_directory": binding.payload["working_directory"],
                "status": "succeeded",
                "stdout_digest": stdout_blob.digest,
                "stderr_digest": stderr_blob.digest,
                "output_manifest": output_manifest,
                "branch_id": branch_id,
                "binding_id": binding_id,
                "checkpoint_id": checkpoint.id,
                "session": binding.payload["session"],
                "pane": binding.payload["pane"],
            },
        )
        self.store.put_relation(binding_id, "completed_as", run.id)
        self.store.put_relation(branch_id, "completed_as", run.id)

        episode = self._require_kind(branch.payload["episode_id"], "episode")
        mandate_id = episode.payload["mandate_id"]
        claim_ids: list[str] = []
        for claim_data in validated["claims"]:
            claim = self.store.put_object(
                "claim",
                {
                    "schema": "research-claim/v1",
                    "episode_id": episode.id,
                    "run_id": run.id,
                    "branch_id": branch_id,
                    "binding_id": binding_id,
                    "text": claim_data["text"],
                    "supporting_assertion_ids": claim_data["supporting_assertion_ids"],
                    "professional_object_ids": claim_data["professional_object_ids"],
                    "support_relations": claim_data["support_relations"],
                    "contradiction_relations": claim_data["contradiction_relations"],
                    "uncertainty": claim_data["uncertainty"],
                    "scope": claim_data["scope"],
                    "external_claim_id": claim_data["claim_id"],
                },
            )
            claim_ids.append(claim.id)
            self.store.put_relation(branch_id, "produced", claim.id)
            self.store.put_relation(run.id, "produced", claim.id)
            for relation in claim_data["support_relations"]:
                self.store.put_relation(
                    relation["assertion_id"],
                    "supports",
                    claim.id,
                    {"professional_object_id": relation["professional_object_id"]},
                )
                self.store.put_relation(
                    claim.id,
                    "concerns",
                    relation["professional_object_id"],
                )
            for relation in claim_data["contradiction_relations"]:
                self.store.put_relation(
                    relation["assertion_id"],
                    "contradicts",
                    claim.id,
                    {"professional_object_id": relation["professional_object_id"]},
                )

        artifact_ids: list[str] = []
        for artifact_data in validated["artifacts"]:
            source_path = artifacts[artifact_data["path"]]
            content = read_regular_file(source_path, max_bytes=self.MAX_ARTIFACT_BYTES)
            blob = self.store.put_blob(content, media_type=artifact_data["media_type"])
            artifact = self.store.put_object(
                "artifact",
                {
                    "schema": "research-artifact/v1",
                    "mandate_id": mandate_id,
                    "episode_id": episode.id,
                    "kind": artifact_data["kind"],
                    "filename": source_path.name,
                    "blob_digest": blob.digest,
                    "metadata": {
                        "title": artifact_data["title"],
                        "source_path": artifact_data["path"],
                        "producing_branch_id": branch_id,
                        "producing_binding_id": binding_id,
                        "producing_checkpoint_id": checkpoint.id,
                        "producing_run_id": run.id,
                    },
                    "parent_id": None,
                },
            )
            artifact_ids.append(artifact.id)
            self.store.put_relation(branch_id, "produced", artifact.id)
            self.store.put_relation(run.id, "produced", artifact.id)

        memory_ids: list[str] = []
        for proposal in validated["memory_proposals"]:
            memory = self.store.put_object(
                "memory",
                {
                    "schema": "research-memory/v1",
                    "mandate_id": mandate_id,
                    "actor": f"codex-branch:{branch_id}",
                    "content": proposal["content"],
                    "scope": proposal["scope"],
                    "authority": "model_proposed",
                    "source_correction_id": None,
                    "effective_from": utc_now(),
                    "effective_until": None,
                    "reason": proposal["reason"],
                },
            )
            memory_ids.append(memory.id)
            self.store.put_relation(branch_id, "proposed_memory", memory.id)

        result = self.store.put_object(
            "result",
            {
                "schema": "research-result/v1",
                "episode_id": episode.id,
                "run_id": run.id,
                "branch_id": branch_id,
                "binding_id": binding_id,
                "checkpoint_id": checkpoint.id,
                "summary": validated["summary"],
                "claim_ids": claim_ids,
                "artifact_ids": artifact_ids,
                "memory_proposal_ids": memory_ids,
                "unresolved_questions": validated["unresolved_questions"],
                "refusal": validated["refusal"],
                "result_digest": digest_json(validated),
            },
        )
        self.store.put_relation(branch_id, "produced", result.id)
        self.store.put_relation(run.id, "produced", result.id)
        self.store.put_relation(checkpoint.id, "resolved_as", result.id)
        for claim_id in claim_ids:
            self.store.put_relation(result.id, "contains", claim_id)
        for artifact_id in artifact_ids:
            self.store.put_relation(result.id, "rendered_as", artifact_id)
        for memory_id in memory_ids:
            self.store.put_relation(result.id, "proposes_memory", memory_id)
        self._store_ntm_event(
            branch_id=branch_id,
            binding_id=binding_id,
            event_kind="branch_result_collected",
            actor="system:host",
            details={
                "run_id": run.id,
                "result_id": result.id,
                "checkpoint_id": checkpoint.id,
            },
        )
        return BranchResultOutcome(
            branch_id=branch_id,
            binding_id=binding_id,
            checkpoint_id=checkpoint.id,
            run_id=run.id,
            result_id=result.id,
            claim_ids=tuple(claim_ids),
            artifact_ids=tuple(artifact_ids),
            memory_proposal_ids=tuple(memory_ids),
        )

    def branch_state(self, branch_id: str) -> dict[str, Any]:
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._latest_binding(branch_id)
        checkpoint = self._latest_checkpoint(branch_id)
        results = [
            self.store.get_object(relation.object_id)
            for relation in self.store.relations_from(branch_id, "produced")
            if self.store.get_object(relation.object_id).kind == "result"
        ]
        events = [
            self._require_kind(relation.object_id, "branch_event")
            for relation in self.store.relations_from(branch_id, "has_event")
        ]
        if results:
            state = "completed"
        elif checkpoint and checkpoint.payload["disposition"] == "refuse":
            state = "refused"
        elif checkpoint and checkpoint.payload["disposition"] == "blocked":
            state = "blocked"
        elif binding:
            state = "active"
        else:
            state = "planned"
        return {
            "branch_id": branch.id,
            "state": state,
            "latest_binding_id": binding.id if binding else None,
            "latest_checkpoint_id": checkpoint.id if checkpoint else None,
            "result_ids": [item.id for item in results],
            "event_ids": [item.id for item in events],
            "context_ids": self._branch_context_ids(branch_id),
        }
