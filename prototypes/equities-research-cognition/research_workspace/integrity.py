from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import IntegrityError, ValidationError
from .store import StoredObject, WorkspaceStore
from .util import digest_bytes, ensure_inside, read_regular_file, safe_relative_path


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

    _projection(store, directory / "commission.json", manifest["commission_id"], "commission projection")
    _projection(store, directory / "method.json", manifest["method_id"], "method projection")
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
                {"id": item.id, "kind": item.kind, "digest": item.digest, "payload": item.payload}
            )
        if value.get("items") != expected_items:
            raise IntegrityError("prior perspective items changed")
    elif prior_path.exists():
        raise IntegrityError("context contains an undeclared prior perspective")

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
        receipt = _projection(store, receipt_path, source.id, f"source receipt {source.id}")
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
    return directory, manifest
