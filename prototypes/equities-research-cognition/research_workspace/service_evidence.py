from __future__ import annotations

from datetime import datetime, timezone
import mimetypes
from pathlib import Path
from typing import Any, Mapping

from .errors import AuthorityError, ValidationError
from .store import StoredObject
from .util import read_regular_file


class EvidenceServiceMixin:
    def capture_source(
        self,
        *,
        mandate_id: str,
        path: Path,
        source_class: str,
        rights: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
        published_at: str | None = None,
        media_type: str | None = None,
        max_bytes: int = 25 * 1024 * 1024,
    ) -> StoredObject:
        self._require_kind(mandate_id, "mandate")
        path = path.expanduser()
        if path.is_symlink():
            raise ValidationError("source path cannot be a symlink")
        path = path.resolve()
        content = read_regular_file(path, max_bytes=max_bytes)
        guessed = mimetypes.guess_type(path.name)[0]
        media_type = media_type or guessed or "application/octet-stream"
        blob = self.store.put_blob(content, media_type=media_type)
        source = self.store.put_object(
            "source",
            {
                "schema": "research-source/v1",
                "mandate_id": mandate_id,
                "filename": path.name,
                "media_type": media_type,
                "blob_digest": blob.digest,
                "source_class": source_class,
                "rights": dict(rights),
                "metadata": dict(metadata or {}),
                "published_at": published_at,
                "captured_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        self.store.put_relation(mandate_id, "has_source", source.id)
        return source

    def create_assertion(
        self,
        *,
        source_id: str,
        locator: str,
        content: str,
        attributes: Mapping[str, Any],
        proposed_by: str,
    ) -> StoredObject:
        self._require_kind(source_id, "source")
        assertion = self.store.put_object(
            "assertion",
            {
                "schema": "research-assertion/v1",
                "source_id": source_id,
                "locator": locator,
                "content": content,
                "attributes": dict(attributes),
                "proposed_by": proposed_by,
            },
        )
        self.store.put_relation(source_id, "contains", assertion.id)
        return assertion

    def create_professional_object(
        self,
        *,
        mandate_id: str,
        kind: str,
        label: str,
        attributes: Mapping[str, Any],
        binding: Mapping[str, Any] | None,
        authority: str,
        actor: str,
    ) -> StoredObject:
        mandate = self._require_kind(mandate_id, "mandate")
        if authority in {"human_confirmed", "policy"}:
            self._require_authorised_actor(mandate, actor, "confirm a professional object")
        item = self.store.put_object(
            "professional_object",
            {
                "schema": "research-professional-object/v1",
                "mandate_id": mandate_id,
                "kind": kind,
                "label": label,
                "attributes": dict(attributes),
                "binding": dict(binding or {}),
                "authority": authority,
                "actor": actor,
            },
        )
        self.store.put_relation(mandate_id, "has_professional_object", item.id)
        return item

    def decide_evidence_use(
        self,
        *,
        episode_id: str,
        assertion_id: str,
        professional_object_id: str,
        intended_use: str,
        permitted_actions: list[str],
        decision: str,
        rationale: str,
        actor: str,
        effective_until: str | None = None,
    ) -> StoredObject:
        episode = self._require_kind(episode_id, "episode")
        assertion = self._require_kind(assertion_id, "assertion")
        professional_object = self._require_kind(professional_object_id, "professional_object")
        mandate = self._require_kind(episode.payload["mandate_id"], "mandate")
        self._require_authorised_actor(mandate, actor, "decide evidence use")
        if professional_object.payload["authority"] not in {"human_confirmed", "policy"}:
            raise AuthorityError("evidence cannot support an unconfirmed professional object")
        source = self._require_kind(assertion.payload["source_id"], "source")
        if source.payload["mandate_id"] != episode.payload["mandate_id"]:
            raise ValidationError("assertion source crosses episode mandate")
        if professional_object.payload["mandate_id"] != episode.payload["mandate_id"]:
            raise ValidationError("professional object crosses episode mandate")
        item = self.store.put_object(
            "evidence_decision",
            {
                "schema": "research-evidence-decision/v1",
                "episode_id": episode_id,
                "assertion_id": assertion_id,
                "professional_object_id": professional_object_id,
                "intended_use": intended_use,
                "permitted_actions": permitted_actions,
                "decision": decision,
                "rationale": rationale,
                "actor": actor,
                "effective_from": episode.payload["evidence_cutoff"],
                "effective_until": effective_until,
            },
        )
        self.store.put_relation(assertion_id, "governed_by", item.id)
        self.store.put_relation(professional_object_id, "governed_by", item.id)
        self.store.put_relation(episode_id, "has_evidence_decision", item.id)
        return item

    @staticmethod
    def _active_at(payload: Mapping[str, Any], at_time: str) -> bool:
        effective_from = payload.get("effective_from")
        effective_until = payload.get("effective_until")
        try:
            at = datetime.fromisoformat(at_time.replace("Z", "+00:00"))
            if at.tzinfo is None:
                at = at.replace(tzinfo=timezone.utc)
            if effective_from:
                start = datetime.fromisoformat(str(effective_from).replace("Z", "+00:00"))
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
                if at < start:
                    return False
            if effective_until:
                end = datetime.fromisoformat(str(effective_until).replace("Z", "+00:00"))
                if end.tzinfo is None:
                    end = end.replace(tzinfo=timezone.utc)
                if at > end:
                    return False
        except ValueError as exc:
            raise ValidationError("evidence decision contains an invalid time") from exc
        return True

    def _latest_evidence_decision(
        self,
        *,
        episode_id: str,
        assertion_id: str,
        professional_object_id: str,
        intended_use: str,
        at_time: str,
    ) -> StoredObject | None:
        matches = [
            item
            for item in self.store.list_objects("evidence_decision")
            if item.payload["episode_id"] == episode_id
            and item.payload["assertion_id"] == assertion_id
            and item.payload["professional_object_id"] == professional_object_id
            and item.payload["intended_use"] == intended_use
            and self._active_at(item.payload, at_time)
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: (item.created_at, item.id))
