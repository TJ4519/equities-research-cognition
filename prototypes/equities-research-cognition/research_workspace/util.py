from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from os import O_RDONLY, close as os_close, fchmod, fdopen, fsync, open as os_open, replace
import tempfile
from typing import Any
import uuid

from .errors import IntegrityError, ValidationError


PREFIXES = {
    "mandate": "man",
    "perspective": "per",
    "episode": "ep",
    "commission": "com",
    "source": "src",
    "assertion": "ast",
    "professional_object": "pob",
    "evidence_decision": "evd",
    "method": "mth",
    "context": "ctx",
    "research_branch": "brn",
    "codex_launch": "cdx",
    "ntm_binding": "ntb",
    "branch_instruction": "bin",
    "branch_event": "bev",
    "branch_ack": "bak",
    "branch_checkpoint": "chk",
    "source_request": "srq",
    "run": "run",
    "claim": "clm",
    "result": "res",
    "artifact": "art",
    "decision": "dec",
    "correction": "cor",
    "memory": "mem",
    "evaluation_case": "eval",
    "replay": "rpl",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def new_id(kind: str) -> str:
    try:
        prefix = PREFIXES[kind]
    except KeyError as exc:
        raise ValidationError(f"unsupported object kind: {kind}") from exc
    return f"{prefix}_{uuid.uuid4().hex}"


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValidationError("record is not canonical JSON") from exc


def digest_json(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_bytes(content: bytes) -> str:
    return sha256(content).hexdigest()


def require_text(value: Any, label: str, *, limit: int | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} is required")
    text = value.strip()
    if limit is not None and len(text) > limit:
        raise ValidationError(f"{label} exceeds {limit} characters")
    return text


def require_string_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValidationError(f"{label} must be a non-empty list")
    result: list[str] = []
    for item in value:
        result.append(require_text(item, label))
    if len(set(result)) != len(result):
        raise ValidationError(f"{label} contains duplicates")
    return result


def ensure_inside(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValidationError(f"path escapes workspace: {candidate}") from exc
    return candidate


def safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValidationError(f"unsafe relative path: {value}")
    return path


def atomic_write(path: Path, content: bytes, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parent = path.parent.resolve()
    if path.exists() and path.is_symlink():
        raise ValidationError(f"refusing to replace symlink: {path}")
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=parent)
    temporary = Path(temporary_name)
    try:
        fchmod(fd, mode)
        with fdopen(fd, "wb", closefd=True) as handle:
            handle.write(content)
            handle.flush()
            fsync(handle.fileno())
        replace(temporary, path)
        directory_fd = os_open(parent, O_RDONLY)
        try:
            fsync(directory_fd)
        finally:
            os_close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_regular_file(path: Path, *, max_bytes: int | None = None) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValidationError(f"expected one regular file: {path}")
    size = path.stat().st_size
    if max_bytes is not None and size > max_bytes:
        raise ValidationError(f"file exceeds {max_bytes} bytes: {path}")
    content = path.read_bytes()
    if max_bytes is not None and len(content) > max_bytes:
        raise ValidationError(f"file exceeds {max_bytes} bytes: {path}")
    return content


def verify_digest(content: bytes, expected: str, label: str) -> None:
    observed = digest_bytes(content)
    if observed != expected:
        raise IntegrityError(f"{label} digest mismatch: expected {expected}, observed {observed}")
