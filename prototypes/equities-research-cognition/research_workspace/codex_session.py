from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shlex
from typing import Any

from .branch_workspace import BranchAttemptPaths
from .errors import IntegrityError, ValidationError
from .util import (
    atomic_write,
    canonical_json,
    digest_bytes,
    ensure_inside,
    read_regular_file,
)


MODEL_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/@:+-]{0,127}")
SANDBOX_MODES = {"workspace-write"}
APPROVAL_POLICIES = {"never"}


@dataclass(frozen=True)
class CodexSessionControl:
    codex_binary_path: str
    codex_binary_digest: str
    launcher_path: str
    launcher_digest: str
    ntm_config_path: str
    ntm_config_digest: str
    model: str
    sandbox: str
    approval_policy: str
    search_enabled: bool

    def manifest(self, *, root: Path) -> dict[str, Any]:
        return {
            "schema": "research-codex-session-control/v1",
            "codex_binary_path": self.codex_binary_path,
            "codex_binary_digest": self.codex_binary_digest,
            "launcher_path": Path(self.launcher_path).relative_to(root).as_posix(),
            "launcher_digest": self.launcher_digest,
            "ntm_config_path": Path(self.ntm_config_path).relative_to(root).as_posix(),
            "ntm_config_digest": self.ntm_config_digest,
            "model": self.model,
            "sandbox": self.sandbox,
            "approval_policy": self.approval_policy,
            "search_enabled": self.search_enabled,
        }


def _require_model(model: str) -> str:
    if not isinstance(model, str) or MODEL_PATTERN.fullmatch(model) is None:
        raise ValidationError("Codex model identifier is invalid")
    return model


def _regular_executable(path: Path) -> tuple[Path, bytes]:
    path = path.expanduser()
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ValidationError("Codex executable must be one exact absolute regular file")
    path = path.resolve()
    content = read_regular_file(path, max_bytes=512 * 1024 * 1024)
    return path, content


def _toml_literal(value: str, label: str) -> str:
    if "\x00" in value or "\n" in value or "\r" in value or "'''" in value:
        raise ValidationError(f"{label} cannot be represented in the NTM config")
    return value


def build_codex_session_control(
    paths: BranchAttemptPaths,
    *,
    codex_binary: Path,
    model: str,
    search_enabled: bool,
    sandbox: str = "workspace-write",
    approval_policy: str = "never",
) -> CodexSessionControl:
    """Build one content-addressed interactive Codex launcher for NTM.

    The launcher starts the ordinary interactive Codex CLI. It never invokes
    ``codex exec``. NTM remains responsible for creating and preserving the
    session.
    """

    model = _require_model(model)
    if sandbox not in SANDBOX_MODES:
        raise ValidationError("Codex sandbox mode is unsupported")
    if approval_policy not in APPROVAL_POLICIES:
        raise ValidationError("Codex approval policy is unsupported")
    codex_binary, codex_bytes = _regular_executable(codex_binary)
    control_root = ensure_inside(paths.root, paths.root / "_control")
    control_root.mkdir(mode=0o700, exist_ok=False)

    argv = [
        str(codex_binary),
        "--sandbox",
        sandbox,
        "--ask-for-approval",
        approval_policy,
    ]
    if search_enabled:
        argv.append("--search")
    argv.extend(["--cd", str(paths.root)])
    command = " ".join(shlex.quote(item) for item in argv)
    launcher = (
        "#!/bin/sh\n"
        "set -eu\n"
        f"exec {command} -m \"$1\"\n"
    ).encode("utf-8")
    launcher_digest = digest_bytes(launcher)
    launcher_path = control_root / f"codex-{launcher_digest}.sh"
    atomic_write(launcher_path, launcher, mode=0o700)

    launcher_literal = _toml_literal(str(launcher_path), "Codex launcher path")
    model_literal = _toml_literal(model, "Codex model")
    config = (
        "[agents]\n"
        f"codex = '''{launcher_literal} "
        "{{shellQuote (.Model | default \""
        f"{model_literal}"
        "\")}}'''\n"
        "[models]\n"
        f'default_codex = "{model_literal}"\n'
    ).encode("utf-8")
    config_digest = digest_bytes(config)
    config_path = control_root / f"ntm-{config_digest}.toml"
    atomic_write(config_path, config, mode=0o600)

    control = CodexSessionControl(
        codex_binary_path=str(codex_binary),
        codex_binary_digest=digest_bytes(codex_bytes),
        launcher_path=str(launcher_path),
        launcher_digest=launcher_digest,
        ntm_config_path=str(config_path),
        ntm_config_digest=config_digest,
        model=model,
        sandbox=sandbox,
        approval_policy=approval_policy,
        search_enabled=bool(search_enabled),
    )
    atomic_write(
        control_root / "control-manifest.json",
        canonical_json(control.manifest(root=paths.root)).encode("utf-8"),
    )
    return control


