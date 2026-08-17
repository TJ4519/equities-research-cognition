"""Allowlisted subprocess boundary for the separately installed NTM binary."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
from typing import Mapping


@dataclass(frozen=True)
class ExecutionResult:
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    response: object | None
    timed_out: bool = False


class NtmAdapter:
    def __init__(self, binary: Path, timeout_seconds: int = 90) -> None:
        self.binary = Path(binary)
        self.timeout_seconds = timeout_seconds
        if not self.binary.is_absolute():
            raise ValueError("NTM binary must be pinned by absolute path")

    def _base(self, config: Path) -> list[str]:
        return [str(self.binary), f"--config={config}"]

    def spawn_command(
        self, session: str, working_dir: Path, role_name: str, config: Path
    ) -> list[str]:
        return self._base(config) + [
            f"--robot-spawn={session}", "--spawn-cod=1", "--spawn-no-user",
            f"--spawn-dir={working_dir}", "--spawn-wait", "--timeout=60s",
            "--spawn-safety", f"--spawn-names={role_name}", "--json",
        ]

    def add_command(self, session: str, model: str, config: Path) -> list[str]:
        return self._base(config) + [
            "add", session, f"--cod=1:{model}", "--no-cass-context", "--json",
        ]

    def status_command(self, session: str, config: Path) -> list[str]:
        return self._base(config) + ["status", session, "--json"]

    def send_command(
        self, session: str, index: int, message: Path, config: Path
    ) -> list[str]:
        return self._base(config) + [
            f"--robot-send={session}", f"--panes={index}",
            f"--msg-file={message}", "--track", "--timeout=60s", "--json",
        ]

    def completion_command(
        self, session: str, index: int, config: Path
    ) -> list[str]:
        return self._base(config) + [
            f"--robot-wait={session}", "--wait-until=complete",
            f"--panes={index}", "--wait-exit-on-error", "--timeout=1s", "--json",
        ]

    def stop_command(self, session: str, config: Path) -> list[str]:
        return self._base(config) + ["kill", session, "--force", "--json"]

    def execute(
        self, argv: list[str], *, environment: Mapping[str, str] | None = None
    ) -> ExecutionResult:
        self._validate(argv)
        try:
            completed = subprocess.run(
                argv,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                shell=False,
                timeout=self.timeout_seconds,
                env=dict(environment) if environment is not None else None,
            )
            stdout, stderr = completed.stdout, completed.stderr
            code, timed_out = completed.returncode, False
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or b"", exc.stderr or b""
            code, timed_out = None, True
        except OSError as exc:
            stdout, stderr, code, timed_out = b"", str(exc).encode(), None, False
        try:
            response = json.loads(stdout)
        except (UnicodeDecodeError, json.JSONDecodeError):
            response = None
        return ExecutionResult(code, stdout, stderr, response, timed_out)

    def _validate(self, argv: list[str]) -> None:
        if (
            len(argv) < 2
            or argv[0] != str(self.binary)
            or not self.binary.is_file()
            or not argv[1].startswith("--config=")
        ):
            raise ValueError("control command does not use pinned NTM")
        config = Path(argv[1][9:])
        if not config.is_absolute() or not config.is_file() or config.is_symlink():
            raise ValueError("NTM config is not one exact regular file")
        session, valid = "", False
        if len(argv) == 11 and argv[2].startswith("--robot-spawn="):
            session = argv[2][14:]
            directory, role = Path(argv[5][12:]), argv[9][14:]
            valid = (
                argv[3:5] == ["--spawn-cod=1", "--spawn-no-user"]
                and argv[5].startswith("--spawn-dir=")
                and directory.is_absolute() and directory.is_dir()
                and argv[6:9] == [
                    "--spawn-wait", "--timeout=60s", "--spawn-safety"
                ]
                and argv[9].startswith("--spawn-names=")
                and re.fullmatch(r"[a-z][a-z_]{0,31}", role) is not None
                and argv[10] == "--json"
            )
        elif len(argv) == 7 and argv[2] == "add":
            session, model = argv[3], argv[4][8:]
            valid = (
                argv[4].startswith("--cod=1:")
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/@:+-]{0,127}", model)
                is not None
                and argv[5:] == ["--no-cass-context", "--json"]
            )
        elif len(argv) == 5 and argv[2] == "status":
            session, valid = argv[3], argv[4] == "--json"
        elif len(argv) == 6 and argv[2] == "kill":
            session, valid = argv[3], argv[4:] == ["--force", "--json"]
        elif len(argv) == 8 and argv[2].startswith("--robot-send="):
            session, message = argv[2][13:], Path(argv[4][11:])
            valid = (
                re.fullmatch(r"--panes=[1-9][0-9]*", argv[3]) is not None
                and argv[4].startswith("--msg-file=")
                and message.is_absolute() and message.is_file()
                and not message.is_symlink()
                and argv[5:] == ["--track", "--timeout=60s", "--json"]
            )
        elif len(argv) == 8 and argv[2].startswith("--robot-wait="):
            session = argv[2][13:]
            valid = (
                argv[3] == "--wait-until=complete"
                and re.fullmatch(r"--panes=[1-9][0-9]*", argv[4]) is not None
                and argv[5:] == [
                    "--wait-exit-on-error", "--timeout=1s", "--json"
                ]
            )
        if (
            not valid
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", session) is None
        ):
            raise ValueError("NTM command is outside the campaign allowlist")
