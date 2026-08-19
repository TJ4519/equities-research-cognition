from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
from typing import Any

from .errors import IntegrityError, ValidationError
from .integrity import load_and_verify_context
from .store import StoredObject, WorkspaceStore
from .util import (
    atomic_write,
    canonical_json,
    digest_bytes,
    ensure_inside,
    read_regular_file,
    safe_relative_path,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PERSISTENT_BRANCH_PROTOCOL = (
    PACKAGE_ROOT / "agents" / "persistent_research_branch" / "protocol.md"
)


@dataclass(frozen=True)
class BranchAttemptPaths:
    root: Path
    inbox: Path
    outbox: Path
    checkpoints: Path
    source_requests: Path
    artifacts: Path
    contexts: Path
    inputs: Path


def _json(path: Path, label: str, *, max_bytes: int = 2 * 1024 * 1024) -> dict[str, Any]:
    try:
        value = json.loads(read_regular_file(path, max_bytes=max_bytes))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise IntegrityError(f"{label} must contain one JSON object")
    return value


def _protocol_bytes() -> bytes:
    if PERSISTENT_BRANCH_PROTOCOL.is_symlink() or not PERSISTENT_BRANCH_PROTOCOL.is_file():
        raise ValidationError("persistent research-branch protocol is unavailable")
    return read_regular_file(PERSISTENT_BRANCH_PROTOCOL, max_bytes=256 * 1024)


def branches_root(store: WorkspaceStore) -> Path:
    root = ensure_inside(store.control, store.control / "branches")
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink():
        raise IntegrityError("branch root cannot be a symlink")
    return root


def branch_root(store: WorkspaceStore, branch_id: str) -> Path:
    root = ensure_inside(branches_root(store), branches_root(store) / branch_id)
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink():
        raise IntegrityError("branch directory cannot be a symlink")
    return root


def attempt_paths(store: WorkspaceStore, branch_id: str, binding_id: str) -> BranchAttemptPaths:
    root = ensure_inside(
        branch_root(store, branch_id),
        branch_root(store, branch_id) / "attempts" / binding_id,
    )
    return BranchAttemptPaths(
        root=root,
        inbox=root / "inbox",
        outbox=root / "outbox",
        checkpoints=root / "outbox" / "checkpoints",
        source_requests=root / "outbox" / "source-requests",
        artifacts=root / "outbox" / "artifacts",
        contexts=root / "contexts",
        inputs=root / "inputs",
    )


def _projection(item: StoredObject) -> bytes:
    return canonical_json(
        {
            "id": item.id,
            "kind": item.kind,
            "digest": item.digest,
            "payload": item.payload,
        }
    ).encode("utf-8")


def _tree_manifest(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise IntegrityError(f"snapshot contains a symlink: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise IntegrityError(f"snapshot contains an unsupported entry: {path}")
        content = read_regular_file(path, max_bytes=25 * 1024 * 1024)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size": len(content),
                "sha256": digest_bytes(content),
            }
        )
    return rows


def _freeze_tree(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_file():
            path.chmod(0o400)
        elif path.is_dir():
            path.chmod(0o500)
    root.chmod(0o500)


def add_context_snapshot(
    store: WorkspaceStore,
    paths: BranchAttemptPaths,
    context_id: str,
) -> dict[str, Any]:
    context = store.get_object(context_id)
    source, manifest = load_and_verify_context(store, context)
    destination = ensure_inside(paths.contexts, paths.contexts / context_id)
    if destination.exists():
        receipt = _json(
            paths.contexts / f"{context_id}.snapshot.json",
            f"context snapshot receipt {context_id}",
        )
        verify_context_snapshot(paths, context_id)
        return receipt
    destination.parent.mkdir(parents=True, mode=0o700, exist_ok=True)

    def ignore(_: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {"output", ".home", ".tmp"}}

    shutil.copytree(source, destination, symlinks=False, ignore=ignore)
    tree = _tree_manifest(destination)
    receipt = {
        "schema": "research-context-snapshot/v1",
        "context_id": context.id,
        "context_digest": context.digest,
        "manifest_digest": context.payload["manifest_digest"],
        "source_manifest_digest": digest_bytes(
            canonical_json(manifest).encode("utf-8")
        ),
        "files": tree,
        "relative_path": destination.relative_to(paths.root).as_posix(),
    }
    atomic_write(
        paths.contexts / f"{context_id}.snapshot.json",
        canonical_json(receipt).encode("utf-8"),
    )
    _freeze_tree(destination)
    return receipt


def verify_context_snapshot(paths: BranchAttemptPaths, context_id: str) -> dict[str, Any]:
    receipt_path = paths.contexts / f"{context_id}.snapshot.json"
    receipt = _json(receipt_path, f"context snapshot receipt {context_id}")
    if receipt.get("schema") != "research-context-snapshot/v1":
        raise IntegrityError("context snapshot receipt has the wrong schema")
    if receipt.get("context_id") != context_id:
        raise IntegrityError("context snapshot receipt names the wrong context")
    relative = safe_relative_path(str(receipt.get("relative_path", "")))
    root = ensure_inside(paths.root, paths.root / relative)
    if root.is_symlink() or not root.is_dir():
        raise IntegrityError("context snapshot directory is unavailable")
    if _tree_manifest(root) != receipt.get("files"):
        raise IntegrityError(f"context snapshot changed: {context_id}")
    return receipt


def create_attempt_workspace(
    store: WorkspaceStore,
    *,
    branch: StoredObject,
    binding_id: str,
    context_ids: list[str],
    input_object_ids: list[str],
    resume_checkpoint_id: str | None,
) -> tuple[BranchAttemptPaths, str]:
    paths = attempt_paths(store, branch.id, binding_id)
    if paths.root.exists():
        raise ValidationError("branch attempt directory already exists")
    for directory in (
        paths.inbox,
        paths.checkpoints,
        paths.source_requests,
        paths.artifacts,
        paths.contexts,
        paths.inputs,
    ):
        directory.mkdir(parents=True, mode=0o700, exist_ok=False)
    atomic_write(paths.root / "branch.json", _projection(branch))
    protocol = _protocol_bytes()
    protocol_digest = digest_bytes(protocol)
    atomic_write(paths.root / "AGENTS.md", protocol, mode=0o400)
    context_receipts = [add_context_snapshot(store, paths, context_id) for context_id in context_ids]
    input_rows: list[dict[str, str]] = []
    for object_id in input_object_ids:
        item = store.get_object(object_id)
        target = paths.inputs / f"{object_id}.json"
        atomic_write(target, _projection(item))
        input_rows.append(
            {
                "id": item.id,
                "kind": item.kind,
                "digest": item.digest,
                "path": target.relative_to(paths.root).as_posix(),
            }
        )
    checkpoint_row: dict[str, str] | None = None
    if resume_checkpoint_id is not None:
        checkpoint = store.get_object(resume_checkpoint_id)
        if checkpoint.kind != "branch_checkpoint":
            raise ValidationError("resume object is not a branch checkpoint")
        target = paths.inputs / f"{checkpoint.id}.json"
        atomic_write(target, _projection(checkpoint))
        checkpoint_row = {
            "id": checkpoint.id,
            "digest": checkpoint.digest,
            "path": target.relative_to(paths.root).as_posix(),
        }
    manifest = {
        "schema": "research-branch-attempt-workspace/v1",
        "branch_id": branch.id,
        "branch_digest": branch.digest,
        "binding_id": binding_id,
        "standing_protocol": {
            "schema": "research-branch-standing-protocol/v1",
            "source": PERSISTENT_BRANCH_PROTOCOL.relative_to(PACKAGE_ROOT).as_posix(),
            "relative_path": "AGENTS.md",
            "sha256": protocol_digest,
        },
        "contexts": context_receipts,
        "inputs": input_rows,
        "resume_checkpoint": checkpoint_row,
        "write_roots": [
            paths.outbox.relative_to(paths.root).as_posix(),
        ],
    }
    manifest_bytes = canonical_json(manifest).encode("utf-8")
    manifest_digest = digest_bytes(manifest_bytes)
    atomic_write(paths.root / "attempt-manifest.json", manifest_bytes)
    return paths, manifest_digest


def verify_attempt_workspace(
    store: WorkspaceStore,
    *,
    branch: StoredObject,
    binding: StoredObject,
) -> tuple[BranchAttemptPaths, dict[str, Any]]:
    paths = attempt_paths(store, branch.id, binding.id)
    if paths.root.is_symlink() or not paths.root.is_dir():
        raise IntegrityError("branch attempt directory is unavailable")
    branch_projection = _json(paths.root / "branch.json", "branch projection")
    if branch_projection != json.loads(_projection(branch)):
        raise IntegrityError("branch projection changed")
    manifest_bytes = read_regular_file(
        paths.root / "attempt-manifest.json",
        max_bytes=2 * 1024 * 1024,
    )
    if digest_bytes(manifest_bytes) != binding.payload["attempt_manifest_digest"]:
        raise IntegrityError("branch attempt manifest changed")
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrityError("branch attempt manifest is invalid JSON") from exc
    if not isinstance(manifest, dict):
        raise IntegrityError("branch attempt manifest must be an object")
    if manifest.get("branch_id") != branch.id or manifest.get("binding_id") != binding.id:
        raise IntegrityError("branch attempt manifest names the wrong binding")
    protocol = manifest.get("standing_protocol")
    if not isinstance(protocol, dict):
        raise IntegrityError("branch attempt lacks a standing protocol")
    if protocol.get("schema") != "research-branch-standing-protocol/v1":
        raise IntegrityError("branch standing protocol has the wrong schema")
    if protocol.get("relative_path") != "AGENTS.md":
        raise IntegrityError("branch standing protocol uses an unexpected path")
    protocol_bytes = read_regular_file(paths.root / "AGENTS.md", max_bytes=256 * 1024)
    if digest_bytes(protocol_bytes) != protocol.get("sha256"):
        raise IntegrityError("branch standing protocol changed")
    for row in manifest.get("contexts", []):
        verify_context_snapshot(paths, row["context_id"])
    for row in manifest.get("inputs", []):
        item = store.get_object(row["id"])
        path = ensure_inside(paths.root, paths.root / safe_relative_path(row["path"]))
        if _json(path, f"branch input {item.id}") != json.loads(_projection(item)):
            raise IntegrityError(f"branch input changed: {item.id}")
    checkpoint = manifest.get("resume_checkpoint")
    if checkpoint:
        item = store.get_object(checkpoint["id"])
        path = ensure_inside(paths.root, paths.root / safe_relative_path(checkpoint["path"]))
        if _json(path, f"resume checkpoint {item.id}") != json.loads(_projection(item)):
            raise IntegrityError("resume checkpoint projection changed")
    from .codex_session import verify_codex_session_control

    verify_codex_session_control(paths, manifest)
    return paths, manifest


def write_instruction(
    paths: BranchAttemptPaths,
    *,
    sequence: int,
    kind: str,
    payload: dict[str, Any],
) -> tuple[Path, str]:
    filename = f"{sequence:04d}-{kind}.json"
    target = ensure_inside(paths.inbox, paths.inbox / filename)
    if target.exists():
        raise ValidationError("branch instruction path already exists")
    content = canonical_json(payload).encode("utf-8")
    atomic_write(target, content)
    return target, digest_bytes(content)


def read_outbox_json(paths: BranchAttemptPaths, relative_path: str, label: str) -> dict[str, Any]:
    relative = safe_relative_path(relative_path)
    target = ensure_inside(paths.outbox, paths.outbox / relative)
    return _json(target, label)


def artifact_population(paths: BranchAttemptPaths) -> dict[str, Path]:
    result: dict[str, Path] = {}
    if not paths.artifacts.exists():
        return result
    for path in sorted(paths.artifacts.rglob("*")):
        if path.is_symlink():
            raise IntegrityError(f"branch artifact population contains a symlink: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise IntegrityError(f"branch artifact population contains a non-file: {path}")
        relative = Path("artifacts") / path.relative_to(paths.artifacts)
        result[relative.as_posix()] = path
    return result