def attach_control_to_attempt(
    paths: BranchAttemptPaths,
    control: CodexSessionControl,
) -> str:
    manifest_path = paths.root / "attempt-manifest.json"
    try:
        manifest = json.loads(read_regular_file(manifest_path, max_bytes=2 * 1024 * 1024))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrityError("branch attempt manifest is invalid JSON") from exc
    if not isinstance(manifest, dict):
        raise IntegrityError("branch attempt manifest must be an object")
    if "codex_session_control" in manifest:
        raise IntegrityError("branch attempt already has a Codex session control")
    manifest["codex_session_control"] = control.manifest(root=paths.root)
    content = canonical_json(manifest).encode("utf-8")
    atomic_write(manifest_path, content)
    return digest_bytes(content)


def verify_codex_session_control(
    paths: BranchAttemptPaths,
    manifest: dict[str, Any],
) -> CodexSessionControl:
    raw = manifest.get("codex_session_control")
    if not isinstance(raw, dict) or raw.get("schema") != "research-codex-session-control/v1":
        raise IntegrityError("branch attempt lacks a valid Codex session control")
    model = _require_model(str(raw.get("model", "")))
    sandbox = str(raw.get("sandbox", ""))
    approval_policy = str(raw.get("approval_policy", ""))
    if sandbox not in SANDBOX_MODES or approval_policy not in APPROVAL_POLICIES:
        raise IntegrityError("Codex session control names an unsupported policy")
    codex_path = Path(str(raw.get("codex_binary_path", "")))
    if codex_path.is_symlink() or not codex_path.is_absolute() or not codex_path.is_file():
        raise IntegrityError("bound Codex executable is unavailable")
    codex_content = read_regular_file(codex_path, max_bytes=512 * 1024 * 1024)
    if digest_bytes(codex_content) != raw.get("codex_binary_digest"):
        raise IntegrityError("bound Codex executable changed")
    launcher_path = ensure_inside(
        paths.root,
        paths.root / Path(str(raw.get("launcher_path", ""))),
    )
    config_path = ensure_inside(
        paths.root,
        paths.root / Path(str(raw.get("ntm_config_path", ""))),
    )
    launcher = read_regular_file(launcher_path, max_bytes=256 * 1024)
    config = read_regular_file(config_path, max_bytes=256 * 1024)
    if digest_bytes(launcher) != raw.get("launcher_digest"):
        raise IntegrityError("Codex launcher changed")
    if digest_bytes(config) != raw.get("ntm_config_digest"):
        raise IntegrityError("NTM Codex configuration changed")
    if b"codex exec" in launcher or b" exec " not in launcher:
        raise IntegrityError("Codex launcher violates the persistent-session contract")
    return CodexSessionControl(
        codex_binary_path=str(codex_path),
        codex_binary_digest=str(raw["codex_binary_digest"]),
        launcher_path=str(launcher_path),
        launcher_digest=str(raw["launcher_digest"]),
        ntm_config_path=str(config_path),
        ntm_config_digest=str(raw["ntm_config_digest"]),
        model=model,
        sandbox=sandbox,
        approval_policy=approval_policy,
        search_enabled=bool(raw.get("search_enabled")),
    )
