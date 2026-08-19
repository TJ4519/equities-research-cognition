from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .errors import AuthorityError


class ConformanceRunPolicyMixin:
    """Keep the direct runner limited to deterministic conformance work."""

    def run_context(
        self,
        *,
        context_id: str,
        argv: list[str],
        timeout_seconds: int = 300,
        extra_environment: Mapping[str, str] | None = None,
    ):
        executable = Path(argv[0]).name.casefold() if argv else ""
        if executable == "codex" or executable.startswith("codex-"):
            raise AuthorityError(
                "Codex research must run in a persistent NTM-managed session"
            )
        return super().run_context(
            context_id=context_id,
            argv=argv,
            timeout_seconds=timeout_seconds,
            extra_environment=extra_environment,
        )
