from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

from .errors import WorkspaceError
from .replay import ReplayEngine
from .service import ResearchWorkspace
from .util import canonical_json


def object_view(item) -> dict[str, Any]:
    return {
        "id": item.id,
        "kind": item.kind,
        "digest": item.digest,
        "created_at": item.created_at,
        "payload": item.payload,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research",
        description="Local-first research workspace",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("root")
    init.add_argument("--title", default="Local research workspace")

    status = sub.add_parser("status")
    status.add_argument("root")

    show = sub.add_parser("show")
    show.add_argument("root")
    show.add_argument("object_id")

    explain = sub.add_parser("explain")
    explain.add_argument("root")
    explain.add_argument("target")

    verify = sub.add_parser("verify")
    verify.add_argument("root")
    verify.add_argument("target")

    replay = sub.add_parser("replay")
    replay.add_argument("root")
    replay.add_argument("evaluation_case")
    replay.add_argument("--timeout", type=int, default=300)

    export = sub.add_parser("proof-export")
    export.add_argument("root")
    export.add_argument("target")
    export.add_argument("destination")
    return parser


def run_command(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "init":
        workspace = ResearchWorkspace.initialise(Path(args.root), title=args.title)
        return workspace.status()
    workspace = ResearchWorkspace.open(Path(args.root))
    if args.command == "status":
        return workspace.status()
    if args.command == "show":
        return object_view(workspace.store.get_object(args.object_id))
    engine = ReplayEngine(workspace.store)
    if args.command == "explain":
        return engine.explain(args.target)
    if args.command == "verify":
        return engine.verify_target(args.target)
    if args.command == "replay":
        return object_view(
            engine.replay_evaluation_case(
                args.evaluation_case,
                timeout_seconds=args.timeout,
            )
        )
    if args.command == "proof-export":
        path = engine.export_proof_pack(args.target, Path(args.destination))
        return {"destination": str(path)}
    raise AssertionError(f"unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_command(args)
    except WorkspaceError as exc:
        print(canonical_json({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(canonical_json({"ok": True, "result": result}))
    return 0
