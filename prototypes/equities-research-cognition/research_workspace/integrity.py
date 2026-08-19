from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import IntegrityError, ValidationError
from .store import StoredObject, WorkspaceStore
from .util import digest_bytes, ensure_inside, read_regular_file, safe_relative_path


CONTEXT_KINDS = {"support", "discovery"}


def _json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(read_regular_file(path, max_bytes=2 * 1024 * 1024))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise IntegrityError(f"{label} must contain one JSON object")
    return value


def _projection(store: WorkspaceStore, path: Path, object_id: str, label: str) -> StoredObject:
    item = store.get_object(object_id)
    value = _json(path, label)
    if value.get("id") != item.id or value.get("digest") != item.digest:
        raise IntegrityError(f"{label} identity changed")
    if value.get("payload") != item.payload:
        raise IntegrityError(f"{label} payload changed")
    return item


def _verify_common_context(
    store: WorkspaceStore,
    context: StoredObject,
    directory: Path,
    manifest: dict[str, Any],
) -> None:
    for key in (
        "episode_id",
        "commission_id",
        "method_id",
        "purpose",
        "intended_use",
        "professional_object_ids",
        "included_assertion_ids",
        "excluded_assertions",
        "memory_entry_ids",
        "allowed_tools",
    ):
        if manifest.get(key) != context.payload.get(key):
            raise IntegrityError(f"sealed context manifest disagrees on {key}")
    context_kind = manifest.get("context_kind", "support")
    if context_kind not in CONTEXT_KINDS:
        raise IntegrityError("sealed context kind is unsupported")
    if context.payload.get("context_kind", "support") != context_kind:
        raise IntegrityError("sealed context manifest disagrees on context kind")
    if context.payload.get("source_ids", []) != manifest.get("source_ids", []):
        raise IntegrityError("sealed context manifest disagrees on discovery sources")

    _projection(
        store,
        directory / "commission.json",
        manifest["commission_id"],
        "commission projection",
    )
    _projection(
        store,
        directory / "method.json",
        manifest["method_id"],
        "method projection",
    )
    for object_id in manifest["professional_object_ids"]:
        _projection(
            store,
            directory / "professional-objects" / f"{object_id}.json",
            object_id,
            f"professional-object projection {object_id}",
        )
    for memory_id in manifest["memory_entry_ids"]:
        _projection(
            store,
            directory / "memory" / f"{memory_id}.json",
            memory_id,
            f"memory projection {memory_id}",
        )

    episode = store.get_object(manifest["episode_id"])
    prior_id = episode.payload.get("prior_perspective_id")
    prior_path = directory / "prior-perspective.json"
    if prior_id:
        value = _json(prior_path, "prior perspective projection")
        prior = store.get_object(prior_id)
        if value.get("id") != prior.id or value.get("digest") != prior.digest:
            raise IntegrityError("prior perspective identity changed")
        if value.get("payload") != prior.payload:
            raise IntegrityError("prior perspective payload changed")
        expected_items = []
        for item_id in prior.payload["item_ids"]:
            item = store.get_object(item_id)
            expected_items.append(
                {
                    "id": item.id,
                    "kind": item.kind,
                    "digest": item.digest,
                    "payload": item.payload,
                }
            )
        if value.get("items") != expected_items:
            raise IntegrityError("prior perspective items changed")
    elif prior_path.exists():
        raise IntegrityError("context contains an undeclared prior perspective")


def _verify_support_context(
    store: WorkspaceStore,
    directory: Path,
    manifest: dict[str, Any],
) -> None:
    if manifest.get("source_ids", []):
        raise IntegrityError("support context cannot contain discovery source ids")
    source_refs = {item["source_id"]: item for item in manifest.get("sources", [])}
    included = set(manifest["included_assertion_ids"])
    excluded = {item["assertion_id"] for item in manifest["excluded_assertions"]}
    assertion_directory = directory / "evidence/assertions"
    for assertion_id in included:
        assertion = store.get_object(assertion_id)
        source = store.get_object(assertion.payload["source_id"])
        source_ref = source_refs.get(source.id)
        if source_ref is None:
            raise IntegrityError(f"context omits source receipt for {assertion_id}")
        receipt_path = directory / safe_relative_path(source_ref["path"])
        receipt = _projection(
            store,
            receipt_path,
            source.id,
            f"source receipt {source.id}",
        )
        blob = store.get_blob(receipt.payload["blob_digest"])
        store.read_blob(blob.digest)
        receipt_json = _json(receipt_path, f"source receipt {source.id}")
        if receipt_json.get("blob") != {
            "sha256": blob.digest,
            "size": blob.size,
            "media_type": blob.media_type,
            "content_included": False,
        }:
            raise IntegrityError(f"source receipt blob identity changed: {source.id}")
        assertion_path = assertion_directory / f"{assertion_id}.json"
        value = _json(assertion_path, f"assertion projection {assertion_id}")
        if value.get("id") != assertion.id or value.get("digest") != assertion.digest:
            raise IntegrityError(f"assertion projection changed: {assertion_id}")
        if value.get("payload") != assertion.payload or value.get("source") != source_ref:
            raise IntegrityError(f"assertion projection payload changed: {assertion_id}")

    observed = {
        path.stem
        for path in assertion_directory.glob("*.json")
        if path.is_file() and not path.is_symlink()
    }
    if observed != included:
        raise IntegrityError("sealed context assertion population differs from manifest")
    for assertion_id in excluded:
        if (assertion_directory / f"{assertion_id}.json").exists():
            raise IntegrityError(f"excluded assertion entered sealed context: {assertion_id}")
    discovery_directory = directory / "evidence/discovery-sources"
    if discovery_directory.exists() and any(discovery_directory.iterdir()):
        raise IntegrityError("support context contains full discovery source material")


