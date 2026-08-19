from __future__ import annotations

from typing import Any

from .branch_workspace import read_outbox_json, verify_attempt_workspace
from .errors import RuntimeFailure, ValidationError
from .service_types import BranchResultOutcome
from .util import (
    canonical_json,
    digest_json,
    require_string_list,
    require_text,
)


class DiscoveryBranchServiceMixin:
    """Give discovery work a result that carries no claim authority."""

    def _is_discovery_branch(self, branch_id: str) -> bool:
        return self._branch_context_kind(branch_id) == "discovery"

    def collect_branch_checkpoint(
        self,
        *,
        branch_id: str,
        binding_id: str,
        relative_path: str,
    ):
        if not self._is_discovery_branch(branch_id):
            return super().collect_branch_checkpoint(
                branch_id=branch_id,
                binding_id=binding_id,
                relative_path=relative_path,
            )
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        latest_instruction = self._latest_instruction(binding_id)
        if latest_instruction is None:
            raise RuntimeFailure("discovery branch has no sent instruction")
        acknowledgement = self._instruction_ack(latest_instruction.id)
        if acknowledgement is None:
            raise RuntimeFailure(
                "latest discovery instruction lacks semantic acknowledgement"
            )
        paths, _ = verify_attempt_workspace(
            self.store,
            branch=branch,
            binding=binding,
        )
        payload = read_outbox_json(
            paths,
            f"checkpoints/{relative_path}",
            "discovery checkpoint",
        )
        if payload.get("schema") != "research-branch-checkpoint/v1":
            raise RuntimeFailure("discovery checkpoint has the wrong schema")
        if payload.get("branch_id") != branch_id or payload.get("binding_id") != binding_id:
            raise RuntimeFailure("discovery checkpoint names the wrong binding")
        previous = self._latest_checkpoint(branch_id)
        sequence = payload.get("sequence")
        expected_sequence = 1 if previous is None else previous.payload["sequence"] + 1
        if sequence != expected_sequence:
            raise RuntimeFailure("discovery checkpoint sequence is not the next value")
        if payload.get("predecessor_id") != (previous.id if previous else None):
            raise RuntimeFailure("discovery checkpoint names the wrong predecessor")
        candidate_claims = payload.get("candidate_claims", [])
        if candidate_claims != []:
            raise RuntimeFailure(
                "discovery checkpoint cannot create supported candidate claims"
            )
        known_requests = {
            relation.object_id
            for relation in self.store.relations_from(branch_id, "has_source_request")
        }
        source_request_ids = require_string_list(
            payload.get("source_request_ids", []),
            "discovery source requests",
            allow_empty=True,
        )
        unknown = set(source_request_ids) - known_requests
        if unknown:
            raise RuntimeFailure(
                "discovery checkpoint names an unknown source request: "
                + ", ".join(sorted(unknown))
            )
        disposition = require_text(
            payload.get("disposition"),
            "discovery checkpoint disposition",
        )
        if disposition not in {"continue", "complete", "refuse", "blocked"}:
            raise RuntimeFailure("discovery checkpoint disposition is unsupported")
        refusal = payload.get("refusal")
        if refusal is not None:
            refusal = require_text(refusal, "discovery refusal")
        if disposition == "refuse" and refusal is None:
            raise RuntimeFailure("refusing discovery checkpoint requires a reason")
        if disposition == "complete" and not source_request_ids:
            raise RuntimeFailure(
                "completed discovery branch must return at least one source request"
            )
        checkpoint = self.store.put_object(
            "branch_checkpoint",
            {
                "schema": "research-branch-checkpoint/v1",
                "branch_id": branch_id,
                "binding_id": binding_id,
                "sequence": sequence,
                "predecessor_id": previous.id if previous else None,
                "acknowledgement_id": acknowledgement.id,
                "candidate_claims": [],
                "rivals": payload.get("rivals", []),
                "source_request_ids": source_request_ids,
                "artifact_proposals": payload.get("artifact_proposals", []),
                "unresolved_questions": require_string_list(
                    payload.get("unresolved_questions", []),
                    "discovery unresolved questions",
                    allow_empty=True,
                ),
                "next_action": payload.get("next_action"),
                "disposition": disposition,
                "refusal": refusal,
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
            event_kind="discovery_checkpoint_collected",
            actor="system:host",
            details={
                "checkpoint_id": checkpoint.id,
                "sequence": sequence,
                "disposition": disposition,
                "source_request_ids": source_request_ids,
            },
        )
        return checkpoint

    def collect_branch_result(
        self,
        *,
        branch_id: str,
        binding_id: str,
    ) -> BranchResultOutcome:
        if not self._is_discovery_branch(branch_id):
            return super().collect_branch_result(
                branch_id=branch_id,
                binding_id=binding_id,
            )
        branch = self._require_kind(branch_id, "research_branch")
        binding = self._require_kind(binding_id, "ntm_binding")
        if not self._has_completion_observation(binding_id):
            raise RuntimeFailure("NTM completion has not been observed")
        instruction = self._latest_instruction(binding_id)
        if instruction is None or self._instruction_ack(instruction.id) is None:
            raise RuntimeFailure("latest discovery instruction lacks acknowledgement")
        checkpoint = self._latest_checkpoint(branch_id)
        if checkpoint is None or checkpoint.payload["binding_id"] != binding_id:
            raise RuntimeFailure("discovery result lacks a checkpoint from this binding")
        if checkpoint.payload["disposition"] not in {"complete", "refuse"}:
            raise RuntimeFailure("discovery checkpoint does not license completion")
        paths, _ = verify_attempt_workspace(
            self.store,
            branch=branch,
            binding=binding,
        )
        payload = read_outbox_json(paths, "result.json", "discovery branch result")
        if payload.get("schema") != "research-branch-result/v1":
            raise RuntimeFailure("discovery result has the wrong schema")
        expected = {
            "branch_id": branch_id,
            "binding_id": binding_id,
            "checkpoint_id": checkpoint.id,
        }
        for key, value in expected.items():
            if payload.get(key) != value:
                raise RuntimeFailure(f"discovery result disagrees on {key}")
        if payload.get("claims", []) != []:
            raise RuntimeFailure("discovery result cannot contain supported claims")
        if payload.get("artifacts", []) != []:
            raise RuntimeFailure("discovery result cannot create professional artifacts")
        if payload.get("memory_proposals", []) != []:
            raise RuntimeFailure("discovery result cannot propose active memory")
        source_request_ids = require_string_list(
            payload.get("source_request_ids", []),
            "discovery result source requests",
            allow_empty=True,
        )
        if source_request_ids != checkpoint.payload["source_request_ids"]:
            raise RuntimeFailure("discovery result changes the checkpoint source requests")
        refusal = payload.get("refusal")
        if refusal is not None:
            refusal = require_text(refusal, "discovery result refusal")
        if checkpoint.payload["disposition"] == "complete" and not source_request_ids:
            raise RuntimeFailure("completed discovery result lacks source requests")
        if checkpoint.payload["disposition"] == "refuse" and refusal is None:
            raise RuntimeFailure("refusing discovery result lacks a reason")

        events = self._binding_events(binding_id)
        event_blob = self.store.put_blob(
            canonical_json(
                [
                    {"id": event.id, "digest": event.digest, "payload": event.payload}
                    for event in events
                ]
            ).encode("utf-8"),
            media_type="application/json",
        )
        empty_blob = self.store.put_blob(b"", media_type="text/plain")
        context_id = self._branch_context_ids(branch_id)[-1]
        run = self.store.put_object(
            "run",
            {
                "schema": "research-run/v1",
                "context_id": context_id,
                "adapter": "ntm-persistent-codex/v1",
                "argv": ["ntm", binding.payload["session"]],
                "working_directory": binding.payload["working_directory"],
                "status": "succeeded",
                "stdout_digest": event_blob.digest,
                "stderr_digest": empty_blob.digest,
                "output_manifest": {
                    "schema": "research-discovery-output-population/v1",
                    "result_digest": digest_json(payload),
                    "checkpoint_id": checkpoint.id,
                    "source_request_ids": source_request_ids,
                    "branch_event_ids": [event.id for event in events],
                },
                "branch_id": branch_id,
                "binding_id": binding_id,
                "checkpoint_id": checkpoint.id,
                "session": binding.payload["session"],
                "pane": binding.payload["pane"],
            },
        )
        result = self.store.put_object(
            "result",
            {
                "schema": "research-result/v1",
                "episode_id": branch.payload["episode_id"],
                "run_id": run.id,
                "branch_id": branch_id,
                "binding_id": binding_id,
                "checkpoint_id": checkpoint.id,
                "summary": require_text(payload.get("summary"), "discovery summary"),
                "claim_ids": [],
                "artifact_ids": [],
                "memory_proposal_ids": [],
                "source_request_ids": source_request_ids,
                "leads": payload.get("leads", []),
                "unresolved_questions": require_string_list(
                    payload.get("unresolved_questions", []),
                    "discovery result unresolved questions",
                    allow_empty=True,
                ),
                "refusal": refusal,
                "result_digest": digest_json(payload),
            },
        )
        self.store.put_relation(binding_id, "completed_as", run.id)
        self.store.put_relation(branch_id, "completed_as", run.id)
        self.store.put_relation(branch_id, "produced", result.id)
        self.store.put_relation(run.id, "produced", result.id)
        self.store.put_relation(checkpoint.id, "resolved_as", result.id)
        for source_request_id in source_request_ids:
            self.store.put_relation(result.id, "requests_source", source_request_id)
        self._store_ntm_event(
            branch_id=branch_id,
            binding_id=binding_id,
            event_kind="discovery_result_collected",
            actor="system:host",
            details={
                "run_id": run.id,
                "result_id": result.id,
                "checkpoint_id": checkpoint.id,
                "source_request_ids": source_request_ids,
            },
        )
        return BranchResultOutcome(
            branch_id=branch_id,
            binding_id=binding_id,
            checkpoint_id=checkpoint.id,
            run_id=run.id,
            result_id=result.id,
            claim_ids=(),
            artifact_ids=(),
            memory_proposal_ids=(),
        )
