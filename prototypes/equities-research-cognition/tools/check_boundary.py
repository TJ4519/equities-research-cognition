#!/usr/bin/env python3
"""Fail closed when the cognition package gains an unreviewed runtime authority."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parents[1]
PRODUCT_ROOT = PACKAGE_ROOT / "product"
HARNESS_ROOT = PACKAGE_ROOT / "harness"
NTM_ROOT = HARNESS_ROOT / "ntm"
LOCAL_WORKSPACE_ROOT = PACKAGE_ROOT / "research_workspace"
LOCAL_PROCESS_PATH = LOCAL_WORKSPACE_ROOT / "runtime.py"
SCENARIO_ROOT = PACKAGE_ROOT / "scenarios"
RUNTIME_SURFACES = (
    PRODUCT_ROOT,
    HARNESS_ROOT,
    LOCAL_WORKSPACE_ROOT,
    PACKAGE_ROOT / "agents",
    PACKAGE_ROOT / "workbenches",
    PACKAGE_ROOT / "manage.py",
    PACKAGE_ROOT / "pyproject.toml",
)
REQUIRED_SURFACES = RUNTIME_SURFACES + (
    SCENARIO_ROOT / "adversarial",
    SCENARIO_ROOT / "protected" / "README.md",
    PACKAGE_ROOT / "skills" / "README.md",
    PACKAGE_ROOT / "evidence" / "README.md",
)
VACATED_AUTHORITIES = (
    WORKSPACE_ROOT / "product",
    WORKSPACE_ROOT / "tests" / "product",
    WORKSPACE_ROOT / "scripts" / "check_clean_product_boundary.py",
    WORKSPACE_ROOT / "scripts" / "classify_clean_product_loc.py",
)
FORBIDDEN_REFERENCES = (
    "rie.judgment",
    "rie/judgment",
    "observed_live",
    "codex_telemetry",
    "PersistentRoleEpisodePort",
    "EpisodeAdmissionService",
    "EpisodeRoleBinding",
    "EpisodeAdmission",
    "persistent_interactive_codex",
    "nvidia-q1-fy27-w7b-analyst-20260715T172023Z",
)
ALLOWED_MODULE_ROOTS = {
    "__future__",
    "argparse",
    "base64",
    "collections",
    "contextlib",
    "ctypes",
    "dataclasses",
    "datetime",
    "decimal",
    "django",
    "getpass",
    "google",
    "harness",
    "hashlib",
    "http",
    "ipaddress",
    "json",
    "mimetypes",
    "opentelemetry",
    "os",
    "pathlib",
    "platform",
    "product",
    "re",
    "research_workspace",
    "selectors",
    "shlex",
    "shutil",
    "signal",
    "socket",
    "sqlite3",
    "stat",
    "struct",
    "subprocess",
    "sys",
    "tempfile",
    "threading",
    "time",
    "typing",
    "urllib",
    "uuid",
    "zipfile",
}
ALLOWED_OS_IMPORTS = {
    "O_CLOEXEC",
    "O_CREAT",
    "O_DIRECTORY",
    "O_EXCL",
    "O_NOFOLLOW",
    "O_RDONLY",
    "O_TRUNC",
    "O_WRONLY",
    "chmod",
    "environ",
    "fdopen",
    "fsync",
    "fstat",
    "geteuid",
    "getgid",
    "getpgid",
    "getpid",
    "getuid",
    "killpg",
    "open",
    "readlink",
    "replace",
    "unlink",
    "walk",
}
FORBIDDEN_CALLS = {
    "__import__",
    "eval",
    "exec",
    "compile",
    "importlib.import_module",
    "runpy.run_module",
    "runpy.run_path",
    "os.system",
    "os.popen",
    "subprocess.run",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.Popen",
}


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _surface_paths(surfaces: tuple[Path, ...]) -> tuple[list[Path], list[str]]:
    paths: list[Path] = []
    errors: list[str] = []
    for surface in surfaces:
        if not surface.exists() and not surface.is_symlink():
            errors.append(f"missing package surface: {surface}")
        elif surface.is_dir():
            paths.extend(surface.rglob("*"))
        else:
            paths.append(surface)
    return paths, errors


def violations(runtime_root: Path | None = None) -> list[str]:
    surfaces = RUNTIME_SURFACES if runtime_root is None else (runtime_root,)
    paths, found = _surface_paths(surfaces)

    if runtime_root is None:
        for surface in REQUIRED_SURFACES:
            if not surface.exists() and not surface.is_symlink():
                found.append(f"missing package surface: {surface}")
        for path in VACATED_AUTHORITIES:
            if path.exists() or path.is_symlink():
                found.append(f"vacated root authority still exists: {path}")

    for root in (PRODUCT_ROOT, HARNESS_ROOT, LOCAL_WORKSPACE_ROOT, SCENARIO_ROOT):
        if not root.exists():
            continue
        for cache in root.rglob("*.pyc"):
            if PACKAGE_ROOT / ".venv" in cache.parents:
                continue
            stem = cache.name.split(".cpython-", 1)[0]
            source = cache.parent.parent / f"{stem}.py"
            if cache.parent.name == "__pycache__" and not source.exists():
                found.append(f"orphan executable bytecode in package: {cache}")

    for path in sorted(set(paths)):
        if ".venv" in path.parts or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            found.append(f"symlink forbidden in package runtime: {path}")
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            found.append(f"binary file requires explicit review: {path}")
            continue
        for token in FORBIDDEN_REFERENCES:
            if token in text:
                found.append(f"forbidden reference {token!r}: {path}")
        if path.suffix != ".py":
            continue
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            found.append(f"invalid Python source {path}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                names = []
            for name in names:
                if isinstance(node, ast.ImportFrom) and node.level > 0:
                    continue
                root = name.split(".", 1)[0]
                if root == "os":
                    allowed = (
                        isinstance(node, ast.ImportFrom)
                        and node.module == "os"
                        and all(alias.name in ALLOWED_OS_IMPORTS for alias in node.names)
                    )
                    if not allowed:
                        found.append(
                            f"unapproved runtime module import {name!r}: "
                            f"{path}:{node.lineno}"
                        )
                elif root and root not in ALLOWED_MODULE_ROOTS:
                    found.append(
                        f"unapproved runtime module import {name!r}: "
                        f"{path}:{node.lineno}"
                    )
            if isinstance(node, ast.Call):
                name = dotted_name(node.func)
                allowed_process_path = (
                    path.is_relative_to(NTM_ROOT) or path == LOCAL_PROCESS_PATH
                )
                allowed_process = allowed_process_path and name in {
                    "subprocess.run",
                    "subprocess.Popen",
                }
                shell = next(
                    (item.value for item in node.keywords if item.arg == "shell"),
                    None,
                )
                if allowed_process and not (
                    isinstance(shell, ast.Constant) and shell.value is False
                ):
                    found.append(
                        f"approved subprocess must set shell=False: {path}:{node.lineno}"
                    )
                elif not allowed_process and (
                    name in FORBIDDEN_CALLS or name.startswith("subprocess.")
                ):
                    found.append(
                        f"dynamic execution primitive {name!r}: "
                        f"{path}:{node.lineno}"
                    )
            if isinstance(node, ast.Name) and node.id == "__builtins__":
                found.append(
                    f"dynamic builtins access forbidden: {path}:{node.lineno}"
                )
    return sorted(set(found))


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else None
    errors = violations(root)
    if errors:
        print("cognition package boundary: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    label = root if root is not None else "all runtime-bearing package surfaces"
    print(f"cognition package boundary: passed ({label})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
