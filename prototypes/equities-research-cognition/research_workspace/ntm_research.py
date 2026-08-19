from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from harness.ntm.adapter import ExecutionResult, NtmAdapter


@dataclass(frozen=True)
class NtmReceipt:
    """One exact NTM control result.

    A successful receipt proves that NTM accepted one control operation. It does
    not prove that Codex understood the research branch or completed useful
    work.
    """

    action: str
    argv: tuple[str, ...]
    exit_code: int | None
    timed_out: bool
    stdout: bytes
    stderr: bytes
    response: Any

    @property
    def succeeded(self) -> bool:
        return not self.timed_out and self.exit_code == 0


class NtmControl(Protocol):
    """Machine-facing NTM surface used by the research workspace.

    Tests may supply an in-memory implementation. Production uses
    :class:`NtmResearchController`, which delegates every process call to the
    existing allowlisted NTM adapter. No direct Codex process is authorised.
    """

    def spawn(
        self,
        *,
        session: str,
        working_directory: Path,
        role_name: str,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt: ...

    def send(
        self,
        *,
        session: str,
        pane: int,
        message: Path,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt: ...

    def status(
        self,
        *,
        session: str,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt: ...

    def completion(
        self,
        *,
        session: str,
        pane: int,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt: ...

    def stop(
        self,
        *,
        session: str,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt: ...


class NtmResearchController:
    """Persistent Codex session control through NTM.

    NTM remains the sole Codex research runtime. This controller does not launch
    Codex itself and deliberately exposes no ``codex exec`` path.
    """

    def __init__(self, adapter: NtmAdapter) -> None:
        self.adapter = adapter

    @staticmethod
    def _receipt(action: str, argv: list[str], result: ExecutionResult) -> NtmReceipt:
        return NtmReceipt(
            action=action,
            argv=tuple(argv),
            exit_code=result.exit_code,
            timed_out=result.timed_out,
            stdout=result.stdout,
            stderr=result.stderr,
            response=result.response,
        )

    def _execute(
        self,
        *,
        action: str,
        argv: list[str],
        environment: Mapping[str, str] | None,
    ) -> NtmReceipt:
        return self._receipt(
            action,
            argv,
            self.adapter.execute(argv, environment=environment),
        )

    def spawn(
        self,
        *,
        session: str,
        working_directory: Path,
        role_name: str,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt:
        return self._execute(
            action="spawn",
            argv=self.adapter.spawn_command(session, working_directory, role_name, config),
            environment=environment,
        )

    def send(
        self,
        *,
        session: str,
        pane: int,
        message: Path,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt:
        return self._execute(
            action="send",
            argv=self.adapter.send_command(session, pane, message, config),
            environment=environment,
        )

    def status(
        self,
        *,
        session: str,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt:
        return self._execute(
            action="status",
            argv=self.adapter.status_command(session, config),
            environment=environment,
        )

    def completion(
        self,
        *,
        session: str,
        pane: int,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt:
        return self._execute(
            action="completion",
            argv=self.adapter.completion_command(session, pane, config),
            environment=environment,
        )

    def stop(
        self,
        *,
        session: str,
        config: Path,
        environment: Mapping[str, str] | None = None,
    ) -> NtmReceipt:
        return self._execute(
            action="stop",
            argv=self.adapter.stop_command(session, config),
            environment=environment,
        )
