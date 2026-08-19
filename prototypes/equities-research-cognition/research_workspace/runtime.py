from __future__ import annotations

from dataclasses import dataclass
import json
from os import getpgid, killpg
from pathlib import Path
import shutil
import signal
import subprocess
from typing import Any, Mapping

from .errors import IntegrityError, RuntimeFailure, ValidationError
from .store import WorkspaceStore
from .util import (
    atomic_write,
    canonical_json,
    digest_bytes,
    ensure_inside,
    read_regular_file,
    require_string_list,
    require_text,
    safe_relative_path,
    utc_now,
)


@dataclass(frozen=True)
class ProcessReceipt:
    argv: list[str]
    working_directory: str
    pid: int
    process_group: int | None
    started_at: str
    ended_at: str
    exit_code: int | None
    signal: int | None
    timed_out: bool
    stdout: bytes
    stderr: bytes


@dataclass(frozen=True)
class OutputPopulation:
    files: list[dict[str, Any]]
    total_bytes: int
    result: dict[str, Any]


class DirectProcessAdapter:
    """Direct child-process boundary for a sealed local context.

    The adapter binds a process to one exact working directory and a minimal
    environment. It does not claim operating-system sandbox isolation.
    """

    MAX_FILES = 100
    MAX_TOTAL_BYTES = 25 * 1024 * 1024
    MAX_SINGLE_BYTES = 10 * 1024 * 1024

    def __init__(self, store: WorkspaceStore) -> None:
        self.store = store

    def execute(
        self,
        *,
        context_directory: Path,
        argv: list[str],
        timeout_seconds: int = 300,
        extra_environment: Mapping[str, str] | None = None,
    ) -> ProcessReceipt:
        context_directory = ensure_inside(self.store.contexts_root, context_directory)
        if context_directory.is_symlink() or not context_directory.is_dir():
            raise ValidationError("context directory must be one exact regular directory")
        if not isinstance(argv, list) or not argv:
            raise ValidationError("runtime argv must be a non-empty list")
        executable = Path(argv[0])
        if not executable.is_absolute() or executable.is_symlink() or not executable.is_file():
            raise ValidationError("runtime executable must be one exact absolute regular file")
        if timeout_seconds < 1 or timeout_seconds > 3600:
            raise ValidationError("runtime timeout is outside the supported range")

        output_directory = context_directory / "output"
        output_directory.mkdir(mode=0o700, exist_ok=True)
        if output_directory.is_symlink():
            raise ValidationError("output directory cannot be a symlink")
        if any(output_directory.iterdir()):
            raise ValidationError("output directory must be empty before a run")

        home = context_directory / ".home"
        temporary = context_directory / ".tmp"
        home.mkdir(mode=0o700, exist_ok=True)
        temporary.mkdir(mode=0o700, exist_ok=True)
        environment = {
            "HOME": str(home),
            "TMPDIR": str(temporary),
            "RESEARCH_CONTEXT_ROOT": str(context_directory),
            "RESEARCH_OUTPUT_DIR": str(output_directory),
            "PYTHONNOUSERSITE": "1",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        }
        if extra_environment:
            for key, value in extra_environment.items():
                if not isinstance(key, str) or not key or "\x00" in key:
                    raise ValidationError("runtime environment contains an invalid key")
                if not isinstance(value, str) or "\x00" in value:
                    raise ValidationError("runtime environment contains an invalid value")
                environment[key] = value

        started_at = utc_now()
        process = subprocess.Popen(
            argv,
            cwd=context_directory,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            start_new_session=True,
        )
        try:
            process_group = getpgid(process.pid)
        except OSError:
            process_group = None
        timed_out = False
        caught_signal: int | None = None
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            if process_group is not None:
                try:
                    killpg(process_group, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            stdout, stderr = process.communicate()
        ended_at = utc_now()
        if process.returncode is not None and process.returncode < 0:
            caught_signal = -process.returncode
        return ProcessReceipt(
            argv=list(argv),
            working_directory=str(context_directory),
            pid=process.pid,
            process_group=process_group,
            started_at=started_at,
            ended_at=ended_at,
            exit_code=process.returncode,
            signal=caught_signal,
            timed_out=timed_out,
            stdout=stdout,
            stderr=stderr,
        )

    def seal_output(self, context_directory: Path) -> OutputPopulation:
        context_directory = ensure_inside(self.store.contexts_root, context_directory)
        output_directory = context_directory / "output"
        if output_directory.is_symlink() or not output_directory.is_dir():
            raise RuntimeFailure("runtime output directory is unavailable")
        files: list[dict[str, Any]] = []
        total_bytes = 0
        for path in sorted(output_directory.rglob("*")):
            if path.is_symlink():
                raise RuntimeFailure(f"runtime output contains a symlink: {path}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise RuntimeFailure(f"runtime output contains a non-file: {path}")
            relative = path.relative_to(output_directory)
            safe_relative_path(relative.as_posix())
            content = read_regular_file(path, max_bytes=self.MAX_SINGLE_BYTES)
            total_bytes += len(content)
            if total_bytes > self.MAX_TOTAL_BYTES:
                raise RuntimeFailure("runtime output exceeds the aggregate byte limit")
            files.append(
                {
                    "path": relative.as_posix(),
                    "size": len(content),
                    "sha256": digest_bytes(content),
                }
            )
            if len(files) > self.MAX_FILES:
                raise RuntimeFailure("runtime output exceeds the file-count limit")
        if not files:
            raise RuntimeFailure("runtime produced no output files")
        result_path = output_directory / "result.json"
        if result_path.is_symlink() or not result_path.is_file():
            raise RuntimeFailure("runtime did not produce result.json")
        try:
            result = json.loads(read_regular_file(result_path, max_bytes=self.MAX_SINGLE_BYTES))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeFailure("result.json is not valid UTF-8 JSON") from exc
        if not isinstance(result, dict):
            raise RuntimeFailure("result.json must contain one JSON object")
        manifest = {
            "schema": "research-output-population/v1",
            "files": files,
            "total_bytes": total_bytes,
        }
        atomic_write(
            output_directory / "host-output-manifest.json",
            canonical_json(manifest).encode("utf-8"),
        )
        return OutputPopulation(files=files, total_bytes=total_bytes, result=result)

    @staticmethod
    def validate_result(
        result: dict[str, Any],
        *,
        included_assertion_ids: set[str],
        professional_object_ids: set[str],
        allowed_support_pairs: set[tuple[str, str]],
        output_files: set[str],
    ) -> dict[str, Any]:
        if result.get("schema") != "research-result/v1":
            raise RuntimeFailure("result.json requires schema research-result/v1")
        summary = require_text(result.get("summary"), "result summary")
        claims = result.get("claims", [])
        artifacts = result.get("artifacts", [])
        memory_proposals = result.get("memory_proposals", [])
        if not isinstance(claims, list):
            raise RuntimeFailure("result claims must be a list")
        if not isinstance(artifacts, list):
            raise RuntimeFailure("result artifacts must be a list")
        if not isinstance(memory_proposals, list):
            raise RuntimeFailure("result memory proposals must be a list")

        validated_claims: list[dict[str, Any]] = []
        seen_claim_ids: set[str] = set()
        for raw in claims:
            if not isinstance(raw, dict):
                raise RuntimeFailure("each result claim must be an object")
            claim_id = require_text(raw.get("claim_id"), "claim id")
            if claim_id in seen_claim_ids:
                raise RuntimeFailure("result claim identifiers must be unique")
            seen_claim_ids.add(claim_id)
            text = require_text(raw.get("text"), "claim text")
            relations = raw.get("support_relations", [])
            if not isinstance(relations, list) or not relations:
                raise RuntimeFailure("claim support relations must be a non-empty list")
            support: list[str] = []
            affected: list[str] = []
            normalised_relations: list[dict[str, str]] = []
            seen_relations: set[tuple[str, str]] = set()
            for relation in relations:
                if not isinstance(relation, dict):
                    raise RuntimeFailure("claim support relation must be an object")
                assertion_id = require_text(relation.get("assertion_id"), "claim supporting assertion")
                object_id = require_text(
                    relation.get("professional_object_id"), "claim professional object"
                )
                pair = (assertion_id, object_id)
                if pair in seen_relations:
                    raise RuntimeFailure("claim support relations contain duplicates")
                seen_relations.add(pair)
                if assertion_id not in included_assertion_ids:
                    raise RuntimeFailure(
                        "claim cites an assertion outside its sealed context: " + assertion_id
                    )
                if object_id not in professional_object_ids:
                    raise RuntimeFailure(
                        "claim names a professional object outside its context: " + object_id
                    )
                if pair not in allowed_support_pairs:
                    raise RuntimeFailure(
                        "claim uses an unpermitted assertion-to-object relation: "
                        + assertion_id
                        + " -> "
                        + object_id
                    )
                support.append(assertion_id)
                affected.append(object_id)
                normalised_relations.append(
                    {"assertion_id": assertion_id, "professional_object_id": object_id}
                )
            uncertainty = require_string_list(
                raw.get("uncertainty", []), "claim uncertainty", allow_empty=True
            )
            validated_claims.append(
                {
                    "claim_id": claim_id,
                    "text": text,
                    "support_relations": normalised_relations,
                    "supporting_assertion_ids": sorted(set(support)),
                    "professional_object_ids": sorted(set(affected)),
                    "uncertainty": uncertainty,
                }
            )

        validated_artifacts: list[dict[str, Any]] = []
        for raw in artifacts:
            if not isinstance(raw, dict):
                raise RuntimeFailure("each result artifact must be an object")
            path = safe_relative_path(require_text(raw.get("path"), "artifact path")).as_posix()
            if path in {"result.json", "host-output-manifest.json"}:
                raise RuntimeFailure("result metadata cannot be declared as an artifact")
            if path not in output_files:
                raise RuntimeFailure(f"declared artifact is missing from output: {path}")
            validated_artifacts.append(
                {
                    "path": path,
                    "kind": require_text(raw.get("kind"), "artifact kind"),
                    "title": require_text(raw.get("title"), "artifact title"),
                    "media_type": require_text(
                        raw.get("media_type", "application/octet-stream"),
                        "artifact media type",
                    ),
                }
            )

        validated_memory: list[dict[str, Any]] = []
        for raw in memory_proposals:
            if not isinstance(raw, dict):
                raise RuntimeFailure("each memory proposal must be an object")
            validated_memory.append(
                {
                    "content": require_text(raw.get("content"), "memory proposal content"),
                    "scope": raw.get("scope", {}),
                    "reason": require_text(raw.get("reason"), "memory proposal reason"),
                }
            )
            if not isinstance(validated_memory[-1]["scope"], dict):
                raise RuntimeFailure("memory proposal scope must be a JSON object")

        return {
            "schema": "research-result/v1",
            "summary": summary,
            "claims": validated_claims,
            "artifacts": validated_artifacts,
            "memory_proposals": validated_memory,
        }


def copy_context_for_replay(source: Path, destination: Path) -> None:
    """Copy a sealed context without its historical output population."""
    if destination.exists():
        raise ValidationError("replay destination already exists")
    destination.mkdir(parents=True, mode=0o700)
    for item in source.iterdir():
        if item.name in {"output", ".home", ".tmp"}:
            continue
        target = destination / item.name
        if item.is_symlink():
            raise IntegrityError(f"sealed context contains a symlink: {item}")
        if item.is_dir():
            shutil.copytree(item, target, symlinks=False)
        elif item.is_file():
            shutil.copy2(item, target)
        else:
            raise IntegrityError(f"sealed context contains an unsupported entry: {item}")
    (destination / "output").mkdir(mode=0o700)
