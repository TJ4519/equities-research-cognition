from __future__ import annotations

import argparse
from pathlib import Path
import sys

from harness.ntm.adapter import NtmAdapter

from .branch_supervisor import BranchSupervisor
from .errors import WorkspaceError
from .ntm_research import NtmResearchController
from .service import ResearchWorkspace
from .util import canonical_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-supervise",
        description="Advance one persistent NTM-managed Codex research branch",
    )
    parser.add_argument("root")
    parser.add_argument("branch")
    parser.add_argument("--ntm-binary", required=True)
    parser.add_argument("--ntm-timeout", type=int, default=90)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        workspace = ResearchWorkspace.open(Path(args.root))
        supervisor = BranchSupervisor(
            workspace,
            NtmResearchController(
                NtmAdapter(
                    Path(args.ntm_binary),
                    timeout_seconds=args.ntm_timeout,
                )
            ),
        )
        report = supervisor.step(args.branch)
    except WorkspaceError as exc:
        print(canonical_json({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(
        canonical_json(
            {
                "ok": True,
                "result": {
                    "branch_id": report.branch_id,
                    "binding_id": report.binding_id,
                    "action": report.action,
                    "object_id": report.object_id,
                    "instruction_id": report.instruction_id,
                    "state": report.state,
                },
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
