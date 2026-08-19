from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shlex
from typing import Any

from .errors import IntegrityError, ValidationError
from .store import WorkspaceStore
from .util import atomic_write, canonical_json, digest_bytes, ensure_inside, read_regular_file


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

    def payload(self) -> dict[str, Any]:
        return {
            "schema": "research-codex-launch/v1",
            "codex_binary_path": self.codex_binary_path,
            "codex_binary_digest": self.codex_binary_digest,
            "launcher_path": self.launcher_path,
            "launcher_digest": self.launcher_digest,
            "ntm_config_path": self.ntm_config_path,
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


def control_root(store: WorkspaceStore) -> Path:
    root = ensure_inside(store.control, store.control / "codex-sessions")
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink():
        raise IntegrityError("Codex session-control root cannot be a symlink")
    return root


def build_codex_session_control(
    store: WorkspaceStore,
    *,
    codex_binary: Path,
    model: str,
    search_enabled: bool,
    sandbox: str = "workspace-write",
    approval_policy: str = "never",
) -> CodexSessionControl:
    """Build one content-addressed interactive Codex launcher for NTM.

    NTM supplies the exact persistent-session working directory. The launcher
    starts the ordinary interactive Codex CLI in that directory. It never
    invokes ``codex exec``.
    """

    model = _require_model(model)
    if sandbox not in SANDBOX_MODES:
        raise ValidationError("Codex sandbox mode is unsupported")
    if approval_policy not in APPROVAL_POLICIES:
        raise ValidationError("Codex approval policy is unsupported")
    codex_binary, codex_bytes = _regular_executable(codex_binary)
    root = control_root(store)

    argv = [
        str(codex_binary),
        "--sandbox",
        sandbox,
        "--ask-for-approval",
        approval_policy,
    ]
    if search_enabled:
        argv.append("--search")
    command = " ".join(shlex.quote(item) for item in argv)
    launcher = (
        "#!/bin/sh\n"
        "set -eu\n"
        f"exec {command} --cd \"$PWD\" -m \"$1\"\n"
    ).encode("utf-8")
    launcher_digest = digest_bytes(launcher)
    launcher_path = root / f"codex-{launcher_digest}.sh"
    if launcher_path.exists():
        if read_regular_file(launcher_path, max_bytes=256 * 1024) != launcher:
            raise IntegrityError("content-addressed Codex launcher changed")
    else:
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
    config_path = root / f"ntm-{config_digest}.toml"
    if config_path.exists():
        if read_regular_file(config_path, max_bytes=256 * 1024) != config:
            raise IntegrityError("content-addressed NTM Codex config changed")
    else:
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
    manifest_path = root / f"control-{config_digest}.json"
    content = canonical_json(control.payload()).encode("utf-8")
    if manifest_path.exists():
        if read_regular_file(manifest_path, max_bytes=256 * 1024) != content:
            raise IntegrityError("content-addressed Codex control manifest changed")
    else:
        atomic_write(manifest_path, content)
    return control


def verify_codex_session_control(payload: dict[str, Any]) -> CodexSessionControl:
    if payload.get("schema") != "research-codex-launch/v1":
        raise IntegrityError("Codex launch object has the wrong schema")
    model = _require_model(str(payload.get("model", "")))
    sandbox = str(payload.get("sandbox", ""))
    approval_policy = str(payload.get("approval_policy", ""))
    if sandbox not in SANDBOX_MODES or approval_policy not in APPROVAL_POLICIES:
        raise IntegrityError("Codex launch names an unsupported policy")
    codex_path = Path(str(payload.get("codex_binary_path", "")))
    launcher_path = Path(str(payload.get("launcher_path", "")))
    config_path = Path(str(payload.get("ntm_config_path", "")))
    for path, label, limit in (
        (codex_path, "Codex executable", 512 * 1024 * 1024),
        (launcher_path, "Codex launcher", 256 * 1024),
        (config_path, "NTM Codex config", 256 * 1024),
    ):
        if path.is_symlink() or not path.is_absolute() or not path.is_file():
            raise IntegrityError(f"{label} is unavailable")
        read_regular_file(path, max_bytes=limit)
    codex_content = read_regular_file(codex_path, max_bytes=512 * 1024 * 1024)
    launcher = read_regular_file(launcher_path, max_bytes=256 * 1024)
    config = read_regular_file(config_path, max_bytes=256 * 1024)
    if digest_bytes(codex_content) != payload.get("codex_binary_digest"):
        raise IntegrityError("bound Codex executable changed")
    if digest_bytes(launcher) != payload.get("launcher_digest"):
        raise IntegrityError("Codex launcher changed")
    if digest_bytes(config) != payload.get("ntm_config_digest"):
        raise IntegrityError("NTM Codex config changed")
    if b"codex exec" in launcher or b"--cd \"$PWD\"" not in launcher:
        raise IntegrityError("Codex launcher violates the persistent-session contract")
    expected_search = bool(payload.get("search_enabled"))
    if (b" --search " in launcher) != expected_search:
        raise IntegrityError("Codex launcher search policy disagrees with its record")
    if model.encode("utf-8") not in config:
        raise IntegrityError("NTM Codex config does not contain the bound model")
    return CodexSessionControl(
        codex_binary_path=str(codex_path),
        codex_binary_digest=str(payload["codex_binary_digest"]),
        launcher_path=str(launcher_path),
        launcher_digest=str(payload["launcher_digest"]),
        ntm_config_path=str(config_path),
        ntm_config_digest=str(payload["ntm_config_digest"]),
        model=model,
        sandbox=sandbox,
        approval_policy=approval_policy,
        search_enabled=expected_search,
    )
