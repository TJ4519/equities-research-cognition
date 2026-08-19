from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from harness.ntm.adapter import NtmAdapter

from .errors import WorkspaceError
from .ntm_research import NtmResearchController
from .replay import ReplayEngine
from .service import ResearchWorkspace
from .util import canonical_json


def parse_json(value: str, label: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be valid JSON") from exc


def parse_object(value: str, label: str) -> dict[str, Any]:
    parsed = parse_json(value, label)
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError(f"{label} must be a JSON object")
    return parsed


def parse_list(value: str, label: str) -> list[Any]:
    parsed = parse_json(value, label)
    if not isinstance(parsed, list):
        raise argparse.ArgumentTypeError(f"{label} must be a JSON list")
    return parsed


def object_view(item) -> dict[str, Any]:
    return {
        "id": item.id,
        "kind": item.kind,
        "digest": item.digest,
        "created_at": item.created_at,
        "payload": item.payload,
    }


def workspace(args: argparse.Namespace) -> ResearchWorkspace:
    return ResearchWorkspace.open(Path(args.root))


def ntm_controller(args: argparse.Namespace) -> NtmResearchController:
    return NtmResearchController(
        NtmAdapter(
            Path(args.ntm_binary),
            timeout_seconds=args.ntm_timeout,
        )
    )


def add_ntm_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ntm-binary", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--ntm-timeout", type=int, default=90)


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

    mandate = sub.add_parser("mandate-create")
    mandate.add_argument("root")
    mandate.add_argument("--title", required=True)
    mandate.add_argument("--decision-use", required=True)
    mandate.add_argument("--actor", required=True)
    mandate.add_argument("--policy-json", default="{}")

    method = sub.add_parser("method-register")
    method.add_argument("root")
    method.add_argument("--name", required=True)
    method.add_argument("--version", required=True)
    method.add_argument("--purpose", required=True)
    method.add_argument("--output-kinds-json", required=True)
    method.add_argument("--required-actions-json", default="[]")
    method.add_argument("--runtime-json", default="{}")
    method.add_argument("--limits-json", default="{}")

    perspective = sub.add_parser("perspective-create")
    perspective.add_argument("root")
    perspective.add_argument("--mandate", required=True)
    perspective.add_argument("--label", required=True)
    perspective.add_argument("--item-ids-json", default="[]")
    perspective.add_argument("--parent")

    episode = sub.add_parser("episode-create")
    episode.add_argument("root")
    episode.add_argument("--mandate", required=True)
    episode.add_argument("--title", required=True)
    episode.add_argument("--request", required=True)
    episode.add_argument("--cutoff", required=True)
    episode.add_argument("--intended-use", required=True)
    episode.add_argument("--prior-perspective")

    commission = sub.add_parser("commission-confirm")
    commission.add_argument("root")
    commission.add_argument("--episode", required=True)
    commission.add_argument("--actor", required=True)
    commission.add_argument("--purpose", required=True)
    commission.add_argument("--subject-ids-json", default="[]")
    commission.add_argument("--method-ids-json", default="[]")
    commission.add_argument("--output-kinds-json", required=True)
    commission.add_argument("--unresolved-json", default="[]")
    commission.add_argument("--limits-json", default="{}")

    source = sub.add_parser("source-capture")
    source.add_argument("root")
    source.add_argument("--mandate", required=True)
    source.add_argument("--path", required=True)
    source.add_argument("--source-class", required=True)
    source.add_argument("--rights-json", required=True)
    source.add_argument("--metadata-json", default="{}")
    source.add_argument("--published-at")
    source.add_argument("--media-type")

    assertion = sub.add_parser("assertion-create")
    assertion.add_argument("root")
    assertion.add_argument("--source", required=True)
    assertion.add_argument("--locator", required=True)
    assertion.add_argument("--content", required=True)
    assertion.add_argument("--attributes-json", default="{}")
    assertion.add_argument("--proposed-by", required=True)

    professional = sub.add_parser("professional-object-create")
    professional.add_argument("root")
    professional.add_argument("--mandate", required=True)
    professional.add_argument("--kind", required=True)
    professional.add_argument("--label", required=True)
    professional.add_argument("--attributes-json", default="{}")
    professional.add_argument("--binding-json", default="{}")
    professional.add_argument(
        "--authority",
        choices=("model_proposed", "human_confirmed", "policy"),
        required=True,
    )
    professional.add_argument("--actor", required=True)

    evidence = sub.add_parser("evidence-decide")
    evidence.add_argument("root")
    evidence.add_argument("--episode", required=True)
    evidence.add_argument("--assertion", required=True)
    evidence.add_argument("--professional-object", required=True)
    evidence.add_argument("--intended-use", required=True)
    evidence.add_argument("--actions-json", required=True)
    evidence.add_argument(
        "--decision",
        choices=("admit", "quarantine", "reject"),
        required=True,
    )
    evidence.add_argument("--rationale", required=True)
    evidence.add_argument("--actor", required=True)
    evidence.add_argument("--effective-until")

    context = sub.add_parser("context-build")
    context.add_argument("root")
    context.add_argument("--episode", required=True)
    context.add_argument("--commission", required=True)
    context.add_argument("--method", required=True)
    context.add_argument("--purpose", required=True)
    context.add_argument("--assertion-ids-json", required=True)
    context.add_argument("--professional-object-ids-json", required=True)
    context.add_argument("--required-action", required=True)
    context.add_argument("--memory-entry-ids-json", default="[]")
    context.add_argument("--allowed-tools-json", default="[]")
    context.add_argument("--output-contract-json", default="{}")

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
    add_ntm_arguments(launch)
    launch.add_argument("--model", required=True)
    launch.add_argument("--role", required=True)
    launch.add_argument("--actor", required=True)
    launch.add_argument("--session")
    launch.add_argument("--pane", type=int, default=1)
    launch.add_argument("--resume-checkpoint")

    branch_state = sub.add_parser("branch-state")
    branch_state.add_argument("root")
    branch_state.add_argument("branch")

    acknowledge = sub.add_parser("branch-acknowledge")
    acknowledge.add_argument("root")
    acknowledge.add_argument("branch")
    acknowledge.add_argument("binding")
    acknowledge.add_argument("instruction")

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
    add_ntm_arguments(context_add)
    context_add.add_argument("--actor", required=True)
    context_add.add_argument("--source-request-ids-json", default="[]")

    steer = sub.add_parser("branch-steer")
    steer.add_argument("root")
    steer.add_argument("branch")
    steer.add_argument("binding")
    add_ntm_arguments(steer)
    steer.add_argument(
        "--kind",
        choices=("steer", "challenge", "complete_request"),
        required=True,
    )
    steer.add_argument("--instruction", required=True)
    steer.add_argument("--actor", required=True)
    steer.add_argument("--context-ids-json", default="[]")
    steer.add_argument("--checkpoint")

    observe_status = sub.add_parser("branch-status")
    observe_status.add_argument("root")
    observe_status.add_argument("branch")
    observe_status.add_argument("binding")
    add_ntm_arguments(observe_status)

    completion = sub.add_parser("branch-completion")
    completion.add_argument("root")
    completion.add_argument("branch")
    completion.add_argument("binding")
    add_ntm_arguments(completion)

    collect = sub.add_parser("branch-collect")
    collect.add_argument("root")
    collect.add_argument("branch")
    collect.add_argument("binding")

    stop = sub.add_parser("branch-stop")
    stop.add_argument("root")
    stop.add_argument("branch")
    stop.add_argument("binding")
    add_ntm_arguments(stop)
    stop.add_argument("--actor", required=True)
    stop.add_argument("--reason", required=True)

    decision = sub.add_parser("decision-record")
    decision.add_argument("root")
    decision.add_argument("--episode", required=True)
    decision.add_argument("--target", required=True)
    decision.add_argument("--action", required=True)
    decision.add_argument("--purpose", required=True)
    decision.add_argument("--actor", required=True)
    decision.add_argument("--grant-json", default="{}")

    correction = sub.add_parser("correction-record")
    correction.add_argument("root")
    correction.add_argument("--episode", required=True)
    correction.add_argument("--target", required=True)
    correction.add_argument("--actor", required=True)
    correction.add_argument("--reason", required=True)
    correction.add_argument("--replacement-json", required=True)
    correction.add_argument("--scope-json", required=True)

    memory = sub.add_parser("memory-create")
    memory.add_argument("root")
    memory.add_argument("--mandate", required=True)
    memory.add_argument("--actor", required=True)
    memory.add_argument("--content", required=True)
    memory.add_argument("--scope-json", required=True)
    memory.add_argument("--authority", required=True)
    memory.add_argument("--source-correction")
    memory.add_argument("--effective-until")

    evaluation = sub.add_parser("evaluation-create")
    evaluation.add_argument("root")
    evaluation.add_argument("--mandate", required=True)
    evaluation.add_argument("--episode", required=True)
    evaluation.add_argument("--name", required=True)
    evaluation.add_argument("--baseline-run", required=True)
    evaluation.add_argument("--baseline-result", required=True)
    evaluation.add_argument("--expected-json", default="{}")

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
        item = ResearchWorkspace.initialise(Path(args.root), title=args.title)
        return item.status()
    item = workspace(args)
    if args.command == "status":
        return item.status()
    if args.command == "show":
        return object_view(item.store.get_object(args.object_id))
    if args.command == "mandate-create":
        return object_view(
            item.create_mandate(
                title=args.title,
                decision_use=args.decision_use,
                actor=args.actor,
                policy=parse_object(args.policy_json, "policy"),
            )
        )
    if args.command == "method-register":
        return object_view(
            item.register_method(
                name=args.name,
                version=args.version,
                purpose=args.purpose,
                output_kinds=parse_list(args.output_kinds_json, "output kinds"),
                required_actions=parse_list(args.required_actions_json, "required actions"),
                runtime=parse_object(args.runtime_json, "runtime"),
                limits=parse_object(args.limits_json, "limits"),
            )
        )
    if args.command == "perspective-create":
        return object_view(
            item.create_perspective(
                mandate_id=args.mandate,
                label=args.label,
                item_ids=parse_list(args.item_ids_json, "perspective items"),
                parent_id=args.parent,
            )
        )
    if args.command == "episode-create":
        return object_view(
            item.create_episode(
                mandate_id=args.mandate,
                title=args.title,
                original_request=args.request,
                evidence_cutoff=args.cutoff,
                intended_use=args.intended_use,
                prior_perspective_id=args.prior_perspective,
            )
        )
    if args.command == "commission-confirm":
        return object_view(
            item.confirm_commission(
                episode_id=args.episode,
                actor=args.actor,
                purpose=args.purpose,
                subject_ids=parse_list(args.subject_ids_json, "commission subjects"),
                method_ids=parse_list(args.method_ids_json, "commission methods"),
                output_kinds=parse_list(args.output_kinds_json, "commission outputs"),
                unresolved_questions=parse_list(args.unresolved_json, "unresolved questions"),
                limits=parse_object(args.limits_json, "commission limits"),
            )
        )
    if args.command == "source-capture":
        return object_view(
            item.capture_source(
                mandate_id=args.mandate,
                path=Path(args.path),
                source_class=args.source_class,
                rights=parse_object(args.rights_json, "source rights"),
                metadata=parse_object(args.metadata_json, "source metadata"),
                published_at=args.published_at,
                media_type=args.media_type,
            )
        )
    if args.command == "assertion-create":
        return object_view(
            item.create_assertion(
                source_id=args.source,
                locator=args.locator,
                content=args.content,
                attributes=parse_object(args.attributes_json, "assertion attributes"),
                proposed_by=args.proposed_by,
            )
        )
    if args.command == "professional-object-create":
        return object_view(
            item.create_professional_object(
                mandate_id=args.mandate,
                kind=args.kind,
                label=args.label,
                attributes=parse_object(args.attributes_json, "professional-object attributes"),
                binding=parse_object(args.binding_json, "professional-object binding"),
                authority=args.authority,
                actor=args.actor,
            )
        )
    if args.command == "evidence-decide":
        return object_view(
            item.decide_evidence_use(
                episode_id=args.episode,
                assertion_id=args.assertion,
                professional_object_id=args.professional_object,
                intended_use=args.intended_use,
                permitted_actions=parse_list(args.actions_json, "evidence actions"),
                decision=args.decision,
                rationale=args.rationale,
                actor=args.actor,
                effective_until=args.effective_until,
            )
        )
    if args.command == "context-build":
        output_contract = parse_object(args.output_contract_json, "output contract")
        return object_view(
            item.build_context(
                episode_id=args.episode,
                commission_id=args.commission,
                method_id=args.method,
                purpose=args.purpose,
                assertion_ids=parse_list(args.assertion_ids_json, "context assertions"),
                professional_object_ids=parse_list(
                    args.professional_object_ids_json,
                    "context professional objects",
                ),
                required_action=args.required_action,
                memory_entry_ids=parse_list(args.memory_entry_ids_json, "context memory"),
                allowed_tools=parse_list(args.allowed_tools_json, "context tools"),
                output_contract=output_contract or None,
            )
        )
    if args.command == "branch-create":
        return object_view(
            item.create_research_branch(
                episode_id=args.episode,
                commission_id=args.commission,
                method_id=args.method,
                branch_kind=args.kind,
                title=args.title,
                question=args.question,
                context_ids=parse_list(args.context_ids_json, "branch contexts"),
                expected_outputs=parse_list(
                    args.expected_outputs_json,
                    "branch expected outputs",
                ),
                authority_ceiling=args.authority_ceiling,
                created_by=args.actor,
                input_object_ids=parse_list(
                    args.input_object_ids_json,
                    "branch input objects",
                ),
                parent_branch_id=args.parent,
            )
        )
    if args.command == "branch-launch":
        outcome = item.launch_research_branch(
            branch_id=args.branch,
            controller=ntm_controller(args),
            config=Path(args.config),
            model=args.model,
            role_name=args.role,
            actor=args.actor,
            session=args.session,
            pane=args.pane,
            resume_checkpoint_id=args.resume_checkpoint,
        )
        return outcome.__dict__
    if args.command == "branch-state":
        return item.branch_state(args.branch)
    if args.command == "branch-acknowledge":
        return object_view(
            item.collect_branch_acknowledgement(
                branch_id=args.branch,
                binding_id=args.binding,
                instruction_id=args.instruction,
            )
        )
    if args.command == "branch-source-request":
        return object_view(
            item.collect_branch_source_request(
                branch_id=args.branch,
                binding_id=args.binding,
                relative_path=args.relative_path,
            )
        )
    if args.command == "branch-checkpoint":
        return object_view(
            item.collect_branch_checkpoint(
                branch_id=args.branch,
                binding_id=args.binding,
                relative_path=args.relative_path,
            )
        )
    if args.command == "branch-context-add":
        return object_view(
            item.attach_branch_context_delta(
                branch_id=args.branch,
                binding_id=args.binding,
                context_id=args.context,
                controller=ntm_controller(args),
                config=Path(args.config),
                actor=args.actor,
                satisfies_source_request_ids=parse_list(
                    args.source_request_ids_json,
                    "satisfied source requests",
                ),
            )
        )
    if args.command == "branch-steer":
        return object_view(
            item.send_branch_instruction(
                branch_id=args.branch,
                binding_id=args.binding,
                controller=ntm_controller(args),
                config=Path(args.config),
                instruction_kind=args.kind,
                actor=args.actor,
                instruction_text=args.instruction,
                context_ids=parse_list(args.context_ids_json, "steering contexts"),
                checkpoint_id=args.checkpoint,
            )
        )
    if args.command == "branch-status":
        return object_view(
            item.observe_branch_status(
                branch_id=args.branch,
                binding_id=args.binding,
                controller=ntm_controller(args),
                config=Path(args.config),
            )
        )
    if args.command == "branch-completion":
        return object_view(
            item.observe_branch_completion(
                branch_id=args.branch,
                binding_id=args.binding,
                controller=ntm_controller(args),
                config=Path(args.config),
            )
        )
    if args.command == "branch-collect":
        return item.collect_branch_result(
            branch_id=args.branch,
            binding_id=args.binding,
        ).__dict__
    if args.command == "branch-stop":
        return object_view(
            item.stop_research_branch(
                branch_id=args.branch,
                binding_id=args.binding,
                controller=ntm_controller(args),
                config=Path(args.config),
                actor=args.actor,
                reason=args.reason,
            )
        )
    if args.command == "decision-record":
        return object_view(
            item.record_decision(
                episode_id=args.episode,
                target_id=args.target,
                action=args.action,
                purpose=args.purpose,
                actor=args.actor,
                grant=parse_object(args.grant_json, "decision grant"),
            )
        )
    if args.command == "correction-record":
        return object_view(
            item.record_correction(
                episode_id=args.episode,
                target_id=args.target,
                actor=args.actor,
                reason=args.reason,
                replacement=parse_object(args.replacement_json, "correction replacement"),
                scope=parse_object(args.scope_json, "correction scope"),
            )
        )
    if args.command == "memory-create":
        return object_view(
            item.create_memory_entry(
                mandate_id=args.mandate,
                actor=args.actor,
                content=args.content,
                scope=parse_object(args.scope_json, "memory scope"),
                authority=args.authority,
                source_correction_id=args.source_correction,
                effective_until=args.effective_until,
            )
        )
    if args.command == "evaluation-create":
        return object_view(
            item.create_evaluation_case(
                mandate_id=args.mandate,
                episode_id=args.episode,
                name=args.name,
                baseline_run_id=args.baseline_run,
                baseline_result_id=args.baseline_result,
                expected=parse_object(args.expected_json, "evaluation expected result"),
            )
        )
    engine = ReplayEngine(item.store)
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