def _verify_discovery_context(
    store: WorkspaceStore,
    directory: Path,
    manifest: dict[str, Any],
) -> None:
    if manifest["included_assertion_ids"] or manifest.get("allowed_support_pairs", []):
        raise IntegrityError("discovery context cannot carry claim-support authority")
    if manifest["excluded_assertions"]:
        raise IntegrityError("discovery context cannot disguise assertion admission decisions")
    assertion_directory = directory / "evidence/assertions"
    if any(assertion_directory.iterdir()):
        raise IntegrityError("discovery context contains assertion projections")
    source_ids = manifest.get("source_ids", [])
    if not isinstance(source_ids, list) or len(source_ids) != len(set(source_ids)):
        raise IntegrityError("discovery source population is malformed")
    refs = {item["source_id"]: item for item in manifest.get("sources", [])}
    if set(refs) != set(source_ids):
        raise IntegrityError("discovery source receipts differ from the manifest")
    for source_id in source_ids:
        source = store.get_object(source_id)
        if source.kind != "source":
            raise IntegrityError("discovery context names a non-source object")
        rights = source.payload.get("rights", {})
        if not isinstance(rights, dict) or rights.get("model_access") is not True:
            raise IntegrityError("discovery source no longer permits model access")
        ref = refs[source_id]
        if ref.get("content_included") is not True:
            raise IntegrityError("discovery source lacks full-content authority")
        receipt_path = directory / safe_relative_path(ref["receipt_path"])
        content_path = directory / safe_relative_path(ref["content_path"])
        receipt = _projection(
            store,
            receipt_path,
            source_id,
            f"discovery source receipt {source_id}",
        )
        blob = store.get_blob(receipt.payload["blob_digest"])
        expected_content = store.read_blob(blob.digest)
        observed_content = read_regular_file(content_path, max_bytes=25 * 1024 * 1024)
        if observed_content != expected_content:
            raise IntegrityError(f"discovery source content changed: {source_id}")
        receipt_json = _json(receipt_path, f"discovery source receipt {source_id}")
        if receipt_json.get("blob") != {
            "sha256": blob.digest,
            "size": blob.size,
            "media_type": blob.media_type,
            "content_included": True,
            "content_path": ref["content_path"],
        }:
            raise IntegrityError(f"discovery source blob identity changed: {source_id}")
    support_source_directory = directory / "evidence/sources"
    if support_source_directory.exists() and any(support_source_directory.iterdir()):
        raise IntegrityError("discovery context contains support-only source receipts")


def load_and_verify_context(
    store: WorkspaceStore,
    context: StoredObject | str,
) -> tuple[Path, dict[str, Any]]:
    if isinstance(context, str):
        context = store.get_object(context)
    if context.kind != "context":
        raise ValidationError(f"{context.id} is not a context")
    store.verify_object(context.id)
    directory = ensure_inside(
        store.root,
        store.root / safe_relative_path(context.payload["relative_directory"]),
    )
    if directory.is_symlink() or not directory.is_dir():
        raise IntegrityError("sealed context directory is unavailable")

    manifest_path = directory / "context-manifest.json"
    manifest_bytes = read_regular_file(manifest_path, max_bytes=2 * 1024 * 1024)
    if digest_bytes(manifest_bytes) != context.payload["manifest_digest"]:
        raise IntegrityError("sealed context manifest digest mismatch")
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrityError("sealed context manifest is invalid JSON") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != "research-context-manifest/v1":
        raise IntegrityError("sealed context manifest has the wrong schema")
    if manifest.get("context_id") != context.id:
        raise IntegrityError("sealed context manifest names the wrong context")

    _verify_common_context(store, context, directory, manifest)
    if manifest.get("context_kind", "support") == "discovery":
        _verify_discovery_context(store, directory, manifest)
    else:
        _verify_support_context(store, directory, manifest)
    return directory, manifest
