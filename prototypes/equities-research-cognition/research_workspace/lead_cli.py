from __future__ import annotations

import argparse
from pathlib import Path
import sys

from harness.ntm.adapter import NtmAdapter

from .errors import WorkspaceError
from .governed_research_lead import GovernedResearchLead
from .ntm_research import NtmResearchController
from .service import ResearchWorkspace
from .util import canonical_json


def _json_list(value: str, label: str) -> list[str]:
    import json

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be valid JSON") from exc
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise argparse.ArgumentTypeError(f"{label} must be a JSON string list")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-lead",
        description="Persistent NTM-managed Codex research lead",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("root")
    start.add_argument("--episode", required=True)
    start.add_argument("--commission", required=True)
    start.add_argument("--method", required=True)
    start.add_argument("--professional-object-ids-json", required=True)
    start.add_argument("--ntm-binary", required=True)
    start.add_argument("--codex-binary", required=True)
    start.add_argument("--model", required=True)
    start.add_argument("--actor", required=True)
    start.add_argument("--session")
    start.add_argument("--ntm-timeout", type=int, default=90)

    validate = sub.add_parser("validate-plan")
    validate.add_argument("root")
    validate.add_argument("artifact")

    materialise = sub.add_parser("materialise")
    materialise.add_argument("root")
    materialise.add_argument("artifact")
    materialise.add_argument("proposal")
    materialise.add_argument("--context-ids-json", required=True)
    materialise.add_argument("--actor", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        workspace = ResearchWorkspace.open(Path(args.root))
        lead = GovernedResearchLead(workspace)
        if args.command == "start":
            controller = NtmResearchController(
                NtmAdapter(
                    Path(args.ntm_binary),
                    timeout_seconds=args.ntm_timeout,
                )
            )
            result = lead.start(
                episode_id=args.episode,
                commission_id=args.commission,
                method_id=args.method,
                professional_object_ids=_json_list(
                    args.professional_object_ids_json,
                    "professional object ids",
                ),
                controller=controller,
                codex_binary=Path(args.codex_binary),
                model=args.model,
                actor=args.actor,
                session=args.session,
            ).__dict__
        elif args.command == "validate-plan":
            result = lead.validate_plan(args.artifact)
        elif args.command == "materialise":
            result = lead.materialise_proposal(
                artifact_id=args.artifact,
                proposal_id=args.proposal,
                context_ids=_json_list(args.context_ids_json, "context ids"),
                actor=args.actor,
            ).__dict__
        else:
            raise AssertionError(f"unhandled lead command: {args.command}")
    except WorkspaceError as exc:
        print(canonical_json({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(canonical_json({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
