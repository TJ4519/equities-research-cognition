from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from harness.ntm.adapter import NtmAdapter

from .errors import WorkspaceError
from .ntm_research import NtmResearchController
from .service import ResearchWorkspace
from .util import canonical_json


COMMANDS = {
    "discovery-context-build",
    "branch-create",
    "branch-launch",
    "branch-state",
    "branch-acknowledge",
    "branch-source-request",
    "branch-checkpoint",
    "branch-context-add",
    "branch-steer",
    "branch-status",
    "branch-completion",
    "branch-collect",
    "branch-stop",
}


def _json(value: str, label: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be valid JSON") from exc


def _list(value: str, label: str) -> list[Any]:
    parsed = _json(value, label)
    if not isinstance(parsed, list):
        raise argparse.ArgumentTypeError(f"{label} must be a JSON list")
    return parsed


def _object(value: str, label: str) -> dict[str, Any]:
    parsed = _json(value, label)
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError(f"{label} must be a JSON object")
    return parsed


def _view(item) -> dict[str, Any]:
    return {
        "id": item.id,
        "kind": item.kind,
        "digest": item.digest,
        "created_at": item.created_at,
        "payload": item.payload,
    }


def _controller(args: argparse.Namespace) -> NtmResearchController:
    return NtmResearchController(
        NtmAdapter(
            Path(args.ntm_binary),
            timeout_seconds=args.ntm_timeout,
        )
    )


def _add_ntm(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ntm-binary", required=True)
    parser.add_argument("--ntm-timeout", type=int, default=90)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research",
        description="Persistent NTM-managed Codex research branches",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    discovery = sub.add_parser("discovery-context-build")
    discovery.add_argument("root")
    discovery.add_argument("--episode", required=True)
    discovery.add_argument("--commission", required=True)
    discovery.add_argument("--method", required=True)
    discovery.add_argument("--purpose", required=True)
    discovery.add_argument("--professional-object-ids-json", required=True)
    discovery.add_argument("--source-ids-json", default="[]")
    discovery.add_argument("--memory-entry-ids-json", default="[]")
    discovery.add_argument("--allow-codex-search", action="store_true")
    discovery.add_argument("--output-contract-json", default="{}")

    branch = sub.add_parser("branch-create")
    branch.add_argument("root")
    branch.add_argument("--episode", required=True)
    branch.add_argument("--commission", required=True)
    branch.add_argument("--method", required=True)
    branch.add_argument(
        "--kind",
        choices=("lead", "research", "challenge", "artifact", "rederivation"),
        required=True,
    )
    branch.add_argument("--title", required=True)
    branch.add_argument("--question", required=True)
    branch.add_argument("--context-ids-json", required=True)
    branch.add_argument("--expected-outputs-json", required=True)
    branch.add_argument("--authority-ceiling", required=True)
    branch.add_argument("--actor", required=True)
    branch.add_argument("--input-object-ids-json", default="[]")
    branch.add_argument("--parent")

    launch = sub.add_parser("branch-launch")
    launch.add_argument("root")
    launch.add_argument("branch")
    _add_ntm(launch)
    launch.add_argument("--codex-binary", required=True)
    launch.add_argument("--model", required=True)
    launch.add_argument("--role", required=True)
    launch.add_argument("--actor", required=True)
    launch.add_argument("--session")
    launch.add_argument("--pane", type=int, default=1)
    launch.add_argument("--resume-checkpoint")

    state = sub.add_parser("branch-state")
    state.add_argument("root")
    state.add_argument("branch")

    acknowledgement = sub.add_parser("branch-acknowledge")
    acknowledgement.add_argument("root")
    acknowledgement.add_argument("branch")
    acknowledgement.add_argument("binding")
    acknowledgement.add_argument("instruction")

    source_request = sub.add_parser("branch-source-request")
    source_request.add_argument("root")
    source_request.add_argument("branch")
    source_request.add_argument("binding")
    source_request.add_argument("relative_path")

    checkpoint = sub.add_parser("branch-checkpoint")
    checkpoint.add_argument("root")
    checkpoint.add_argument("branch")
    checkpoint.add_argument("binding")
    checkpoint.add_argument("relative_path")

    context_add = sub.add_parser("branch-context-add")
    context_add.add_argument("root")
    context_add.add_argument("branch")
    context_add.add_argument("binding")
    context_add.add_argument("context")
    _add_ntm(context_add)
    context_add.add_argument("--actor", required=True)
    context_add.add_argument("--source-request-ids-json", default="[]")

    steer = sub.add_parser("branch-steer")
    steer.add_argument("root")
    steer.add_argument("branch")
    steer.add_argument("binding")
    _add_ntm(steer)
    steer.add_argument(
        "--kind",
        choices=("steer", "challenge", "complete_request"),
        required=True,
    )
    steer.add_argument("--instruction", required=True)
    steer.add_argument("--actor", required=True)
    steer.add_argument("--context-ids-json", default="[]")
    steer.add_argument("--checkpoint")

    status = sub.add_parser("branch-status")
    status.add_argument("root")
    status.add_argument("branch")
    status.add_argument("binding")
    _add_ntm(status)

    completion = sub.add_parser("branch-completion")
    completion.add_argument("root")
    completion.add_argument("branch")
    completion.add_argument("binding")
    _add_ntm(completion)

    collect = sub.add_parser("branch-collect")
    collect.add_argument("root")
    collect.add_argument("branch")
    collect.add_argument("binding")

    stop = sub.add_parser("branch-stop")
    stop.add_argument("root")
    stop.add_argument("branch")
    stop.add_argument("binding")
    _add_ntm(stop)
    stop.add_argument("--actor", required=True)
    stop.add_argument("--reason", required=True)
    return parser


def run_command(args: argparse.Namespace) -> dict[str, Any]:
    workspace = ResearchWorkspace.open(Path(args.root))
    if args.command == "discovery-context-build":
        output_contract = _object(args.output_contract_json, "output contract")
        return _view(
            workspace.build_discovery_context(
                episode_id=args.episode,
                commission_id=args.commission,
                method_id=args.method,
                purpose=args.purpose,
                professional_object_ids=_list(
                    args.professional_object_ids_json,
                    "professional object ids",
                ),
                source_ids=_list(args.source_ids_json, "source ids"),
                memory_entry_ids=_list(
                    args.memory_entry_ids_json,
                    "memory entry ids",
                ),
                allow_codex_search=args.allow_codex_search,
                output_contract=output_contract or None,
            )
        )
    if args.command == "branch-create":
        return _view(
            workspace.create_research_branch(
                episode_id=args.episode,
                commission_id=args.commission,
                method_id=args.method,
                branch_kind=args.kind,
                title=args.title,
                question=args.question,
                context_ids=_list(args.context_ids_json, "context ids"),
                expected_outputs=_list(
                    args.expected_outputs_json,
                    "expected outputs",
                ),
                authority_ceiling=args.authority_ceiling,
                created_by=args.actor,
                input_object_ids=_list(
                    args.input_object_ids_json,
                    "input object ids",
                ),
                parent_branch_id=args.parent,
            )
        )
    if args.command == "branch-launch":
        return workspace.launch_research_branch(
            branch_id=args.branch,
            controller=_controller(args),
            codex_binary=Path(args.codex_binary),
            model=args.model,
            role_name=args.role,
            actor=args.actor,
            session=args.session,
            pane=args.pane,
            resume_checkpoint_id=args.resume_checkpoint,
        ).__dict__
    if args.command == "branch-state":
        return workspace.branch_state(args.branch)
    if args.command == "branch-acknowledge":
        return _view(
            workspace.collect_branch_acknowledgement(
                branch_id=args.branch,
                binding_id=args.binding,
                instruction_id=args.instruction,
            )
        )
    if args.command == "branch-source-request":
        return _view(
            workspace.collect_branch_source_request(
                branch_id=args.branch,
                binding_id=args.binding,
                relative_path=args.relative_path,
            )
        )
    if args.command == "branch-checkpoint":
        return _view(
            workspace.collect_branch_checkpoint(
                branch_id=args.branch,
                binding_id=args.binding,
                relative_path=args.relative_path,
            )
        )
    if args.command == "branch-context-add":
        return _view(
            workspace.attach_branch_context_delta(
                branch_id=args.branch,
                binding_id=args.binding,
                context_id=args.context,
                controller=_controller(args),
                actor=args.actor,
                satisfies_source_request_ids=_list(
                    args.source_request_ids_json,
                    "source request ids",
                ),
            )
        )
    if args.command == "branch-steer":
        return _view(
            workspace.send_branch_instruction(
                branch_id=args.branch,
                binding_id=args.binding,
                controller=_controller(args),
                instruction_kind=args.kind,
                actor=args.actor,
                instruction_text=args.instruction,
                context_ids=_list(args.context_ids_json, "context ids"),
                checkpoint_id=args.checkpoint,
            )
        )
    if args.command == "branch-status":
        return _view(
            workspace.observe_branch_status(
                branch_id=args.branch,
                binding_id=args.binding,
                controller=_controller(args),
            )
        )
    if args.command == "branch-completion":
        return _view(
            workspace.observe_branch_completion(
                branch_id=args.branch,
                binding_id=args.binding,
                controller=_controller(args),
            )
        )
    if args.command == "branch-collect":
        return workspace.collect_branch_result(
            branch_id=args.branch,
            binding_id=args.binding,
        ).__dict__
    if args.command == "branch-stop":
        return _view(
            workspace.stop_research_branch(
                branch_id=args.branch,
                binding_id=args.binding,
                controller=_controller(args),
                actor=args.actor,
                reason=args.reason,
            )
        )
    raise AssertionError(f"unhandled branch command: {args.command}")


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
