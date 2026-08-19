from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Mapping

from .errors import AuthorityError, ValidationError
from .store import StoredObject
from .util import (
    atomic_write,
    canonical_json,
    digest_bytes,
    ensure_inside,
    new_id,
    require_string_list,
    safe_relative_path,
)


class ContextServiceMixin:
    def build_context(
        self,
        *,
        episode_id: str,
        commission_id: str,
        method_id: str,
        purpose: str,
        assertion_ids: list[str],
        professional_object_ids: list[str],
        required_action: str,
        memory_entry_ids: list[str] | None = None,
        allowed_tools: list[str] | None = None,
        output_contract: Mapping[str, Any] | None = None,
    ) -> StoredObject:
        episode = self._require_kind(episode_id, "episode")
        commission = self._require_kind(commission_id, "commission")
        method = self._require_kind(method_id, "method")
        if commission.payload["episode_id"] != episode_id:
            raise ValidationError("commission does not belong to episode")
        if method_id not in commission.payload["method_ids"]:
            raise AuthorityError("confirmed commission does not permit this method")
        professional_object_ids = require_string_list(
            professional_object_ids, "context professional objects"
        )
        assertion_ids = require_string_list(assertion_ids, "context assertions", allow_empty=True)
        memory_entry_ids = require_string_list(
            memory_entry_ids or [], "context memory entries", allow_empty=True
        )
        allowed_tools = require_string_list(
            allowed_tools or [], "context allowed tools", allow_empty=True
        )
        for object_id in professional_object_ids:
            item = self._require_kind(object_id, "professional_object")
            if item.payload["mandate_id"] != episode.payload["mandate_id"]:
                raise ValidationError("context professional object crosses mandate")
            if item.payload["authority"] not in {"human_confirmed", "policy"}:
                raise AuthorityError("support context requires a confirmed professional object")
        for memory_id in memory_entry_ids:
            item = self._require_kind(memory_id, "memory")
            if item.payload["mandate_id"] != episode.payload["mandate_id"]:
                raise ValidationError("context memory crosses mandate")
            if item.payload["authority"] not in {"human_confirmed", "policy"}:
                raise AuthorityError("model-proposed memory cannot enter a consequential context")
            if item.payload.get("effective_until") and not self._active_at(
                item.payload, episode.payload["evidence_cutoff"]
            ):
                raise AuthorityError("expired memory cannot enter a context")

        included_assertions: list[str] = []
        excluded_assertions: list[dict[str, str]] = []
        allowed_support_pairs: list[dict[str, str]] = []
        for assertion_id in assertion_ids:
            assertion = self._require_kind(assertion_id, "assertion")
            source = self._require_kind(assertion.payload["source_id"], "source")
            if source.payload["mandate_id"] != episode.payload["mandate_id"]:
                raise ValidationError("context assertion crosses mandate")
            admitted_pairs: list[tuple[str, str]] = []
            reasons: list[str] = []
            for object_id in professional_object_ids:
                decision = self._latest_evidence_decision(
                    episode_id=episode_id,
                    assertion_id=assertion_id,
                    professional_object_id=object_id,
                    intended_use=episode.payload["intended_use"],
                    at_time=episode.payload["evidence_cutoff"],
                )
                if decision is None:
                    reasons.append(f"no decision for {object_id}")
                    continue
                payload = decision.payload
                if payload["decision"] == "admit" and required_action in payload["permitted_actions"]:
                    admitted_pairs.append((assertion_id, object_id))
                else:
                    reasons.append(f"{payload['decision']} for {object_id}: {payload['rationale']}")
            if admitted_pairs:
                included_assertions.append(assertion_id)
                allowed_support_pairs.extend(
                    {
                        "assertion_id": assertion_id,
                        "professional_object_id": object_id,
                    }
                    for _, object_id in admitted_pairs
                )
            else:
                excluded_assertions.append(
                    {
                        "assertion_id": assertion_id,
                        "reason": "; ".join(reasons) or "not admitted for this use",
                    }
                )

        if not included_assertions:
            raise AuthorityError("no assertion is admitted for the requested context action")

        context_id = new_id("context")
        context_directory = ensure_inside(self.store.contexts_root, self.store.contexts_root / context_id)
        if context_directory.exists():
            raise ValidationError("context directory already exists")
        context_directory.mkdir(parents=True, mode=0o700)
        try:
            for name in (
                "evidence/sources",
                "evidence/assertions",
                "professional-objects",
                "memory",
                "output",
            ):
                (context_directory / name).mkdir(parents=True, mode=0o700, exist_ok=True)

            atomic_write(
                context_directory / "commission.json",
                canonical_json(
                    {"id": commission.id, "digest": commission.digest, "payload": commission.payload}
                ).encode("utf-8"),
            )
            atomic_write(
                context_directory / "method.json",
                canonical_json(
                    {"id": method.id, "digest": method.digest, "payload": method.payload}
                ).encode("utf-8"),
            )

            prior_perspective_id = episode.payload.get("prior_perspective_id")
            if prior_perspective_id:
                perspective = self._require_kind(prior_perspective_id, "perspective")
                perspective_items = []
                for item_id in perspective.payload["item_ids"]:
                    item = self.store.get_object(item_id)
                    perspective_items.append(
                        {"id": item.id, "kind": item.kind, "digest": item.digest, "payload": item.payload}
                    )
                atomic_write(
                    context_directory / "prior-perspective.json",
                    canonical_json(
                        {
                            "id": perspective.id,
                            "digest": perspective.digest,
                            "payload": perspective.payload,
                            "items": perspective_items,
                        }
                    ).encode("utf-8"),
                )

            for object_id in professional_object_ids:
                item = self._require_kind(object_id, "professional_object")
                atomic_write(
                    context_directory / "professional-objects" / f"{object_id}.json",
                    canonical_json({"id": item.id, "digest": item.digest, "payload": item.payload}).encode("utf-8"),
                )

            materialised_sources: dict[str, dict[str, Any]] = {}
            for assertion_id in included_assertions:
                assertion = self._require_kind(assertion_id, "assertion")
                source = self._require_kind(assertion.payload["source_id"], "source")
                if source.id not in materialised_sources:
                    blob = self.store.get_blob(source.payload["blob_digest"])
                    source_relative = Path("evidence/sources") / f"{source.id}.json"
                    source_receipt = {
                        "id": source.id,
                        "digest": source.digest,
                        "payload": source.payload,
                        "blob": {
                            "sha256": blob.digest,
                            "size": blob.size,
                            "media_type": blob.media_type,
                            "content_included": False,
                        },
                    }
                    atomic_write(
                        context_directory / source_relative,
                        canonical_json(source_receipt).encode("utf-8"),
                    )
                    materialised_sources[source.id] = {
                        "source_id": source.id,
                        "source_digest": source.digest,
                        "blob_digest": blob.digest,
                        "path": source_relative.as_posix(),
                        "content_included": False,
                    }
                atomic_write(
                    context_directory / "evidence/assertions" / f"{assertion_id}.json",
                    canonical_json(
                        {
                            "id": assertion.id,
                            "digest": assertion.digest,
                            "payload": assertion.payload,
                            "source": materialised_sources[source.id],
                        }
                    ).encode("utf-8"),
                )

            for memory_id in memory_entry_ids:
                item = self._require_kind(memory_id, "memory")
                atomic_write(
                    context_directory / "memory" / f"{memory_id}.json",
                    canonical_json({"id": item.id, "digest": item.digest, "payload": item.payload}).encode("utf-8"),
                )

            manifest = {
                "schema": "research-context-manifest/v1",
                "context_id": context_id,
                "episode_id": episode_id,
                "commission_id": commission_id,
                "method_id": method_id,
                "purpose": purpose,
                "intended_use": episode.payload["intended_use"],
                "evidence_cutoff": episode.payload["evidence_cutoff"],
                "professional_object_ids": professional_object_ids,
                "included_assertion_ids": included_assertions,
                "allowed_support_pairs": allowed_support_pairs,
                "excluded_assertions": excluded_assertions,
                "memory_entry_ids": memory_entry_ids,
                "allowed_tools": allowed_tools,
                "sources": sorted(materialised_sources.values(), key=lambda item: item["source_id"]),
                "output_contract": dict(
                    output_contract
                    or {"schema": "research-result/v1", "required_path": "result.json"}
                ),
            }
            manifest_bytes = canonical_json(manifest).encode("utf-8")
            manifest_digest = digest_bytes(manifest_bytes)
            atomic_write(context_directory / "context-manifest.json", manifest_bytes)

            context = self.store.put_object(
                "context",
                {
                    "schema": "research-context/v1",
                    "episode_id": episode_id,
                    "commission_id": commission_id,
                    "method_id": method_id,
                    "purpose": purpose,
                    "intended_use": episode.payload["intended_use"],
                    "professional_object_ids": professional_object_ids,
                    "included_assertion_ids": included_assertions,
                    "excluded_assertions": excluded_assertions,
                    "memory_entry_ids": memory_entry_ids,
                    "allowed_tools": allowed_tools,
                    "relative_directory": context_directory.relative_to(self.store.root).as_posix(),
                    "manifest_digest": manifest_digest,
                },
                object_id=context_id,
            )
            self.store.put_relation(episode_id, "has_context", context.id)
            self.store.put_relation(context.id, "uses_commission", commission_id)
            self.store.put_relation(context.id, "uses_method", method_id)
            for assertion_id in included_assertions:
                self.store.put_relation(context.id, "includes", assertion_id)
            for item in excluded_assertions:
                self.store.put_relation(
                    context.id, "excludes", item["assertion_id"], {"reason": item["reason"]}
                )
            for memory_id in memory_entry_ids:
                self.store.put_relation(context.id, "includes_memory", memory_id)
            return context
        except Exception:
            if context_directory.exists():
                shutil.rmtree(context_directory)
            raise

    def _context_directory(self, context: StoredObject) -> Path:
        return ensure_inside(
            self.store.root,
            self.store.root / safe_relative_path(context.payload["relative_directory"]),
        )
