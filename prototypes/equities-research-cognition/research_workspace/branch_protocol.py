from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .branch_workspace import (
    BranchAttemptPaths,
    create_attempt_workspace,
    verify_attempt_workspace,
)
from .errors import IntegrityError, ValidationError
from .store import StoredObject, WorkspaceStore
from .util import atomic_write, canonical_json, digest_bytes, read_regular_file


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_SOURCE = PACKAGE_ROOT / "agents" / "persistent_research_branch" / "protocol.md"


def _protocol_bytes() -> bytes:
    if PROTOCOL_SOURCE.is_symlink() or not PROTOCOL_SOURCE.is_file():
        raise ValidationError("persistent research-branch protocol is unavailable")
    return read_regular_file(PROTOCOL_SOURCE, max_bytes=256 * 1024)


def _manifest(paths: BranchAttemptPaths) -> dict[str, Any]:
    try:
        value = json.loads(
            read_regular_file(
                paths.root / "attempt-manifest.json",
                max_bytes=2 * 1024 * 1024,
            )
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrityError("branch attempt manifest is invalid JSON") from exc
    if not isinstance(value, dict):
        raise IntegrityError("branch attempt manifest must be an object")
    return value


def create_persistent_attempt_workspace(
    store: WorkspaceStore,
    *,
    branch: StoredObject,
    binding_id: str,
    context_ids: list[str],
    input_object_ids: list[str],
    resume_checkpoint_id: str | None,
) -> tuple[BranchAttemptPaths, str]:
    paths, _ = create_attempt_workspace(
        store,
        branch=branch,
        binding_id=binding_id,
        context_ids=context_ids,
        input_object_ids=input_object_ids,
        resume_checkpoint_id=resume_checkpoint_id,
    )
    protocol = _protocol_bytes()
    protocol_digest = digest_bytes(protocol)
    atomic_write(paths.root / "AGENTS.md", protocol, mode=0o400)
    manifest = _manifest(paths)
    manifest["standing_protocol"] = {
        "schema": "research-branch-standing-protocol/v1",
        "source": PROTOCOL_SOURCE.relative_to(PACKAGE_ROOT).as_posix(),
        "relative_path": "AGENTS.md",
        "sha256": protocol_digest,
    }
    content = canonical_json(manifest).encode("utf-8")
    atomic_write(paths.root / "attempt-manifest.json", content)
    return paths, digest_bytes(content)


def verify_persistent_attempt_workspace(
    store: WorkspaceStore,
    *,
    branch: StoredObject,
    binding: StoredObject,
) -> tuple[BranchAttemptPaths, dict[str, Any]]:
    paths, manifest = verify_attempt_workspace(
        store,
        branch=branch,
        binding=binding,
    )
    protocol = manifest.get("standing_protocol")
    if not isinstance(protocol, dict):
        raise IntegrityError("branch attempt lacks a standing protocol")
    if protocol.get("schema") != "research-branch-standing-protocol/v1":
        raise IntegrityError("branch standing protocol has the wrong schema")
    if protocol.get("relative_path") != "AGENTS.md":
        raise IntegrityError("branch standing protocol uses an unexpected path")
    content = read_regular_file(paths.root / "AGENTS.md", max_bytes=256 * 1024)
    if digest_bytes(content) != protocol.get("sha256"):
        raise IntegrityError("branch standing protocol changed")
    return paths, manifest
