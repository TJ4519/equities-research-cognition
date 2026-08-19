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
)


class DiscoveryContextServiceMixin:
    """Build broad discovery context that grants no claim-support authority."""

    def build_discovery_context(
        self,
        *,
        episode_id: str,
        commission_id: str,
        method_id: str,
        purpose: str,
        professional_object_ids: list[str],
        source_ids: list[str] | None = None,
        memory_entry_ids: list[str] | None = None,
        allow_codex_search: bool = False,
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
            professional_object_ids,
            "discovery professional objects",
        )
        source_ids = require_string_list(
            source_ids or [],
            "discovery sources",
            allow_empty=True,
        )
        memory_entry_ids = require_string_list(
            memory_entry_ids or [],
            "discovery memory entries",
            allow_empty=True,
        )
        for object_id in professional_object_ids:
            item = self._require_kind(object_id, "professional_object")
            if item.payload["mandate_id"] != episode.payload["mandate_id"]:
                raise ValidationError("discovery object crosses mandate")
            if item.payload["authority"] not in {"human_confirmed", "policy"}:
                raise AuthorityError(
                    "discovery context requires a confirmed professional object"
                )
        for memory_id in memory_entry_ids:
            item = self._require_kind(memory_id, "memory")
            if item.payload["mandate_id"] != episode.payload["mandate_id"]:
                raise ValidationError("discovery memory crosses mandate")
            if item.payload["authority"] not in {"human_confirmed", "policy"}:
                raise AuthorityError(
                    "model-proposed memory cannot enter a discovery context"
                )
            if item.payload.get("effective_until") and not self._active_at(
                item.payload,
                episode.payload["evidence_cutoff"],
            ):
                raise AuthorityError("expired memory cannot enter a context")

        sources: list[StoredObject] = []
        for source_id in source_ids:
            source = self._require_kind(source_id, "source")
            if source.payload["mandate_id"] != episode.payload["mandate_id"]:
                raise ValidationError("discovery source crosses mandate")
            rights = source.payload.get("rights", {})
            if not isinstance(rights, dict) or rights.get("model_access") is not True:
                raise AuthorityError(
                    "source rights do not permit full-content model discovery"
                )
            sources.append(source)

        context_id = new_id("context")
        directory = ensure_inside(
            self.store.contexts_root,
            self.store.contexts_root / context_id,
        )
        if directory.exists():
            raise ValidationError("context directory already exists")
        directory.mkdir(parents=True, mode=0o700)
        try:
            for name in (
                "evidence/discovery-sources",
                "evidence/assertions",
                "professional-objects",
                "memory",
                "output",
            ):
                (directory / name).mkdir(parents=True, mode=0o700, exist_ok=True)
            atomic_write(
                directory / "commission.json",
                canonical_json(
                    {
                        "id": commission.id,
                        "digest": commission.digest,
                        "payload": commission.payload,
                    }
                ).encode("utf-8"),
            )
            atomic_write(
                directory / "method.json",
                canonical_json(
                    {"id": method.id, "digest": method.digest, "payload": method.payload}
                ).encode("utf-8"),
            )
            prior_id = episode.payload.get("prior_perspective_id")
            if prior_id:
                perspective = self._require_kind(prior_id, "perspective")
                items = []
                for item_id in perspective.payload["item_ids"]:
                    item = self.store.get_object(item_id)
                    items.append(
                        {
                            "id": item.id,
                            "kind": item.kind,
                            "digest": item.digest,
                            "payload": item.payload,
                        }
                    )
                atomic_write(
                    directory / "prior-perspective.json",
                    canonical_json(
                        {
                            "id": perspective.id,
                            "digest": perspective.digest,
                            "payload": perspective.payload,
                            "items": items,
                        }
                    ).encode("utf-8"),
                )
            for object_id in professional_object_ids:
                item = self._require_kind(object_id, "professional_object")
                atomic_write(
                    directory / "professional-objects" / f"{object_id}.json",
                    canonical_json(
                        {"id": item.id, "digest": item.digest, "payload": item.payload}
                    ).encode("utf-8"),
                )
            materialised_sources: list[dict[str, Any]] = []
            for source in sources:
                blob = self.store.get_blob(source.payload["blob_digest"])
                content = self.store.read_blob(blob.digest)
                suffix = Path(source.payload["filename"]).suffix or ".bin"
                content_relative = (
                    Path("evidence/discovery-sources")
                    / f"{source.id}-{blob.digest}{suffix}"
                )
                receipt_relative = (
                    Path("evidence/discovery-sources") / f"{source.id}.json"
                )
                atomic_write(directory / content_relative, content, mode=0o400)
                receipt = {
                    "id": source.id,
                    "digest": source.digest,
                    "payload": source.payload,
                    "blob": {
                        "sha256": blob.digest,
                        "size": blob.size,
                        "media_type": blob.media_type,
                        "content_included": True,
                        "content_path": content_relative.as_posix(),
                    },
                }
                atomic_write(
                    directory / receipt_relative,
                    canonical_json(receipt).encode("utf-8"),
                )
                materialised_sources.append(
                    {
                        "source_id": source.id,
                        "source_digest": source.digest,
                        "blob_digest": blob.digest,
                        "receipt_path": receipt_relative.as_posix(),
                        "content_path": content_relative.as_posix(),
                        "content_included": True,
                    }
                )
            for memory_id in memory_entry_ids:
                item = self._require_kind(memory_id, "memory")
                atomic_write(
                    directory / "memory" / f"{memory_id}.json",
                    canonical_json(
                        {"id": item.id, "digest": item.digest, "payload": item.payload}
                    ).encode("utf-8"),
                )
            allowed_tools = ["source_request"]
            if allow_codex_search:
                allowed_tools.append("codex_search")
            manifest = {
                "schema": "research-context-manifest/v1",
                "context_kind": "discovery",
                "context_id": context_id,
                "episode_id": episode_id,
                "commission_id": commission_id,
                "method_id": method_id,
                "purpose": purpose,
                "intended_use": episode.payload["intended_use"],
                "evidence_cutoff": episode.payload["evidence_cutoff"],
                "professional_object_ids": professional_object_ids,
                "included_assertion_ids": [],
                "allowed_support_pairs": [],
                "excluded_assertions": [],
                "memory_entry_ids": memory_entry_ids,
                "allowed_tools": allowed_tools,
                "source_ids": source_ids,
                "sources": materialised_sources,
                "output_contract": dict(
                    output_contract
                    or {
                        "schema": "research-discovery-result/v1",
                        "source_requests": True,
                        "supported_claims": False,
                    }
                ),
            }
            manifest_bytes = canonical_json(manifest).encode("utf-8")
            manifest_digest = digest_bytes(manifest_bytes)
            atomic_write(directory / "context-manifest.json", manifest_bytes)
            context = self.store.put_object(
                "context",
                {
                    "schema": "research-context/v1",
                    "context_kind": "discovery",
                    "episode_id": episode_id,
                    "commission_id": commission_id,
                    "method_id": method_id,
                    "purpose": purpose,
                    "intended_use": episode.payload["intended_use"],
                    "professional_object_ids": professional_object_ids,
                    "included_assertion_ids": [],
                    "excluded_assertions": [],
                    "memory_entry_ids": memory_entry_ids,
                    "allowed_tools": allowed_tools,
                    "source_ids": source_ids,
                    "relative_directory": directory.relative_to(self.store.root).as_posix(),
                    "manifest_digest": manifest_digest,
                },
                object_id=context_id,
            )
            self.store.put_relation(episode_id, "has_context", context.id)
            self.store.put_relation(context.id, "uses_commission", commission_id)
            self.store.put_relation(context.id, "uses_method", method_id)
            for source_id in source_ids:
                self.store.put_relation(context.id, "includes_discovery_source", source_id)
            for memory_id in memory_entry_ids:
                self.store.put_relation(context.id, "includes_memory", memory_id)
            return context
        except Exception:
            if directory.exists():
                shutil.rmtree(directory)
            raise
