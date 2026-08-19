from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Self

from .errors import AuthorityError, ValidationError
from .store import StoredObject, WorkspaceStore


class BaseServiceMixin:
    def __init__(self, store: WorkspaceStore) -> None:
        self.store = store

    @classmethod
    def initialise(cls, root: Path, *, title: str = "Local research workspace") -> Self:
        return cls(WorkspaceStore.initialise(root, title=title))

    @classmethod
    def open(cls, root: Path) -> Self:
        return cls(WorkspaceStore(root))

    def _require_kind(self, object_id: str, kind: str) -> StoredObject:
        item = self.store.get_object(object_id)
        if item.kind != kind:
            raise ValidationError(f"{object_id} is {item.kind}, expected {kind}")
        return item

    def _mandate_for_episode(self, episode_id: str) -> StoredObject:
        episode = self._require_kind(episode_id, "episode")
        return self._require_kind(episode.payload["mandate_id"], "mandate")

    @staticmethod
    def _authorised_actors(mandate: StoredObject) -> set[str]:
        actors = {mandate.payload["actor"]}
        configured = mandate.payload.get("policy", {}).get("authorised_actors", [])
        if isinstance(configured, list):
            actors.update(item for item in configured if isinstance(item, str) and item.strip())
        return actors

    def _require_authorised_actor(self, mandate: StoredObject, actor: str, action: str) -> None:
        if actor not in self._authorised_actors(mandate):
            raise AuthorityError(f"{actor} is not authorised to {action} under {mandate.id}")

    def _target_has_use_decision(self, target_id: str) -> bool:
        for relation in self.store.relations_from(target_id, "has_decision"):
            decision = self._require_kind(relation.object_id, "decision")
            if decision.payload["action"] in {"use", "accept", "rely"}:
                return True
        return False

    def _validate_perspective_item(self, mandate_id: str, item_id: str) -> None:
        item = self.store.get_object(item_id)
        if item.kind == "memory":
            if item.payload["mandate_id"] != mandate_id:
                raise ValidationError("perspective memory crosses mandate")
            if item.payload["authority"] not in {"human_confirmed", "policy"}:
                raise AuthorityError("model-proposed memory cannot enter an active perspective")
        elif item.kind in {"result", "claim", "artifact"}:
            if not self._target_has_use_decision(item_id):
                raise AuthorityError(f"{item.kind} {item_id} lacks a scoped use decision")
        elif item.kind == "professional_object":
            if item.payload["mandate_id"] != mandate_id:
                raise ValidationError("perspective professional object crosses mandate")
            if item.payload["authority"] not in {"human_confirmed", "policy"}:
                raise AuthorityError(
                    "model-proposed professional object cannot enter an active perspective"
                )
        elif item.kind not in {"decision", "correction"}:
            raise ValidationError(f"{item.kind} cannot enter an active perspective in V0")

    def create_mandate(
        self,
        *,
        title: str,
        decision_use: str,
        actor: str,
        policy: Mapping[str, Any] | None = None,
    ) -> StoredObject:
        return self.store.put_object(
            "mandate",
            {
                "schema": "research-mandate/v1",
                "title": title,
                "decision_use": decision_use,
                "policy": dict(policy or {}),
                "actor": actor,
            },
        )

    def create_perspective(
        self,
        *,
        mandate_id: str,
        label: str,
        item_ids: list[str] | None = None,
        parent_id: str | None = None,
    ) -> StoredObject:
        self._require_kind(mandate_id, "mandate")
        items = item_ids or []
        for item_id in items:
            self._validate_perspective_item(mandate_id, item_id)
        if parent_id is not None:
            parent = self._require_kind(parent_id, "perspective")
            if parent.payload["mandate_id"] != mandate_id:
                raise ValidationError("perspective parent crosses mandate")
        perspective = self.store.put_object(
            "perspective",
            {
                "schema": "research-perspective/v1",
                "mandate_id": mandate_id,
                "label": label,
                "item_ids": items,
                "parent_id": parent_id,
            },
        )
        self.store.put_relation(mandate_id, "has_perspective", perspective.id)
        if parent_id is not None:
            self.store.put_relation(parent_id, "superseded_by", perspective.id)
        for item_id in items:
            self.store.put_relation(perspective.id, "contains", item_id)
        return perspective

    def create_episode(
        self,
        *,
        mandate_id: str,
        title: str,
        original_request: str,
        evidence_cutoff: str,
        intended_use: str,
        prior_perspective_id: str | None = None,
    ) -> StoredObject:
        self._require_kind(mandate_id, "mandate")
        if prior_perspective_id is not None:
            perspective = self._require_kind(prior_perspective_id, "perspective")
            if perspective.payload["mandate_id"] != mandate_id:
                raise ValidationError("episode prior perspective crosses mandate")
        episode = self.store.put_object(
            "episode",
            {
                "schema": "research-episode/v1",
                "mandate_id": mandate_id,
                "title": title,
                "original_request": original_request,
                "evidence_cutoff": evidence_cutoff,
                "intended_use": intended_use,
                "prior_perspective_id": prior_perspective_id,
            },
        )
        self.store.put_relation(mandate_id, "has_episode", episode.id)
        if prior_perspective_id:
            self.store.put_relation(episode.id, "begins_from", prior_perspective_id)
        return episode

    def confirm_commission(
        self,
        *,
        episode_id: str,
        actor: str,
        purpose: str,
        subject_ids: list[str],
        method_ids: list[str],
        output_kinds: list[str],
        unresolved_questions: list[str] | None = None,
        limits: Mapping[str, Any] | None = None,
    ) -> StoredObject:
        episode = self._require_kind(episode_id, "episode")
        mandate = self._require_kind(episode.payload["mandate_id"], "mandate")
        self._require_authorised_actor(mandate, actor, "confirm a commission")
        for subject_id in subject_ids:
            self.store.get_object(subject_id)
        for method_id in method_ids:
            self._require_kind(method_id, "method")
        commission = self.store.put_object(
            "commission",
            {
                "schema": "research-commission/v1",
                "episode_id": episode_id,
                "actor": actor,
                "purpose": purpose,
                "subject_ids": subject_ids,
                "method_ids": method_ids,
                "output_kinds": output_kinds,
                "unresolved_questions": unresolved_questions or [],
                "limits": dict(limits or {}),
                "intended_use": episode.payload["intended_use"],
            },
        )
        self.store.put_relation(episode_id, "has_confirmed_commission", commission.id)
        for subject_id in subject_ids:
            self.store.put_relation(commission.id, "concerns", subject_id)
        for method_id in method_ids:
            self.store.put_relation(commission.id, "permits_method", method_id)
        return commission

    def register_method(
        self,
        *,
        name: str,
        version: str,
        purpose: str,
        output_kinds: list[str],
        required_actions: list[str] | None = None,
        runtime: Mapping[str, Any] | None = None,
        limits: Mapping[str, Any] | None = None,
    ) -> StoredObject:
        return self.store.put_object(
            "method",
            {
                "schema": "research-method/v1",
                "name": name,
                "version": version,
                "purpose": purpose,
                "output_kinds": output_kinds,
                "required_actions": required_actions or [],
                "runtime": dict(runtime or {}),
                "limits": dict(limits or {}),
            },
        )
