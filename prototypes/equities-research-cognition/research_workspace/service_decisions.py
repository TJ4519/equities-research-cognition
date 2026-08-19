from __future__ import annotations

from typing import Any, Mapping

from .errors import ValidationError
from .store import StoredObject
from .util import utc_now


class DecisionServiceMixin:
    def record_decision(
        self,
        *,
        episode_id: str,
        target_id: str,
        action: str,
        purpose: str,
        actor: str,
        grant: Mapping[str, Any],
    ) -> StoredObject:
        mandate = self._mandate_for_episode(episode_id)
        self._require_authorised_actor(mandate, actor, "record a decision")
        self.store.get_object(target_id)
        decision = self.store.put_object(
            "decision",
            {
                "schema": "research-decision/v1",
                "episode_id": episode_id,
                "target_id": target_id,
                "action": action,
                "purpose": purpose,
                "actor": actor,
                "grant": dict(grant),
            },
        )
        self.store.put_relation(target_id, "has_decision", decision.id)
        self.store.put_relation(episode_id, "has_decision", decision.id)
        return decision

    def record_correction(
        self,
        *,
        episode_id: str,
        target_id: str,
        actor: str,
        reason: str,
        replacement: Mapping[str, Any],
        scope: Mapping[str, Any],
    ) -> StoredObject:
        mandate = self._mandate_for_episode(episode_id)
        self._require_authorised_actor(mandate, actor, "record a correction")
        self.store.get_object(target_id)
        correction = self.store.put_object(
            "correction",
            {
                "schema": "research-correction/v1",
                "episode_id": episode_id,
                "target_id": target_id,
                "actor": actor,
                "reason": reason,
                "replacement": dict(replacement),
                "scope": dict(scope),
            },
        )
        self.store.put_relation(target_id, "corrected_by", correction.id)
        self.store.put_relation(episode_id, "has_correction", correction.id)
        return correction

    def create_memory_entry(
        self,
        *,
        mandate_id: str,
        actor: str,
        content: str,
        scope: Mapping[str, Any],
        authority: str,
        source_correction_id: str | None = None,
        effective_until: str | None = None,
    ) -> StoredObject:
        mandate = self._require_kind(mandate_id, "mandate")
        if authority in {"human_confirmed", "policy"}:
            self._require_authorised_actor(mandate, actor, "create active memory")
        if source_correction_id:
            self._require_kind(source_correction_id, "correction")
        memory = self.store.put_object(
            "memory",
            {
                "schema": "research-memory/v1",
                "mandate_id": mandate_id,
                "actor": actor,
                "content": content,
                "scope": dict(scope),
                "authority": authority,
                "source_correction_id": source_correction_id,
                "effective_from": utc_now(),
                "effective_until": effective_until,
            },
        )
        self.store.put_relation(mandate_id, "has_memory", memory.id)
        if source_correction_id:
            self.store.put_relation(source_correction_id, "promoted_as_memory", memory.id)
        return memory

    def create_evaluation_case(
        self,
        *,
        mandate_id: str,
        episode_id: str,
        name: str,
        baseline_run_id: str,
        baseline_result_id: str,
        expected: Mapping[str, Any] | None = None,
    ) -> StoredObject:
        self._require_kind(mandate_id, "mandate")
        self._require_kind(episode_id, "episode")
        run = self._require_kind(baseline_run_id, "run")
        result = self._require_kind(baseline_result_id, "result")
        if run.payload["context_id"] not in {
            relation.object_id for relation in self.store.relations_from(episode_id, "has_context")
        }:
            raise ValidationError("baseline run does not belong to episode")
        if result.payload["run_id"] != baseline_run_id:
            raise ValidationError("baseline result does not belong to run")
        case = self.store.put_object(
            "evaluation_case",
            {
                "schema": "research-evaluation-case/v1",
                "mandate_id": mandate_id,
                "episode_id": episode_id,
                "name": name,
                "baseline_run_id": baseline_run_id,
                "baseline_result_id": baseline_result_id,
                "expected": dict(
                    expected
                    or {
                        "result_digest": result.payload["result_digest"],
                        "claim_ids": result.payload["claim_ids"],
                        "artifact_ids": result.payload["artifact_ids"],
                    }
                ),
            },
        )
        self.store.put_relation(episode_id, "has_evaluation_case", case.id)
        return case

    def status(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for item in self.store.list_objects():
            counts[item.kind] = counts.get(item.kind, 0) + 1
        return {
            "schema": self.store.meta().get("schema_version"),
            "root": str(self.store.root),
            "counts": dict(sorted(counts.items())),
            "integrity": self.store.verify_all(),
        }
