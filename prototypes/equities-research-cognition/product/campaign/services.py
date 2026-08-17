from __future__ import annotations

from hashlib import sha256
import json
from os import environ
from pathlib import Path
import re
import shlex
from typing import Mapping
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from harness.langfuse.transport import (
    LangfuseConnection,
    LangfuseRejected,
    build_codex_trace_arguments,
    campaign_launch_environment,
    connection_from_environment,
    readback_observations,
    readback_project_identity,
    sanitized_control_environment,
)
from harness.ntm.adapter import ExecutionResult, NtmAdapter

from .models import (
    Artifact,
    ArtifactVersion,
    Proposal,
    ProposalDisposition,
    ResearchCampaign,
    ResearchStateDisposition,
    ResearchStateTransition,
    RuntimeEvent,
    RunSpecVersion,
    TraceLink,
    WorkOrder,
    canonical_bytes,
    canonical_digest,
)
from .research_state import (
    ResearchStateRejected,
    project_transition,
    validate_transition,
)


PROTOTYPE_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_ROOT = PROTOTYPE_ROOT / "agents"
WORKBENCH_ROOT = PROTOTYPE_ROOT / "workbenches"
SKILL_LOCK = PROTOTYPE_ROOT / "skills" / "lock.json"
ACTIVE_WORKBENCHES = (
    (
        "equities/comparable-state-reconstruction/v0",
        "v0",
        "comparable-state-v0",
        "Comparable definitions, scope, period and units or explicit refusal.",
    ),
    (
        "equities/aggregate-driver-attribution/v0",
        "v0",
        "aggregate-driver-v0",
        "Price, volume, mix, FX, timing, interaction and residual identity.",
    ),
    (
        "equities/expectation-surfaces/v1",
        "v1",
        "expectation-surfaces-v1",
        "Cutoff-time guidance, consensus, narrative, positioning and model routes.",
    ),
    (
        "equities/decision-consequence-map/v1",
        "v1",
        "decision-consequence-v1",
        "Candidate decision mapping; currently refuses without product-issued "
        "decision authority.",
    ),
)
PROTOCOL_FILES = {
    "bound_work": "bound_work/protocol.md",
    "planner": "planner/protocol.md",
    "research_worker": "research_worker/protocol.md",
    "adversarial_review": "adversarial_review/protocol.md",
    "synthesis": "synthesis/protocol.md",
    "judgment": "judgment/protocol.md",
}
PROTOCOL_OUTPUTS = {
    "bound_work": ("outcome.json", "run-acknowledgement.json"),
    "planner": ("plan.md", "proposals.jsonl"),
    "research_worker": (
        "branch.md",
        "epistemic-delta.json",
        "research-state.json",
        "workbench-result.json",
    ),
    "adversarial_review": ("review.md",),
    "synthesis": ("synthesis.md",),
    "judgment": ("judgment.json",),
}
PLANNER_INTERPRETATION_AUTHORITY_LIMIT = "planner_interpretation_only"
STALE_PLANNER_INPUT_MESSAGE = (
    "This proposal was planned before the current evidence was accepted. "
    "Re-plan from current evidence before approving follow-on research."
)


class CampaignRejected(Exception):
    pass


def _text(value: object, label: str, limit: int | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CampaignRejected(f"{label} is required")
    value = value.strip()
    if limit is not None and len(value) > limit:
        raise CampaignRejected(f"{label} is too long")
    return value


def require_director(campaign: ResearchCampaign, user: object) -> None:
    if campaign.director_id != getattr(user, "pk", None):
        raise CampaignRejected("only the campaign director may act")


def workbench_catalog() -> list[dict[str, object]]:
    rows = []
    for workbench_id, version, directory, purpose in ACTIVE_WORKBENCHES:
        protocol_path = WORKBENCH_ROOT / directory / "protocol.md"
        if protocol_path.is_symlink() or not protocol_path.is_file():
            raise CampaignRejected("active workbench source is unavailable")
        rows.append(
            {
                "workbench_id": workbench_id,
                "version": version,
                "purpose": purpose,
                "protocol_sha256": sha256(protocol_path.read_bytes()).hexdigest(),
                "protocol_path": protocol_path.relative_to(PROTOTYPE_ROOT).as_posix(),
            }
        )
    return rows


def skill_catalog() -> list[dict[str, object]]:
    try:
        lock = json.loads(SKILL_LOCK.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CampaignRejected("cognition skill lock is unavailable") from exc
    packages = lock.get("packages") if isinstance(lock, dict) else None
    if (
        not isinstance(lock, dict)
        or lock.get("schema") != "external-cognition-skill-lock/v1"
        or not isinstance(packages, list)
        or not packages
    ):
        raise CampaignRejected("cognition skill lock is malformed")
    required = {
        "name",
        "relative_source",
        "skill_sha256",
        "file_count",
        "files",
    }
    if any(not isinstance(item, dict) or set(item) != required for item in packages):
        raise CampaignRejected("cognition skill lock is malformed")
    for package in packages:
        files = package["files"]
        if (
            not isinstance(package["file_count"], int)
            or package["file_count"] < 1
            or not isinstance(files, list)
            or len(files) != package["file_count"]
        ):
            raise CampaignRejected("cognition skill lock is malformed")
        seen: set[str] = set()
        for item in files:
            if (
                not isinstance(item, dict)
                or set(item) != {"path", "sha256"}
                or not isinstance(item["path"], str)
                or not isinstance(item["sha256"], str)
                or len(item["sha256"]) != 64
                or any(
                    character not in "0123456789abcdef"
                    for character in item["sha256"]
                )
            ):
                raise CampaignRejected("cognition skill lock is malformed")
            relative = Path(item["path"])
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or item["path"] in seen
            ):
                raise CampaignRejected("cognition skill lock is malformed")
            seen.add(item["path"])
        skill_rows = [item for item in files if item["path"] == "SKILL.md"]
        if (
            len(skill_rows) != 1
            or skill_rows[0]["sha256"] != package["skill_sha256"]
        ):
            raise CampaignRejected("cognition skill lock is malformed")
    return packages


def _required_reads(proposal: Proposal) -> list[dict[str, object]]:
    filename = PROTOCOL_FILES.get(proposal.protocol)
    if not filename:
        raise CampaignRejected("proposal names an unavailable protocol")
    role_path = PROTOCOL_ROOT / filename
    if role_path.is_symlink() or not role_path.is_file():
        raise CampaignRejected("frozen role protocol is unavailable")
    reads: list[dict[str, object]] = [
        {
            "kind": "role_protocol",
            "name": proposal.protocol,
            "path": str(role_path),
            "sha256": sha256(role_path.read_bytes()).hexdigest(),
        }
    ]
    known_workbenches = {
        (item["workbench_id"], item["version"]): item
        for item in workbench_catalog()
    }
    selected_workbenches = proposal.contract.get("workbenches", [])
    for selected in selected_workbenches:
        item = known_workbenches[(selected["workbench_id"], selected["version"])]
        path = PROTOTYPE_ROOT / item["protocol_path"]
        reads.append(
            {
                "kind": "workbench_protocol",
                "name": item["workbench_id"],
                "path": str(path),
                "sha256": item["protocol_sha256"],
            }
        )
    skill_root = Path(settings.CAMPAIGN_CODEX_SKILL_ROOT).expanduser()
    for selected in proposal.contract.get("reasoning_operators", []):
        reads.append(
            {
                "kind": "reasoning_skill",
                "name": selected["name"],
                "path": str(skill_root / selected["name"] / "SKILL.md"),
                "sha256": selected["skill_sha256"],
                "file_count": selected["file_count"],
                "package_files": selected["files"],
            }
        )
    return reads


def _output_contract(
    campaign: ResearchCampaign, order_id: uuid.UUID, protocol: str
) -> dict[str, object]:
    required = PROTOCOL_OUTPUTS.get(protocol)
    if required is None:
        raise CampaignRejected("proposal names an unavailable output contract")
    relative_root = Path("work") / str(order_id) / "out"
    return {
        "schema_version": "work-order-output/v1",
        "output_root": str(Path(campaign.artifact_root) / relative_root),
        "campaign_relative_root": relative_root.as_posix(),
        "write_policy": "write_only_beneath_output_root",
        "required_paths": sorted(required),
        "primary_path": required[0],
        "attestation_path": "artifact-attestation.json",
        "population_policy": "regular_files_at_output_root_only",
    }


def canonical_bound_work_packet(
    *,
    campaign: ResearchCampaign,
    proposal: Proposal,
    run_spec: RunSpecVersion,
    order_id: uuid.UUID,
    logical_role_id: uuid.UUID,
) -> dict[str, object]:
    """Derive the complete bound dispatch from its immutable authorities."""
    job_inputs = [
        {"id": item["id"], "sha256": item["sha256"]}
        for item in sorted(run_spec.input_manifest, key=lambda item: item["id"])
    ]
    job_input_files = [
        {
            **item,
            "materialized_path": str(
                Path(campaign.artifact_root)
                / "dispatches"
                / f"{order_id}.inputs"
                / (
                    f"{item['id']}-{item['sha256']}"
                    f"{Path(item['filename']).suffix or '.bin'}"
                )
            ),
        }
        for item in sorted(run_spec.input_manifest, key=lambda item: item["id"])
    ]
    return {
        "schema_version": "research-work-order/v1",
        "campaign_id": str(campaign.pk),
        "research_case_id": str(campaign.pk),
        "work_order_id": str(order_id),
        "logical_role_id": str(logical_role_id),
        "proposal_id": str(proposal.pk),
        "proposal_digest": proposal.digest,
        "protocol": "bound_work",
        "decision_use": campaign.equities_decision_use,
        "evidence_cutoff": campaign.evidence_cutoff.isoformat(),
        "task": proposal.task,
        "contract": proposal.contract,
        "output_contract": _output_contract(campaign, order_id, "bound_work"),
        "required_read_policy": (
            "Read every exact required_reads path before work; verify its SHA-256 "
            "and fail rather than substitute changed cognition."
        ),
        "required_reads": _required_reads(proposal),
        "inputs": [],
        "research_state_input": {"basis": WorkOrder.StateBasis.COMMISSION},
        "supporting_research_states": [],
        "run_spec": {"id": str(run_spec.pk), "sha256": run_spec.digest},
        "job_inputs": job_inputs,
        "job_input_files": job_input_files,
        "objective": run_spec.objective,
        "run_instruction": run_spec.instruction,
        "outcome_authority": "provisional_only",
    }


def _require_known_workbenches(contract: dict[str, object]) -> None:
    selected = contract.get("workbenches", [])
    if not isinstance(selected, list):
        raise CampaignRejected("proposal workbench selection is malformed")
    known = {
        (item["workbench_id"], item["version"]): item
        for item in workbench_catalog()
    }
    for item in selected:
        if (
            not isinstance(item, dict)
            or set(item) != {
                "workbench_id", "version", "protocol_sha256"
            }
            or (item["workbench_id"], item["version"]) not in known
            or any(
                item[key] != known[(item["workbench_id"], item["version"])][key]
                for key in item
            )
        ):
            raise CampaignRejected("proposal selects an unknown workbench version")


def _require_known_reasoning(contract: dict[str, object]) -> None:
    selected = contract.get("reasoning_operators", [])
    if not isinstance(selected, list):
        raise CampaignRejected("proposal reasoning selection is malformed")
    known = {item["name"]: item for item in skill_catalog()}
    authority = {
        "failure_tested",
        "expected_epistemic_delta",
        "kill_condition",
    }
    for item in selected:
        if (
            not isinstance(item, dict)
            or set(item) != set(next(iter(known.values()))) | authority
            or item.get("name") not in known
            or any(item[key] != known[item["name"]][key] for key in known[item["name"]])
            or any(not isinstance(item[key], str) or not item[key].strip() for key in authority)
        ):
            raise CampaignRejected("proposal selects an unknown reasoning operator")


def create_campaign(
    *,
    director: object,
    title: str,
    issuer_or_security: str,
    equities_decision_use: str,
    evidence_cutoff: object,
    question: str,
) -> ResearchCampaign:
    campaign_id = uuid.uuid4()
    root = Path(settings.CAMPAIGN_ROOT).expanduser().resolve() / str(campaign_id)
    if root.exists():
        raise CampaignRejected("campaign artifact root already exists")
    try:
        root.mkdir(parents=True)
        return ResearchCampaign.objects.create(
            id=campaign_id,
            director=director,
            title=_text(title, "campaign title", 180),
            issuer_or_security=_text(
                issuer_or_security, "issuer or security", 240
            ),
            equities_decision_use=_text(
                equities_decision_use, "equities decision use"
            ),
            evidence_cutoff=evidence_cutoff,
            commissioned_question=_text(question, "commissioned question"),
            ntm_session=f"flywheel-{campaign_id.hex[:20]}",
            artifact_root=str(root),
        )
    except (IntegrityError, OSError, ValidationError, ValueError) as exc:
        if root.exists():
            root.rmdir()
        raise CampaignRejected("campaign creation failed closed") from exc


def _uploaded_artifact(upload: object, *, label: str) -> tuple[str, str, bytes]:
    name = getattr(upload, "name", "")
    media_type = getattr(upload, "content_type", "") or "application/octet-stream"
    if not isinstance(name, str) or not name or Path(name).name != name:
        raise CampaignRejected(f"{label} filename is unsafe")
    declared_size = getattr(upload, "size", None)
    if (
        isinstance(declared_size, int)
        and declared_size > settings.CAMPAIGN_ARTIFACT_MAX_BYTES
    ):
        raise CampaignRejected(f"{label} exceeds the custody limit")
    try:
        content = upload.read(settings.CAMPAIGN_ARTIFACT_MAX_BYTES + 1)
    except (AttributeError, OSError, TypeError) as exc:
        raise CampaignRejected(f"{label} could not be read") from exc
    if not isinstance(content, bytes) or not content:
        raise CampaignRejected(f"{label} is empty")
    if len(content) > settings.CAMPAIGN_ARTIFACT_MAX_BYTES:
        raise CampaignRejected(f"{label} exceeds the custody limit")
    return name, _text(media_type, f"{label} media type", 120), content


def _input_manifest(items: list[ArtifactVersion]) -> list[dict[str, str]]:
    return [
        {
            "id": str(item.pk),
            "role": item.role,
            "filename": item.filename,
            "media_type": item.media_type,
            "sha256": item.digest,
        }
        for item in sorted(items, key=lambda item: str(item.pk))
    ]


def create_owned_job(
    *,
    director: object,
    title: str,
    issuer_or_security: str,
    equities_decision_use: str,
    evidence_cutoff: object,
    question: str,
    run_instruction: str,
    starting_artifact: object | None,
    sources: list[object],
) -> ResearchCampaign:
    """Create one owned job, immutable inputs/specification, and bound work."""
    if starting_artifact is None:
        raise CampaignRejected("starting artifact is required")
    if not sources:
        raise CampaignRejected("at least one source is required")
    if len(sources) > settings.CAMPAIGN_JOB_MAX_SOURCES:
        raise CampaignRejected("job has too many sources")
    prepared: list[tuple[str, str, str, bytes]] = []
    aggregate_bytes = 0
    for role, upload, label in [
        (
            ArtifactVersion.Role.STARTING_ARTIFACT,
            starting_artifact,
            "starting artifact",
        ),
        *[
            (ArtifactVersion.Role.SOURCE, source, "source")
            for source in sources
        ],
    ]:
        name, media_type, content = _uploaded_artifact(upload, label=label)
        aggregate_bytes += len(content)
        if aggregate_bytes > settings.CAMPAIGN_JOB_MAX_INPUT_BYTES:
            raise CampaignRejected("job inputs exceed the aggregate custody limit")
        prepared.append((role, name, media_type, content))
    campaign_id = uuid.uuid4()
    root = Path(settings.CAMPAIGN_ROOT).expanduser().resolve() / str(campaign_id)
    if root.exists():
        raise CampaignRejected("campaign artifact root already exists")
    try:
        root.mkdir(parents=True)
        with transaction.atomic():
            campaign = ResearchCampaign.objects.create(
                id=campaign_id,
                director=director,
                title=_text(title, "job title", 180),
                issuer_or_security=_text(
                    issuer_or_security, "issuer or security", 240
                ),
                equities_decision_use=_text(
                    equities_decision_use, "professional decision use"
                ),
                evidence_cutoff=evidence_cutoff,
                commissioned_question=_text(question, "objective"),
                ntm_session=f"flywheel-{campaign_id.hex[:20]}",
                artifact_root=str(root),
            )
            inputs = [
                ArtifactVersion.objects.create(
                    campaign=campaign,
                    role=role,
                    filename=name,
                    media_type=media_type,
                    content=content,
                    digest=sha256(content).hexdigest(),
                )
                for role, name, media_type, content in prepared
            ]
            spec_id = uuid.uuid4()
            objective = campaign.commissioned_question
            instruction = _text(run_instruction, "run instruction")
            manifest = _input_manifest(inputs)
            outcome_contract = {
                "schema_version": "bound-run-outcome/v1",
                "allowed_kinds": ["candidate", "refusal"],
                "authority": "provisional_only",
            }
            spec_payload = {
                "id": str(spec_id),
                "campaign": str(campaign.pk),
                "objective": objective,
                "instruction": instruction,
                "input_manifest": manifest,
                "outcome_contract": outcome_contract,
            }
            spec = RunSpecVersion.objects.create(
                id=spec_id,
                campaign=campaign,
                objective=objective,
                instruction=instruction,
                input_manifest=manifest,
                outcome_contract=outcome_contract,
                digest=canonical_digest(spec_payload),
            )
            proposal = record_proposal(
                campaign=campaign,
                author=Proposal.Author.DIRECTOR,
                author_user=director,
                protocol="bound_work",
                title="Produce a provisional result from the exact supplied inputs",
                task=instruction,
                contract={
                    "workbenches": [],
                    "reasoning_operators": [],
                    "run_spec": {"id": str(spec.pk), "sha256": spec.digest},
                    "authority": "provisional_only",
                },
            )
            _approved_order(proposal, user=director, run_spec=spec)
            return campaign
    except (IntegrityError, OSError, ValidationError, ValueError, CampaignRejected) as exc:
        if root.exists() and not any(root.iterdir()):
            root.rmdir()
        if isinstance(exc, CampaignRejected):
            raise
        raise CampaignRejected("owned job creation failed closed") from exc


def _configured_langfuse_source(
    source: Mapping[str, str],
) -> dict[str, str]:
    return {
        "FLYWHEEL_LANGFUSE_TARGET_BASE_URL": (
            settings.LANGFUSE_TARGET_BASE_URL
        ),
        "FLYWHEEL_LANGFUSE_TARGET_PROJECT_ID": (
            settings.LANGFUSE_TARGET_PROJECT_ID
        ),
        "FLYWHEEL_LANGFUSE_AUTHORIZATION": source.get(
            "FLYWHEEL_LANGFUSE_AUTHORIZATION", ""
        ),
    }


def configured_langfuse_connection(
    source: Mapping[str, str],
) -> LangfuseConnection:
    return connection_from_environment(_configured_langfuse_source(source))


def _verify_provider_project(connection: LangfuseConnection) -> None:
    try:
        readback_project_identity(connection=connection)
    except LangfuseRejected as exc:
        raise CampaignRejected(str(exc)) from exc


def _preflight_langfuse_runtime(
    live_source: Mapping[str, str],
) -> dict[str, str]:
    snapshot = dict(live_source)
    try:
        connection = configured_langfuse_connection(snapshot)
        _verify_provider_project(connection)
    except LangfuseRejected as exc:
        raise CampaignRejected(str(exc)) from exc
    return snapshot


def record_proposal(
    *,
    campaign: ResearchCampaign,
    author: str,
    protocol: str,
    title: str,
    task: str,
    contract: dict[str, object],
    parent: Proposal | None = None,
    author_user: object | None = None,
    _system_interpretation: bool = False,
) -> Proposal:
    proposal_id = uuid.uuid4()
    payload = {
        "id": str(proposal_id),
        "campaign": str(campaign.pk),
        "parent": str(parent.pk) if parent else None,
        "author": author,
        "author_user": getattr(author_user, "pk", None),
        "protocol": _text(protocol, "protocol", 80),
        "title": _text(title, "proposal title", 240),
        "task": _text(task, "proposal task"),
        "contract": contract,
    }
    if not isinstance(contract, dict):
        raise CampaignRejected("proposal contract must be a JSON object")
    if contract.get("authority_limit") == PLANNER_INTERPRETATION_AUTHORITY_LIMIT and (
        not _system_interpretation
        or author != Proposal.Author.PLANNER
        or payload["protocol"] != "planner"
    ):
        raise CampaignRejected("planner interpretation authority is system-issued")
    _require_known_workbenches(contract)
    _require_known_reasoning(contract)
    try:
        return Proposal.objects.create(
            id=proposal_id,
            campaign=campaign,
            parent=parent,
            author=author,
            author_user=author_user,
            protocol=payload["protocol"],
            title=payload["title"],
            task=payload["task"],
            contract=contract,
            digest=canonical_digest(payload),
        )
    except (IntegrityError, ValidationError) as exc:
        raise CampaignRejected("proposal violates exact campaign custody") from exc


def _disposition(
    proposal: Proposal, *, user: object, kind: str, feedback: str = ""
) -> ProposalDisposition:
    require_director(proposal.campaign, user)
    if hasattr(proposal, "disposition"):
        raise CampaignRejected("proposal already has a terminal disposition")
    try:
        return ProposalDisposition.objects.create(
            proposal=proposal,
            kind=kind,
            actor=user,
            feedback=feedback,
        )
    except (IntegrityError, ValidationError) as exc:
        raise CampaignRejected("proposal disposition failed closed") from exc


def _is_planner_interpretation(proposal: Proposal) -> bool:
    return bool(
        proposal.author == Proposal.Author.PLANNER
        and proposal.protocol == "planner"
        and proposal.contract.get("authority_limit")
        == PLANNER_INTERPRETATION_AUTHORITY_LIMIT
    )


def _planner_interpretation_ancestor(proposal: Proposal) -> Proposal | None:
    current: Proposal | None = proposal
    seen: set[uuid.UUID] = set()
    while current is not None:
        if current.pk in seen:
            raise CampaignRejected("proposal lineage is cyclic")
        seen.add(current.pk)
        if _is_planner_interpretation(current):
            return current
        current = current.parent
    return None


def _require_confirmed_planner_interpretation(proposal: Proposal) -> None:
    if not _planner_route_available(proposal):
        raise CampaignRejected("planner interpretation is not confirmed")


def _planner_route_available(proposal: Proposal) -> bool:
    if proposal.protocol == "planner":
        return True
    interpretation = _planner_interpretation_ancestor(proposal)
    return interpretation is None or (
        getattr(interpretation, "disposition", None) is not None
        and interpretation.disposition.kind == ProposalDisposition.Kind.APPROVED
    )


def _planner_interpretation_source(
    proposal: Proposal,
) -> tuple[WorkOrder, list[int]]:
    if not _is_planner_interpretation(proposal):
        raise CampaignRejected("proposal is not a planner interpretation")
    planning_work_order_id = proposal.contract.get("planning_work_order_id")
    if not isinstance(planning_work_order_id, str):
        raise CampaignRejected("planner interpretation lacks its planning work")
    try:
        planning_order = (
            WorkOrder.objects.select_related("proposal")
            .filter(
                pk=planning_work_order_id,
                campaign=proposal.campaign,
                protocol="planner",
            )
            .first()
        )
    except (ValidationError, ValueError) as exc:
        raise CampaignRejected(
            "planner interpretation lacks its planning work"
        ) from exc
    if planning_order is None:
        raise CampaignRejected("planner interpretation lacks its planning work")
    artifact_ids: list[int] = []
    for name in ("plan_artifact", "routes_artifact"):
        reference = proposal.contract.get(name)
        if (
            not isinstance(reference, dict)
            or set(reference) != {"artifact_id", "sha256"}
            or not isinstance(reference.get("artifact_id"), int)
            or not isinstance(reference.get("sha256"), str)
        ):
            raise CampaignRejected("planner interpretation lacks exact artifacts")
        artifact = Artifact.objects.filter(
            pk=reference["artifact_id"],
            campaign=proposal.campaign,
            work_order=planning_order,
        ).first()
        if artifact is None or artifact.digest != reference["sha256"]:
            raise CampaignRejected("planner interpretation artifact does not match")
        artifact_ids.append(artifact.pk)
    return planning_order, artifact_ids


def _originating_planner_order(proposal: Proposal) -> WorkOrder:
    interpretation = _planner_interpretation_ancestor(proposal)
    if interpretation is None:
        raise CampaignRejected(STALE_PLANNER_INPUT_MESSAGE)
    planning_order, _ = _planner_interpretation_source(interpretation)
    return planning_order


def _require_current_planner_input(
    proposal: Proposal,
    input_state: ResearchStateTransition,
) -> None:
    try:
        planning_order = _originating_planner_order(proposal)
    except CampaignRejected as exc:
        raise CampaignRejected(STALE_PLANNER_INPUT_MESSAGE) from exc
    if (
        planning_order.protocol != "planner"
        or planning_order.campaign_id != proposal.campaign_id
        or input_state.campaign_id != proposal.campaign_id
        or planning_order.input_state_id != input_state.pk
    ):
        raise CampaignRejected(STALE_PLANNER_INPUT_MESSAGE)


@transaction.atomic
def _approved_order(
    proposal: Proposal,
    *,
    user: object,
    input_artifact_ids: list[int] | None = None,
    input_state: ResearchStateTransition | None = None,
    supporting_states: list[ResearchStateTransition] | None = None,
    run_spec: RunSpecVersion | None = None,
) -> WorkOrder:
    if _is_planner_interpretation(proposal):
        raise CampaignRejected(
            "confirm the planner interpretation without creating research work"
        )
    if input_state is not None:
        input_state = (
            ResearchStateTransition.objects.select_for_update()
            .select_related(
                "workbench_artifact",
                "state_artifact",
                "delta_artifact",
            )
            .get(pk=input_state.pk)
        )
    _require_confirmed_planner_interpretation(proposal)
    state_contract = proposal.contract.get("research_state")
    continuation_requires_current_planner = False
    if proposal.protocol == "bound_work":
        if (
            run_spec is None
            or run_spec.campaign_id != proposal.campaign_id
            or proposal.contract.get("run_spec")
            != {"id": str(run_spec.pk), "sha256": run_spec.digest}
            or input_artifact_ids
            or input_state
            or supporting_states
        ):
            raise CampaignRejected("bound work lacks its exact run specification")
    elif run_spec is not None:
        raise CampaignRejected("run specification may authorize only bound work")
    elif proposal.protocol == "research_worker":
        if (
            not isinstance(state_contract, dict)
            or set(state_contract) != {"mode"}
            or state_contract["mode"] not in {"root", "continue"}
        ):
            raise CampaignRejected("research work lacks an exact state basis")
        if (state_contract["mode"] == "root") == bool(input_state):
            raise CampaignRejected("research work names the wrong state basis")
        continuation_requires_current_planner = (
            state_contract["mode"] == "continue"
        )
        if len(proposal.contract.get("workbenches", [])) != 1:
            raise CampaignRejected("research work requires one primary workbench")
        if len(proposal.contract.get("reasoning_operators", [])) != 1:
            raise CampaignRejected("research work requires one bounded reasoning operator")
        _text(proposal.contract.get("decision_hinge"), "research decision hinge")
        _text(proposal.contract.get("claim_ceiling"), "research claim ceiling")
        if supporting_states:
            raise CampaignRejected(
                "research-state evolution has one exact parent; use synthesis "
                "to combine independent branches"
            )
    elif supporting_states and proposal.protocol != "synthesis":
        raise CampaignRejected(
            "only synthesis may combine independent supporting research states"
        )
    supporting = sorted(
        {item.pk: item for item in supporting_states or []}.values(),
        key=lambda item: str(item.pk),
    )
    for item in supporting:
        disposition = getattr(item, "disposition", None)
        if (
            item.campaign_id != proposal.campaign_id
            or item.pk == getattr(input_state, "pk", None)
            or not disposition
            or disposition.kind != ResearchStateDisposition.Kind.ACCEPTED
            or item.successors.filter(
                disposition__kind=ResearchStateDisposition.Kind.ACCEPTED
            ).exists()
        ):
            raise CampaignRejected("supporting research state is not an active accepted leaf")
    disposition = getattr(input_state, "disposition", None) if input_state else None
    state_basis = WorkOrder.StateBasis.COMMISSION
    if input_state:
        if input_state.successors.filter(
            disposition__kind=ResearchStateDisposition.Kind.ACCEPTED
        ).exists():
            raise CampaignRejected("research state has an accepted successor")
        state_basis = (
            WorkOrder.StateBasis.CHALLENGED_TRANSITION
            if disposition
            and disposition.kind == ResearchStateDisposition.Kind.CHALLENGED
            and proposal.protocol == "adversarial_review"
            else WorkOrder.StateBasis.ACCEPTED_TRANSITION
        )
        if (
            state_basis == WorkOrder.StateBasis.ACCEPTED_TRANSITION
            and (
                not disposition
                or disposition.kind != ResearchStateDisposition.Kind.ACCEPTED
            )
        ):
            raise CampaignRejected("research state is not accepted for continuation")
    if continuation_requires_current_planner:
        _require_current_planner_input(proposal, input_state)
    _disposition(
        proposal,
        user=user,
        kind=ProposalDisposition.Kind.APPROVED,
    )
    order_id, role_id = uuid.uuid4(), uuid.uuid4()
    artifacts = sorted(set(input_artifact_ids or []))
    state_artifact_ids = set(
        proposal.campaign.state_transitions.values_list(
            "workbench_artifact_id", flat=True
        )
    ) | set(
        proposal.campaign.state_transitions.values_list(
            "state_artifact_id", flat=True
        )
    ) | set(
        proposal.campaign.state_transitions.values_list(
            "delta_artifact_id", flat=True
        )
    )
    if state_artifact_ids.intersection(artifacts):
        raise CampaignRejected(
            "research state must use the typed state-input authority"
        )
    if input_state:
        artifacts = sorted(
            set(
                artifacts
                + [
                    input_state.workbench_artifact_id,
                    input_state.state_artifact_id,
                    input_state.delta_artifact_id,
                ]
            )
        )
    for item in supporting:
        artifacts.extend(
            [
                item.workbench_artifact_id,
                item.state_artifact_id,
                item.delta_artifact_id,
            ]
        )
    artifacts = sorted(set(artifacts))
    owned = list(
        Artifact.objects.filter(
            campaign=proposal.campaign, pk__in=artifacts
        ).order_by("pk")
    )
    if [item.pk for item in owned] != artifacts:
        raise CampaignRejected("work-order input crosses campaign custody")
    def materialized(item: Artifact) -> str:
        suffix = Path(item.relative_path).suffix or ".bin"
        return str(
            Path(proposal.campaign.artifact_root)
            / "dispatches"
            / f"{order_id}.inputs"
            / f"{item.pk}-{item.digest}{suffix}"
        )

    input_rows = [
        {
            "artifact_id": item.pk,
            "sha256": item.digest,
            "media_type": item.media_type,
            "materialized_path": materialized(item),
        }
        for item in owned
    ]
    input_by_id = {item["artifact_id"]: item for item in input_rows}
    packet = {
        "schema_version": "research-work-order/v1",
        "campaign_id": str(proposal.campaign_id),
        "research_case_id": str(proposal.campaign_id),
        "work_order_id": str(order_id),
        "logical_role_id": str(role_id),
        "proposal_id": str(proposal.pk),
        "proposal_digest": proposal.digest,
        "protocol": proposal.protocol,
        "decision_use": proposal.campaign.equities_decision_use,
        "evidence_cutoff": proposal.campaign.evidence_cutoff.isoformat(),
        "task": proposal.task,
        "contract": proposal.contract,
        "output_contract": _output_contract(
            proposal.campaign, order_id, proposal.protocol
        ),
        "required_read_policy": (
            "Read every exact required_reads path before work; verify its SHA-256 "
            "and fail rather than substitute changed cognition."
        ),
        "required_reads": _required_reads(proposal),
        "inputs": input_rows,
        "research_state_input": (
            {
                "basis": state_basis,
                "transition_id": str(input_state.pk),
                "transition_sha256": input_state.digest,
                "workbench_result_artifact_id": input_state.workbench_artifact_id,
                "workbench_result_sha256": input_state.workbench_artifact.digest,
                "workbench_result_materialized_path": input_by_id[
                    input_state.workbench_artifact_id
                ]["materialized_path"],
                "state_artifact_id": input_state.state_artifact_id,
                "state_sha256": input_state.state_artifact.digest,
                "state_materialized_path": input_by_id[
                    input_state.state_artifact_id
                ]["materialized_path"],
                "delta_artifact_id": input_state.delta_artifact_id,
                "delta_sha256": input_state.delta_artifact.digest,
                "delta_materialized_path": input_by_id[
                    input_state.delta_artifact_id
                ]["materialized_path"],
            }
            if input_state
            else {"basis": WorkOrder.StateBasis.COMMISSION}
        ),
        "supporting_research_states": [
            {
                "transition_id": str(item.pk),
                "transition_sha256": item.digest,
                "workbench_result_artifact_id": item.workbench_artifact_id,
                "workbench_result_sha256": item.workbench_artifact.digest,
                "workbench_result_materialized_path": input_by_id[
                    item.workbench_artifact_id
                ]["materialized_path"],
                "state_artifact_id": item.state_artifact_id,
                "state_sha256": item.state_artifact.digest,
                "state_materialized_path": input_by_id[
                    item.state_artifact_id
                ]["materialized_path"],
                "delta_artifact_id": item.delta_artifact_id,
                "delta_sha256": item.delta_artifact.digest,
                "delta_materialized_path": input_by_id[
                    item.delta_artifact_id
                ]["materialized_path"],
            }
            for item in supporting
        ],
    }
    if run_spec is not None:
        packet = canonical_bound_work_packet(
            campaign=proposal.campaign,
            proposal=proposal,
            run_spec=run_spec,
            order_id=order_id,
            logical_role_id=role_id,
        )
    identity = {
        "id": str(order_id),
        "campaign": str(proposal.campaign_id),
        "proposal": str(proposal.pk),
        "logical_role_id": str(role_id),
        "protocol": proposal.protocol,
        "proposal_digest": proposal.digest,
        "input_artifact_ids": artifacts,
        "state_basis": state_basis,
        "input_state": str(input_state.pk) if input_state else None,
        "packet": packet,
    }
    if run_spec is not None:
        identity["run_spec"] = str(run_spec.pk)
        identity["run_spec_sha256"] = run_spec.digest
    try:
        return WorkOrder.objects.create(
            id=order_id,
            campaign=proposal.campaign,
            proposal=proposal,
            run_spec=run_spec,
            logical_role_id=role_id,
            protocol=proposal.protocol,
            proposal_digest=proposal.digest,
            input_artifact_ids=artifacts,
            state_basis=state_basis,
            input_state=input_state,
            packet=packet,
            digest=canonical_digest(identity),
        )
    except (IntegrityError, ValidationError) as exc:
        raise CampaignRejected("work-order creation failed closed") from exc


def approve_planner_programme(
    campaign: ResearchCampaign, user: object
) -> WorkOrder:
    require_director(campaign, user)
    if campaign.work_orders.exists():
        raise CampaignRejected("campaign already has an authorized first step")
    research_frame = next(
        item
        for item in skill_catalog()
        if item["name"] == "research-frame-search-with-domain-mechanisms"
    )
    proposal = record_proposal(
        campaign=campaign,
        author=Proposal.Author.DIRECTOR,
        author_user=user,
        protocol="planner",
        title="Design the research programme",
        task=campaign.commissioned_question,
        contract={
            "decision_use": campaign.equities_decision_use,
            "evidence_cutoff": campaign.evidence_cutoff.isoformat(),
            "required_output": "research-programme/v1",
            "authority_limit": "proposals_only",
            "workbench_catalog": workbench_catalog(),
            "skill_catalog": skill_catalog(),
            "reasoning_operators": [
                {
                    **research_frame,
                    "failure_tested": "proxy-to-target substitution at planning",
                    "expected_epistemic_delta": (
                        "decision hinge, rivals, discriminators, and bounded routes"
                    ),
                    "kill_condition": "no proposed route can change the decision read",
                }
            ],
        },
    )
    return _approved_order(proposal, user=user)


@transaction.atomic
def request_planner_reentry(
    transition: ResearchStateTransition,
    user: object,
) -> WorkOrder:
    transition = (
        ResearchStateTransition.objects.select_for_update()
        .select_related(
            "campaign",
            "workbench_artifact",
            "state_artifact",
            "delta_artifact",
        )
        .get(pk=transition.pk)
    )
    require_director(transition.campaign, user)
    if transition.successors.filter(
        disposition__kind=ResearchStateDisposition.Kind.ACCEPTED
    ).exists():
        raise CampaignRejected("research state has an accepted successor")
    disposition = getattr(transition, "disposition", None)
    if (
        disposition is None
        or disposition.kind != ResearchStateDisposition.Kind.ACCEPTED
    ):
        raise CampaignRejected("research state is not accepted for continuation")
    research_frame = next(
        item
        for item in skill_catalog()
        if item["name"] == "research-frame-search-with-domain-mechanisms"
    )
    proposal = record_proposal(
        campaign=transition.campaign,
        author=Proposal.Author.DIRECTOR,
        author_user=user,
        protocol="planner",
        title="Re-plan from current evidence",
        task=(
            "Re-plan the authorised research programme from the supplied accepted "
            "research state. Return proposed next research, challenge, synthesis, "
            "stop or bounded refusal for director disposition. Do not execute "
            "follow-on research."
        ),
        contract={
            "decision_use": transition.campaign.equities_decision_use,
            "evidence_cutoff": transition.campaign.evidence_cutoff.isoformat(),
            "required_output": "research-programme/v1",
            "authority_limit": "proposals_only",
            "replans_transition_id": str(transition.pk),
            "workbench_catalog": workbench_catalog(),
            "skill_catalog": skill_catalog(),
            "reasoning_operators": [
                {
                    **research_frame,
                    "failure_tested": (
                        "stale programme after material research evidence"
                    ),
                    "expected_epistemic_delta": (
                        "preserve, revise, park, cancel, synthesize, stop, or "
                        "refuse from the supplied current state"
                    ),
                    "kill_condition": (
                        "no proposed programme action changes because of the "
                        "supplied state"
                    ),
                }
            ],
        },
    )
    return _approved_order(
        proposal,
        user=user,
        input_state=transition,
    )


def approve_proposal(
    proposal: Proposal,
    *,
    user: object,
    input_artifact_ids: list[int] | None = None,
    input_state: ResearchStateTransition | None = None,
    supporting_states: list[ResearchStateTransition] | None = None,
) -> ProposalDisposition | WorkOrder:
    if _is_planner_interpretation(proposal):
        return _disposition(
            proposal,
            user=user,
            kind=ProposalDisposition.Kind.APPROVED,
        )
    return _approved_order(
        proposal,
        user=user,
        input_artifact_ids=input_artifact_ids,
        input_state=input_state,
        supporting_states=supporting_states,
    )


def reject_proposal(
    proposal: Proposal, user: object, *, reason: str = ""
) -> ProposalDisposition:
    return _disposition(
        proposal,
        user=user,
        kind=ProposalDisposition.Kind.REJECTED,
        feedback=reason,
    )


def request_proposal_revision(
    proposal: Proposal, user: object, *, feedback: str = ""
) -> ProposalDisposition:
    with transaction.atomic():
        if _is_planner_interpretation(proposal) and (
            not isinstance(feedback, str) or not feedback.strip()
        ):
            raise CampaignRejected("rough feedback is required")
        disposition = _disposition(
            proposal,
            user=user,
            kind=ProposalDisposition.Kind.REVISION_REQUESTED,
            feedback=feedback,
        )
        source_order = None
        input_artifact_ids: list[int] = []
        if _is_planner_interpretation(proposal):
            source_order, input_artifact_ids = _planner_interpretation_source(
                proposal
            )
        revision = record_proposal(
            campaign=proposal.campaign,
            author=Proposal.Author.DIRECTOR,
            author_user=user,
            protocol="planner",
            title=f"Revise: {proposal.title}"[:240],
            task="Return a revised proposal; do not perform the research.",
            contract={
                **(source_order.proposal.contract if source_order else {}),
                "authority_limit": "proposals_only",
                "revises_proposal_id": str(proposal.pk),
                "director_feedback": feedback,
            },
        )
        _approved_order(
            revision,
            user=user,
            input_artifact_ids=input_artifact_ids,
        )
        return disposition


def rewrite_proposal(
    proposal: Proposal,
    user: object,
    *,
    protocol: str,
    task: str,
    rationale: str,
) -> Proposal:
    require_director(proposal.campaign, user)
    if (
        not hasattr(proposal, "disposition")
        or proposal.disposition.kind == ProposalDisposition.Kind.APPROVED
    ):
        raise CampaignRejected("rewrite requires a rejected or revision parent")
    return record_proposal(
        campaign=proposal.campaign,
        parent=proposal,
        author=Proposal.Author.DIRECTOR,
        author_user=user,
        protocol=protocol or proposal.protocol,
        title=task[:240],
        task=task,
        contract={**proposal.contract, "director_rationale": _text(rationale, "rationale")},
    )


def _state_disposition(
    transition: ResearchStateTransition,
    *,
    user: object,
    kind: str,
    feedback: str = "",
) -> ResearchStateDisposition:
    require_director(transition.campaign, user)
    if hasattr(transition, "disposition"):
        raise CampaignRejected("research state already has a terminal disposition")
    try:
        return ResearchStateDisposition.objects.create(
            transition=transition,
            kind=kind,
            actor=user,
            feedback=feedback.strip(),
        )
    except (IntegrityError, ValidationError) as exc:
        raise CampaignRejected("research-state disposition failed closed") from exc


@transaction.atomic
def accept_research_state(
    transition: ResearchStateTransition, user: object
) -> ResearchStateDisposition:
    transition = ResearchStateTransition.objects.select_for_update().get(
        pk=transition.pk
    )
    if transition.parent_id:
        ResearchStateTransition.objects.select_for_update().get(
            pk=transition.parent_id
        )
        if ResearchStateTransition.objects.filter(
            parent_id=transition.parent_id,
            disposition__kind=ResearchStateDisposition.Kind.ACCEPTED,
        ).exclude(pk=transition.pk).exists():
            raise CampaignRejected(
                "research state already has an accepted successor"
            )
    return _state_disposition(
        transition,
        user=user,
        kind=ResearchStateDisposition.Kind.ACCEPTED,
    )


def reject_research_state(
    transition: ResearchStateTransition, user: object, *, reason: str = ""
) -> ResearchStateDisposition:
    return _state_disposition(
        transition,
        user=user,
        kind=ResearchStateDisposition.Kind.REJECTED,
        feedback=reason,
    )


def challenge_research_state(
    transition: ResearchStateTransition, user: object, *, feedback: str
) -> WorkOrder:
    feedback = _text(feedback, "challenge feedback")
    modes = next(
        item for item in skill_catalog() if item["name"] == "modes-of-reasoning-panel"
    )
    with transaction.atomic():
        _state_disposition(
            transition,
            user=user,
            kind=ResearchStateDisposition.Kind.CHALLENGED,
            feedback=feedback,
        )
        proposal = record_proposal(
            campaign=transition.campaign,
            parent=transition.work_order.proposal,
            author=Proposal.Author.DIRECTOR,
            author_user=user,
            protocol="adversarial_review",
            title=f"Challenge: {transition.work_order.proposal.title}"[:240],
            task=(
                "Attack the exact candidate research state and propose the smallest "
                "route-back; do not repair or accept it."
            ),
            contract={
                "research_state": {"mode": "continue"},
                "challenged_transition_id": str(transition.pk),
                "director_feedback": feedback,
                "reasoning_operators": [
                    {
                        **modes,
                        "failure_tested": feedback,
                        "expected_epistemic_delta": (
                            "identify a concrete block, narrowing, or route-back"
                        ),
                        "kill_condition": "no claim, route, or refusal would change",
                    }
                ],
            },
        )
        return _approved_order(proposal, user=user, input_state=transition)


def adapter() -> NtmAdapter:
    return NtmAdapter(
        Path(settings.NTM_BINARY),
        timeout_seconds=settings.NTM_CONTROL_TIMEOUT_SECONDS,
    )


def _verify_required_reads(order: WorkOrder) -> str:
    expected = _required_reads(order.proposal)
    if order.packet.get("required_reads") != expected:
        raise CampaignRejected("frozen cognition read contract changed")
    for item in expected:
        path = Path(item["path"])
        if (
            path.is_symlink()
            or not path.is_file()
            or sha256(path.read_bytes()).hexdigest() != item["sha256"]
        ):
            raise CampaignRejected("frozen cognition input is unavailable")
        if item["kind"] == "reasoning_skill":
            package_root = path.parent
            observed: dict[str, str] = {}
            if package_root.is_symlink() or not package_root.is_dir():
                raise CampaignRejected("frozen cognition skill package is unavailable")
            for candidate in package_root.rglob("*"):
                relative = candidate.relative_to(package_root)
                if "__pycache__" in relative.parts or candidate.suffix == ".pyc":
                    continue
                if candidate.is_symlink():
                    raise CampaignRejected(
                        "frozen cognition skill package contains a symlink"
                    )
                if candidate.is_file():
                    observed[relative.as_posix()] = sha256(
                        candidate.read_bytes()
                    ).hexdigest()
            locked = {
                row["path"]: row["sha256"] for row in item["package_files"]
            }
            if observed != locked or len(observed) != item["file_count"]:
                raise CampaignRejected("frozen cognition skill package changed")
    return next(
        item["sha256"] for item in expected if item["kind"] == "role_protocol"
    )


def _validate_runtime_contract(order: WorkOrder) -> None:
    if order.protocol == "bound_work":
        if order.run_spec_id is None:
            raise CampaignRejected("bound work lacks an immutable run specification")
        try:
            order.run_spec.full_clean()
            order.full_clean()
        except ValidationError as exc:
            raise CampaignRejected("bound work no longer matches its exact run specification") from exc
        expected_packet = canonical_bound_work_packet(
            campaign=order.campaign,
            proposal=order.proposal,
            run_spec=order.run_spec,
            order_id=order.pk,
            logical_role_id=order.logical_role_id,
        )
        if order.packet != expected_packet:
            raise CampaignRejected("bound work packet changed from its canonical specification")
    try:
        _output_root(order)
    except CampaignRejected as exc:
        raise CampaignRejected(
            "approved work predates or no longer matches the current execution "
            "contract; authorize a new work order"
        ) from exc
    _verify_required_reads(order)


def _control_files(
    order: WorkOrder, *, require_open_output: bool = True
) -> tuple[Path, Path]:
    root = Path(order.campaign.artifact_root)
    control = root / "_control"
    control.mkdir(exist_ok=True)
    protocol_digest = _verify_required_reads(order)
    output_root = _output_root(order)
    if require_open_output and not output_root.is_dir():
        raise CampaignRejected("work-order output root is unavailable at launch")
    try:
        trace_args = build_codex_trace_arguments(
            base_url=settings.LANGFUSE_TARGET_BASE_URL,
            campaign_id=str(order.campaign_id),
            work_order_id=str(order.pk),
            proposal_digest=order.proposal_digest,
            role_id=str(order.logical_role_id),
            role_contract_digest=protocol_digest,
        )
    except LangfuseRejected as exc:
        raise CampaignRejected(str(exc)) from exc
    codex = Path(settings.CAMPAIGN_CODEX_BINARY)
    if not codex.is_absolute() or not codex.is_file():
        raise CampaignRejected("Codex executable is not pinned")
    launcher = (
        "#!/bin/sh\nset -eu\n"
        "exec "
        + shlex.quote(str(codex))
        + " --sandbox workspace-write --ask-for-approval never --search --cd "
        + shlex.quote(str(output_root))
        + " "
        + " ".join(shlex.quote(item) for item in trace_args)
        + ' -m "$1"\n'
    ).encode()
    launcher_path = control / f"codex-{sha256(launcher).hexdigest()}.sh"
    if not launcher_path.exists():
        launcher_path.write_bytes(launcher)
        launcher_path.chmod(0o700)
    elif launcher_path.read_bytes() != launcher:
        raise CampaignRejected("frozen Codex launcher changed")
    config = (
        "[agents]\n"
        f"codex = '''{launcher_path} "
        '{{shellQuote (.Model | default "'
        f'{settings.CAMPAIGN_CODEX_MODEL}'
        "\")}}'''\n"
        "[models]\n"
        f'default_codex = "{settings.CAMPAIGN_CODEX_MODEL}"\n'
    ).encode()
    config_path = control / f"ntm-{sha256(config).hexdigest()}.toml"
    if not config_path.exists():
        config_path.write_bytes(config)
    elif config_path.read_bytes() != config:
        raise CampaignRejected("frozen NTM configuration changed")
    return launcher_path, config_path


def _tracked_send_target(argv: list[str]) -> str | None:
    targets = [
        item.split("=", 1)[1]
        for item in argv
        if re.fullmatch(r"--panes=[1-9][0-9]*", item)
    ]
    return targets[0] if len(targets) == 1 else None


def _launch_response_succeeded(response: object, *, session: str) -> bool:
    if (
        not isinstance(response, dict)
        or response.get("session") != session
        or "error" in response
    ):
        return False
    if response.get("success") is True:
        agents = response.get("agents")
        return bool(
            isinstance(agents, list)
            and len(agents) == 1
            and isinstance(agents[0], dict)
            and isinstance(agents[0].get("title"), str)
            and agents[0]["title"]
        )
    panes = response.get("new_panes")
    if (
        response.get("success") is False
        or response.get("added_codex") != 1
        or response.get("total_added") != 1
        or not isinstance(panes, list)
        or len(panes) != 1
        or not isinstance(panes[0], dict)
    ):
        return False
    pane = panes[0]
    return bool(
        pane.get("type") == "cod"
        and isinstance(pane.get("title"), str)
        and pane["title"]
        and isinstance(pane.get("command"), str)
        and pane["command"]
        and isinstance(response.get("generated_at"), str)
        and response["generated_at"]
    )


def _tracked_send_succeeded(
    response: object,
    *,
    session: str,
    target: str | None,
) -> bool:
    if not isinstance(response, dict) or target is None:
        return False
    sent, ack = response.get("send"), response.get("ack")
    if not isinstance(sent, dict) or not isinstance(ack, dict):
        return False
    confirmations = ack.get("confirmations")
    return bool(
        response.get("success") is True
        and sent.get("success") is True
        and sent.get("session") == session
        and sent.get("blocked") is False
        and sent.get("targets") == [target]
        and sent.get("successful") == [target]
        and sent.get("failed") == []
        and ack.get("success") is True
        and ack.get("session") == session
        and isinstance(confirmations, list)
        and len(confirmations) == 1
        and isinstance(confirmations[0], dict)
        and confirmations[0].get("pane") == target
        and confirmations[0].get("ack_type")
        in {
            "prompt_returned",
            "echo_detected",
            "explicit_ack",
            "output_started",
        }
        and ack.get("pending") == []
        and ack.get("failed") == []
        and ack.get("timed_out") is False
    )


def _status_response_succeeded(
    response: object, *, session: str
) -> bool:
    if not isinstance(response, dict) or response.get("session") != session:
        return False
    if response.get("condition") == "complete":
        return response.get("success") is True
    return bool(
        response.get("exists") is True
        and isinstance(response.get("generated_at"), str)
        and response["generated_at"]
        and isinstance(response.get("working_directory"), str)
        and isinstance(response.get("panes"), list)
        and isinstance(response.get("agent_counts"), dict)
        and "error" not in response
    )


def _stop_response_succeeded(
    response: object, *, session: str
) -> bool:
    return bool(
        isinstance(response, dict)
        and response.get("killed") is True
        and response.get("session") == session
        and isinstance(response.get("generated_at"), str)
        and response["generated_at"]
        and "error" not in response
    )


def _runtime_event(
    *,
    campaign: ResearchCampaign,
    order: WorkOrder | None,
    kind: str,
    argv: list[str],
    result: ExecutionResult,
) -> RuntimeEvent:
    event_id = uuid.uuid4()
    response = result.response if isinstance(result.response, (dict, list)) else None
    response_succeeded = bool(
        isinstance(response, dict) and response.get("success") is True
    )
    if kind == RuntimeEvent.Kind.LAUNCH:
        response_succeeded = _launch_response_succeeded(
            response, session=campaign.ntm_session
        )
    elif kind == RuntimeEvent.Kind.SEND:
        response_succeeded = _tracked_send_succeeded(
            response,
            session=campaign.ntm_session,
            target=_tracked_send_target(argv),
        )
    elif kind == RuntimeEvent.Kind.STATUS:
        response_succeeded = _status_response_succeeded(
            response, session=campaign.ntm_session
        )
    elif kind == RuntimeEvent.Kind.STOP:
        response_succeeded = _stop_response_succeeded(
            response, session=campaign.ntm_session
        )
    succeeded = bool(
        result.exit_code == 0 and not result.timed_out and response_succeeded
    )
    payload = {
        "id": str(event_id),
        "campaign": str(campaign.pk),
        "work_order": str(order.pk) if order else None,
        "kind": kind,
        "generation": 1,
        "request": {"argv": argv},
        "response": response,
        "succeeded": succeeded,
    }
    return RuntimeEvent.objects.create(
        id=event_id,
        campaign=campaign,
        work_order=order,
        kind=kind,
        request=payload["request"],
        response=response,
        succeeded=succeeded,
        digest=canonical_digest(payload),
    )


def _execute(
    *,
    campaign: ResearchCampaign,
    order: WorkOrder | None,
    kind: str,
    argv: list[str],
    control: NtmAdapter,
    environment: dict[str, str],
) -> RuntimeEvent:
    return _runtime_event(
        campaign=campaign,
        order=order,
        kind=kind,
        argv=argv,
        result=control.execute(argv, environment=environment),
    )


def launch_role(
    order: WorkOrder, user: object, control: NtmAdapter | None = None
) -> RuntimeEvent:
    campaign = order.campaign
    require_director(campaign, user)
    if order.runtime_events.filter(kind=RuntimeEvent.Kind.LAUNCH).exists():
        raise CampaignRejected("work order already has a launch attempt")
    _validate_runtime_contract(order)
    runtime_source = _preflight_langfuse_runtime(environ)
    _prepare_output_root(order)
    _, config = _control_files(order)
    control = control or adapter()
    prior = RuntimeEvent.objects.filter(
        campaign=campaign,
        kind=RuntimeEvent.Kind.LAUNCH,
        succeeded=True,
    ).exists()
    role_name = "planner" if order.protocol == "planner" else "researcher"
    argv = (
        control.add_command(
            campaign.ntm_session, settings.CAMPAIGN_CODEX_MODEL, config
        )
        if prior
        else control.spawn_command(
            campaign.ntm_session, PROTOTYPE_ROOT, role_name, config
        )
    )
    try:
        environment = campaign_launch_environment(runtime_source)
    except LangfuseRejected as exc:
        raise CampaignRejected(str(exc)) from exc
    return _execute(
        campaign=campaign,
        order=order,
        kind=RuntimeEvent.Kind.LAUNCH,
        argv=argv,
        control=control,
        environment=environment,
    )


def refresh_status(
    order: WorkOrder, user: object, control: NtmAdapter | None = None
) -> RuntimeEvent:
    campaign = order.campaign
    require_director(campaign, user)
    _validate_runtime_contract(order)
    _, config = _control_files(order)
    control = control or adapter()
    sent = order.runtime_events.filter(
        kind=RuntimeEvent.Kind.SEND, succeeded=True
    ).first()
    if sent is not None:
        return _execute(
            campaign=campaign,
            order=order,
            kind=RuntimeEvent.Kind.STATUS,
            argv=control.completion_command(
                campaign.ntm_session, _target_index(order), config
            ),
            control=control,
            environment=sanitized_control_environment(environ),
        )
    return _execute(
        campaign=campaign,
        order=order,
        kind=RuntimeEvent.Kind.STATUS,
        argv=control.status_command(campaign.ntm_session, config),
        control=control,
        environment=sanitized_control_environment(environ),
    )


def _target_index(order: WorkOrder) -> int:
    launch = order.runtime_events.filter(
        kind=RuntimeEvent.Kind.LAUNCH, succeeded=True
    ).first()
    statuses = order.runtime_events.filter(
        kind=RuntimeEvent.Kind.STATUS, succeeded=True
    ).order_by("-created_at")
    if launch is None:
        raise CampaignRejected("refresh exact NTM readiness before sending")
    expected_title = None
    if isinstance(launch.response, dict):
        agents = launch.response.get("agents")
        added = launch.response.get("new_panes")
        rows = agents if isinstance(agents, list) else added
        if isinstance(rows, list) and len(rows) == 1 and isinstance(rows[0], dict):
            expected_title = rows[0].get("title")
    for status in statuses:
        if not isinstance(status.response, dict):
            continue
        panes = status.response.get("panes")
        if not isinstance(panes, list):
            continue
        matches = [
            pane
            for pane in panes
            if isinstance(pane, dict)
            and pane.get("title") == expected_title
            and pane.get("type") == "codex"
            and pane.get("command") == "codex"
            and pane.get("context_model") == settings.CAMPAIGN_CODEX_MODEL
        ]
        if len(matches) == 1 and isinstance(matches[0].get("index"), int):
            return matches[0]["index"]
    raise CampaignRejected("exact Codex work state is not ready")


def _completion_observed(order: WorkOrder) -> bool:
    sent = order.runtime_events.filter(
        kind=RuntimeEvent.Kind.SEND, succeeded=True
    ).order_by("-created_at").first()
    if (
        sent is None
        or not _tracked_send_succeeded(
            sent.response,
            session=order.campaign.ntm_session,
            target=_tracked_send_target(sent.request.get("argv", [])),
        )
    ):
        return False
    target = _tracked_send_target(sent.request.get("argv", []))
    for event in order.runtime_events.filter(
        kind=RuntimeEvent.Kind.STATUS,
        succeeded=True,
        created_at__gte=sent.created_at,
    ).order_by("-created_at"):
        response = event.response
        agents = response.get("agents") if isinstance(response, dict) else None
        if (
            _tracked_send_target(event.request.get("argv", [])) == target
            and isinstance(response, dict)
            and response.get("success") is True
            and response.get("session") == order.campaign.ntm_session
            and response.get("condition") == "complete"
            and isinstance(agents, list)
            and len(agents) == 1
            and isinstance(agents[0], dict)
            and isinstance(agents[0].get("pane"), str)
            and agents[0]["pane"]
            and agents[0].get("state") == "WAITING"
            and agents[0].get("agent_type") == "codex"
        ):
            return True
    return False


def _dispatch_path(order: WorkOrder) -> Path:
    root = Path(order.campaign.artifact_root)
    path = root / "dispatches" / f"{order.pk}.json"
    path.parent.mkdir(exist_ok=True)
    inputs = {
        item.pk: item
        for item in Artifact.objects.filter(
            campaign=order.campaign,
            pk__in=[row["artifact_id"] for row in order.packet["inputs"]],
        )
    }
    for row in order.packet["inputs"]:
        artifact = inputs.get(row["artifact_id"])
        materialized = Path(row["materialized_path"])
        expected = (
            root
            / "dispatches"
            / f"{order.pk}.inputs"
            / f"{row['artifact_id']}-{row['sha256']}{Path(artifact.relative_path).suffix or '.bin'}"
            if artifact
            else None
        )
        if (
            artifact is None
            or artifact.digest != row["sha256"]
            or artifact.media_type != row["media_type"]
            or materialized != expected
            or materialized.is_symlink()
        ):
            raise CampaignRejected("work-order input materialization is invalid")
        materialized.parent.mkdir(parents=True, exist_ok=True)
        content = bytes(artifact.content)
        if materialized.exists():
            if not materialized.is_file() or materialized.read_bytes() != content:
                raise CampaignRejected("materialized work-order input changed")
        else:
            materialized.write_bytes(content)
            materialized.chmod(0o400)
    if order.run_spec_id:
        job_inputs = {
            str(item.pk): item
            for item in ArtifactVersion.objects.filter(
                campaign=order.campaign,
                pk__in=[row["id"] for row in order.packet["job_input_files"]],
            )
        }
        for row in order.packet["job_input_files"]:
            artifact = job_inputs.get(row["id"])
            materialized = Path(row["materialized_path"])
            expected = (
                root
                / "dispatches"
                / f"{order.pk}.inputs"
                / f"{row['id']}-{row['sha256']}{Path(row['filename']).suffix or '.bin'}"
            )
            if (
                artifact is None
                or artifact.digest != row["sha256"]
                or artifact.role != row["role"]
                or artifact.filename != row["filename"]
                or artifact.media_type != row["media_type"]
                or materialized != expected
                or materialized.is_symlink()
            ):
                raise CampaignRejected("bound job input materialization is invalid")
            materialized.parent.mkdir(parents=True, exist_ok=True)
            content = bytes(artifact.content)
            if materialized.exists():
                if not materialized.is_file() or materialized.read_bytes() != content:
                    raise CampaignRejected("materialized bound job input changed")
            else:
                materialized.write_bytes(content)
                materialized.chmod(0o400)
        _verify_materialized_bound_inputs(order)
    _prepare_output_root(order)
    content = canonical_bytes(order.packet)
    if not path.exists():
        path.write_bytes(content)
    elif path.read_bytes() != content:
        raise CampaignRejected("frozen work-order packet changed")
    return path


def _verify_materialized_bound_inputs(order: WorkOrder) -> None:
    if order.protocol != "bound_work" or order.run_spec_id is None:
        raise CampaignRejected("bound input verification requires exact bound work")
    campaign_root = Path(order.campaign.artifact_root)
    input_root = campaign_root / "dispatches" / f"{order.pk}.inputs"
    if (
        not campaign_root.is_absolute()
        or campaign_root.is_symlink()
        or not campaign_root.is_dir()
        or input_root.is_symlink()
        or not input_root.is_dir()
    ):
        raise CampaignRejected("materialized bound job input population is invalid")
    current = input_root
    while current != campaign_root:
        if current.is_symlink():
            raise CampaignRejected("materialized bound job input path contains a symlink")
        current = current.parent

    rows = order.packet.get("job_input_files")
    if not isinstance(rows, list) or not rows:
        raise CampaignRejected("bound job lacks its materialized input contract")
    artifacts = {
        str(item.pk): item
        for item in ArtifactVersion.objects.filter(
            campaign=order.campaign,
            pk__in=[row.get("id") for row in rows if isinstance(row, dict)],
        )
    }
    expected_names: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise CampaignRejected("bound job input materialization is invalid")
        artifact = artifacts.get(row.get("id"))
        if artifact is None:
            raise CampaignRejected("bound job input materialization is invalid")
        expected = input_root / (
            f"{artifact.pk}-{artifact.digest}"
            f"{Path(artifact.filename).suffix or '.bin'}"
        )
        materialized = Path(str(row.get("materialized_path", "")))
        expected_names.add(expected.name)
        if (
            materialized != expected
            or row.get("sha256") != artifact.digest
            or row.get("role") != artifact.role
            or row.get("filename") != artifact.filename
            or row.get("media_type") != artifact.media_type
            or materialized.is_symlink()
            or not materialized.is_file()
        ):
            raise CampaignRejected("bound job input materialization is invalid")
        content = materialized.read_bytes()
        if (
            len(content) != len(bytes(artifact.content))
            or sha256(content).hexdigest() != artifact.digest
        ):
            raise CampaignRejected("materialized bound job input changed")
    if {path.name for path in input_root.iterdir()} != expected_names:
        raise CampaignRejected("materialized bound job input population changed")


def send_dispatch(
    order: WorkOrder, user: object, control: NtmAdapter | None = None
) -> RuntimeEvent:
    campaign = order.campaign
    require_director(campaign, user)
    if order.runtime_events.filter(kind=RuntimeEvent.Kind.SEND).exists():
        raise CampaignRejected("work order already has a send attempt")
    _validate_runtime_contract(order)
    target = _target_index(order)
    _, config = _control_files(order)
    control = control or adapter()
    return _execute(
        campaign=campaign,
        order=order,
        kind=RuntimeEvent.Kind.SEND,
        argv=control.send_command(
            campaign.ntm_session, target, _dispatch_path(order), config
        ),
        control=control,
        environment=sanitized_control_environment(environ),
    )


def stop_campaign(
    campaign: ResearchCampaign, user: object, control: NtmAdapter | None = None
) -> RuntimeEvent:
    require_director(campaign, user)
    order = campaign.work_orders.order_by("-created_at").first()
    if order is None:
        raise CampaignRejected("campaign has no authorized work")
    _, config = _control_files(order, require_open_output=False)
    control = control or adapter()
    return _execute(
        campaign=campaign,
        order=None,
        kind=RuntimeEvent.Kind.STOP,
        argv=control.stop_command(campaign.ntm_session, config),
        control=control,
        environment=sanitized_control_environment(environ),
    )


def _output_root(order: WorkOrder) -> Path:
    expected = _output_contract(order.campaign, order.pk, order.protocol)
    if order.packet.get("output_contract") != expected:
        raise CampaignRejected("frozen output custody contract changed")
    root = Path(expected["output_root"])
    campaign_root = Path(order.campaign.artifact_root)
    if (
        not root.is_absolute()
        or campaign_root.is_symlink()
        or not campaign_root.is_dir()
        or root != campaign_root / expected["campaign_relative_root"]
    ):
        raise CampaignRejected("frozen output custody root is invalid")
    return root


def _prepare_output_root(order: WorkOrder) -> Path:
    root = _output_root(order)
    sealed = root.parent / "sealed"
    if sealed.exists() or sealed.is_symlink():
        raise CampaignRejected("work-order output custody is already sealed")
    if root.exists():
        if root.is_symlink() or not root.is_dir() or any(root.iterdir()):
            raise CampaignRejected("work-order output root is not empty")
    else:
        root.mkdir(parents=True)
        root.chmod(0o700)
    current = root
    campaign_root = Path(order.campaign.artifact_root)
    while current != campaign_root:
        if current.is_symlink():
            raise CampaignRejected("work-order output path contains a symlink")
        current = current.parent
    return root


def _proposal_rows(content: bytes) -> list[dict[str, object]]:
    rows = []
    for line in content.splitlines():
        try:
            row = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CampaignRejected("planner proposal output is malformed") from exc
        if not isinstance(row, dict):
            raise CampaignRejected("planner proposal output is malformed")
        rows.append(row)
    return rows


def _output_files(
    root: Path, *, exact_paths: set[str] | None = None
) -> dict[str, bytes]:
    if root.is_symlink() or not root.is_dir():
        raise CampaignRejected("work-order output root is unavailable")
    paths = sorted(root.iterdir())
    if exact_paths is not None and {path.name for path in paths} != exact_paths:
        raise CampaignRejected("bound work output population is not exact")
    files: dict[str, bytes] = {}
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise CampaignRejected(
                "artifact population must contain regular files at its root only"
            )
        if path.stat().st_size > settings.CAMPAIGN_ARTIFACT_MAX_BYTES:
            raise CampaignRejected("artifact exceeds the custody limit")
        with path.open("rb") as stream:
            content = stream.read(settings.CAMPAIGN_ARTIFACT_MAX_BYTES + 1)
        if len(content) > settings.CAMPAIGN_ARTIFACT_MAX_BYTES:
            raise CampaignRejected("artifact exceeds the custody limit")
        files[path.name] = content
    return files


def _seal_output_root(order: WorkOrder) -> Path | None:
    root = _output_root(order)
    sealed = root.parent / "sealed"
    if root.exists() and sealed.exists():
        raise CampaignRejected("work-order output custody has conflicting roots")
    if sealed.exists():
        if sealed.is_symlink() or not sealed.is_dir():
            raise CampaignRejected("sealed output custody is invalid")
        return sealed
    if not root.exists():
        return None
    if root.is_symlink() or not root.is_dir():
        raise CampaignRejected("work-order output root is unavailable")
    root.rename(sealed)
    sealed.chmod(0o500)
    return sealed


def _validate_artifact_attestation(
    order: WorkOrder, content: bytes, outputs: Mapping[str, bytes]
) -> dict[str, object]:
    try:
        value = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CampaignRejected("artifact attestation is malformed") from exc
    required = {
        "schema_version",
        "campaign_id",
        "work_order_id",
        "logical_role_id",
        "artifacts",
        "authority",
    }
    rows = value.get("artifacts") if isinstance(value, dict) else None
    if (
        not isinstance(value, dict)
        or set(value) != required
        or value.get("schema_version")
        != "work-order-artifact-attestation/v1"
        or value.get("campaign_id") != str(order.campaign_id)
        or value.get("work_order_id") != str(order.pk)
        or value.get("logical_role_id") != str(order.logical_role_id)
        or value.get("authority") != "worker_candidate_attestation"
        or not isinstance(rows, list)
    ):
        raise CampaignRejected("artifact attestation is malformed")
    expected_rows = [
        {
            "relative_path": path,
            "byte_length": len(payload),
            "sha256": sha256(payload).hexdigest(),
        }
        for path, payload in sorted(outputs.items())
    ]
    if rows != expected_rows:
        raise CampaignRejected("artifact attestation does not match exact outputs")
    contract = order.packet.get("output_contract")
    required_paths = (
        contract.get("required_paths") if isinstance(contract, dict) else None
    )
    if (
        not isinstance(required_paths, list)
        or not set(required_paths).issubset(outputs)
    ):
        if order.protocol == "research_worker":
            raise CampaignRejected(
                "research work lacks exact workbench result, state, and "
                "epistemic delta"
            )
        raise CampaignRejected("work order lacks its required output population")
    if order.protocol == "bound_work":
        _validate_bound_outputs(order, outputs)
    return value


def _validate_bound_outputs(
    order: WorkOrder, outputs: Mapping[str, bytes]
) -> None:
    if set(outputs) != {"outcome.json", "run-acknowledgement.json"}:
        raise CampaignRejected("bound work must produce exactly one outcome and acknowledgement")
    try:
        acknowledgement = json.loads(outputs["run-acknowledgement.json"])
        outcome = json.loads(outputs["outcome.json"])
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CampaignRejected("bound work output is malformed") from exc
    expected_acknowledgement = {
        "schema_version": "bound-run-acknowledgement/v1",
        "campaign_id": str(order.campaign_id),
        "run_spec_id": str(order.run_spec_id),
        "run_spec_sha256": order.run_spec.digest if order.run_spec_id else None,
        "work_order_id": str(order.pk),
        "inputs": order.packet.get("job_inputs"),
    }
    if acknowledgement != expected_acknowledgement:
        raise CampaignRejected("worker did not acknowledge the exact bound run")
    required = {
        "schema_version", "kind", "authority", "summary", "candidate", "refusal"
    }
    if (
        not isinstance(outcome, dict)
        or set(outcome) != required
        or outcome.get("schema_version") != "bound-run-outcome/v1"
        or outcome.get("kind") not in {"candidate", "refusal"}
        or outcome.get("authority") != "provisional_only"
        or not isinstance(outcome.get("summary"), str)
        or not outcome["summary"].strip()
    ):
        raise CampaignRejected("bound work outcome is malformed")
    if outcome["kind"] == "candidate":
        if not isinstance(outcome.get("candidate"), dict) or not outcome["candidate"]:
            raise CampaignRejected("bound work candidate is empty")
        if outcome.get("refusal") is not None:
            raise CampaignRejected("bound work outcome contains conflicting dispositions")
    elif (
        outcome.get("candidate") is not None
        or not isinstance(outcome.get("refusal"), str)
        or not outcome["refusal"].strip()
    ):
        raise CampaignRejected("bound work refusal is not bounded")


def _stored_attestation(order: WorkOrder) -> tuple[Artifact, dict[str, object]]:
    attestations = list(
        order.artifacts.filter(
            relative_path="artifact-attestation.json"
        ).order_by("pk")
    )
    if len(attestations) != 1:
        raise CampaignRejected("work order lacks one artifact attestation")
    outputs = {
        item.relative_path: bytes(item.content)
        for item in order.artifacts.exclude(
            relative_path="artifact-attestation.json"
        ).order_by("relative_path")
    }
    return (
        attestations[0],
        _validate_artifact_attestation(
            order, bytes(attestations[0].content), outputs
        ),
    )


def collect_artifacts(campaign: ResearchCampaign, user: object) -> int:
    require_director(campaign, user)
    if campaign.trace_links.exists():
        raise CampaignRejected("correlated campaign custody is final")
    collected = 0
    for order in campaign.work_orders.order_by("created_at"):
        if order.artifacts.exists():
            _stored_attestation(order)
            continue
        if not _completion_observed(order):
            if not _output_root(order).exists():
                continue
            raise CampaignRejected(
                "observe exact work-order completion before collecting outputs"
            )
        if order.protocol == "bound_work":
            _verify_materialized_bound_inputs(order)
        root = _seal_output_root(order)
        if root is None:
            continue
        exact_output_paths = None
        if order.protocol == "bound_work":
            contract = order.packet["output_contract"]
            exact_output_paths = set(contract["required_paths"]) | {
                contract["attestation_path"]
            }
        files = _output_files(root, exact_paths=exact_output_paths)
        attestation_path = order.packet["output_contract"]["attestation_path"]
        attestation_content = files.pop(attestation_path, None)
        if attestation_content is None:
            raise CampaignRejected("work order lacks its final artifact attestation")
        _validate_artifact_attestation(order, attestation_content, files)
        files[attestation_path] = attestation_content
        pending: list[tuple[Path, str, bytes, str]] = []
        for relative, content in sorted(files.items()):
            path = root / relative
            digest = sha256(content).hexdigest()
            pending.append((path, relative, content, digest))

        transition_payload = None
        existing_transition = getattr(order, "state_transition", None)
        pending_by_path = {item[1]: item[2] for item in pending}
        state_paths = {
            "workbench-result.json",
            "research-state.json",
            "epistemic-delta.json",
        }
        if order.protocol == "research_worker":
            if existing_transition and state_paths.intersection(pending_by_path):
                raise CampaignRejected("research-state transition is already final")
            if not existing_transition:
                if not state_paths.issubset(pending_by_path):
                    raise CampaignRejected(
                        "research work lacks exact workbench result, state, and "
                        "epistemic delta"
                    )
                try:
                    transition_payload = validate_transition(
                        order,
                        workbench_content=pending_by_path[
                            "workbench-result.json"
                        ],
                        state_content=pending_by_path["research-state.json"],
                        delta_content=pending_by_path["epistemic-delta.json"],
                    )
                except ResearchStateRejected as exc:
                    raise CampaignRejected(str(exc)) from exc

        with transaction.atomic():
            created: dict[str, Artifact] = {}
            for path, relative, content, digest in pending:
                artifact = Artifact.objects.create(
                    campaign=campaign,
                    work_order=order,
                    kind=Path(relative).stem,
                    relative_path=relative,
                    version=1,
                    media_type=(
                        "application/json"
                        if path.suffix in {".json", ".jsonl"}
                        else "text/markdown"
                    ),
                    content=content,
                    digest=digest,
                )
                created[relative] = artifact
                collected += 1
                if (
                    order.protocol in {"planner", "adversarial_review"}
                    and relative == "proposals.jsonl"
                ):
                    parent_id = order.proposal.contract.get("revises_proposal_id")
                    parent = (
                        Proposal.objects.filter(
                            pk=parent_id, campaign=campaign
                        ).first()
                        if parent_id
                        else (
                            order.proposal
                            if order.protocol == "adversarial_review"
                            else None
                        )
                    )
                    if parent_id and parent is None:
                        raise CampaignRejected(
                            "planner revision target is unavailable"
                        )
                    if order.protocol == "planner":
                        try:
                            plan = created["plan.md"]
                            plan_text = bytes(plan.content).decode("utf-8")
                        except (KeyError, UnicodeDecodeError) as exc:
                            raise CampaignRejected(
                                "planner interpretation is unavailable"
                            ) from exc
                        parent = record_proposal(
                            campaign=campaign,
                            parent=parent,
                            author=Proposal.Author.PLANNER,
                            protocol="planner",
                            title="What I think you mean",
                            task=_text(plan_text, "planner interpretation"),
                            contract={
                                "authority_limit": (
                                    PLANNER_INTERPRETATION_AUTHORITY_LIMIT
                                ),
                                "planning_work_order_id": str(order.pk),
                                "plan_artifact": {
                                    "artifact_id": plan.pk,
                                    "sha256": plan.digest,
                                },
                                "routes_artifact": {
                                    "artifact_id": artifact.pk,
                                    "sha256": artifact.digest,
                                },
                            },
                            _system_interpretation=True,
                        )
                    for row in _proposal_rows(content):
                        record_proposal(
                            campaign=campaign,
                            parent=parent,
                            author=(
                                Proposal.Author.REVIEWER
                                if order.protocol == "adversarial_review"
                                else Proposal.Author.PLANNER
                            ),
                            protocol=_text(
                                row.get("protocol"), "proposal protocol", 80
                            ),
                            title=_text(row.get("title"), "proposal title", 240),
                            task=_text(row.get("task"), "proposal task"),
                            contract=row.get("contract"),
                        )
            if transition_payload:
                transition_id = uuid.uuid4()
                workbench_artifact = created["workbench-result.json"]
                state_artifact = created["research-state.json"]
                delta_artifact = created["epistemic-delta.json"]
                relation = {
                    "id": str(transition_id),
                    "campaign": str(campaign.pk),
                    "work_order": str(order.pk),
                    "parent": (
                        str(order.input_state_id) if order.input_state_id else None
                    ),
                    "workbench_artifact": workbench_artifact.pk,
                    "workbench_sha256": workbench_artifact.digest,
                    "state_artifact": state_artifact.pk,
                    "state_sha256": state_artifact.digest,
                    "delta_artifact": delta_artifact.pk,
                    "delta_sha256": delta_artifact.digest,
                }
                ResearchStateTransition.objects.create(
                    id=transition_id,
                    campaign=campaign,
                    work_order=order,
                    parent=order.input_state,
                    workbench_artifact=workbench_artifact,
                    state_artifact=state_artifact,
                    delta_artifact=delta_artifact,
                    digest=canonical_digest(relation),
                )
    return collected


def _provider_observation(
    row: object,
    *,
    campaign: ResearchCampaign,
    order: WorkOrder,
    project_id: str,
) -> dict[str, object]:
    metadata = row.get("metadata") if isinstance(row, dict) else None
    required_metadata = {
        "flywheel_run_id": str(campaign.pk),
        "flywheel_work_order_id": str(order.pk),
        "flywheel_work_order_proposal_digest": order.proposal_digest,
        "flywheel_role_instance": str(order.logical_role_id),
        "flywheel_role_contract": order.packet["required_reads"][0]["sha256"],
    }
    if (
        not isinstance(row, dict)
        or not isinstance(metadata, dict)
        or any(metadata.get(key) != value for key, value in required_metadata.items())
        or not isinstance(row.get("id"), str)
        or not re.fullmatch(r"[0-9a-f]{16}", row["id"])
        or not isinstance(row.get("traceId"), str)
        or not re.fullmatch(r"[0-9a-f]{32}", row["traceId"])
        or not isinstance(row.get("startTime"), str)
        or not isinstance(row.get("endTime"), str)
        or row.get("projectId") != project_id
        or (
            row.get("parentObservationId") is not None
            and (
                not isinstance(row["parentObservationId"], str)
                or not re.fullmatch(r"[0-9a-f]{16}", row["parentObservationId"])
            )
        )
        or not isinstance(row.get("type"), str)
        or not row["type"]
        or not isinstance(row.get("name"), str)
        or not row["name"]
        or not isinstance(row.get("level"), str)
        or not row["level"]
        or row["level"] == "ERROR"
        or row.get("sessionId") != str(campaign.pk)
        or (
            row["type"] == "GENERATION"
            and (
                not isinstance(row.get("providedModelName"), str)
                or not row["providedModelName"]
                or not isinstance(row.get("usageDetails"), dict)
            )
        )
    ):
        raise CampaignRejected(
            "Langfuse observation does not match exact work-order population"
        )
    return row


def _native_turn_identity(root: Mapping[str, object]) -> tuple[str, str]:
    metadata = root.get("metadata")
    if not isinstance(metadata, dict):
        raise CampaignRejected("Langfuse root lacks native Codex identity")
    sources = [
        item
        for item in (
            metadata.get("attributes"),
            metadata.get("resourceAttributes"),
            metadata,
        )
        if isinstance(item, dict)
    ]
    conversation_id = next(
        (
            item[key]
            for item in sources
            for key in ("thread.id", "conversation.id")
            if isinstance(item.get(key), str) and item[key]
        ),
        None,
    )
    turn_id = next(
        (
            item["turn.id"]
            for item in sources
            if isinstance(item.get("turn.id"), str) and item["turn.id"]
        ),
        None,
    )
    if (
        not isinstance(conversation_id, str)
        or not isinstance(turn_id, str)
        or len(conversation_id) > 160
        or len(turn_id) > 160
    ):
        raise CampaignRejected("Langfuse root lacks native Codex identity")
    return conversation_id, turn_id


def _primary_artifact(order: WorkOrder) -> Artifact:
    contract = order.packet.get("output_contract")
    primary_path = contract.get("primary_path") if isinstance(contract, dict) else None
    if not isinstance(primary_path, str):
        raise CampaignRejected("work-order primary artifact contract is invalid")
    artifacts = list(order.artifacts.filter(relative_path=primary_path))
    if len(artifacts) != 1:
        raise CampaignRejected("work order lacks one exact primary artifact")
    return artifacts[0]


def correlate_campaign(
    campaign: ResearchCampaign,
    user: object,
    connection: LangfuseConnection,
) -> list[TraceLink]:
    require_director(campaign, user)
    if campaign.trace_links.exists():
        raise CampaignRejected("campaign readback is final")
    try:
        expected = configured_langfuse_connection({
            "FLYWHEEL_LANGFUSE_AUTHORIZATION": connection.authorization,
        })
    except LangfuseRejected as exc:
        raise CampaignRejected(str(exc)) from exc
    if (
        connection.base_url != expected.base_url
        or connection.project_id != expected.project_id
    ):
        raise CampaignRejected(
            "Langfuse connection does not match the configured project"
        )
    readback_until = timezone.now()
    try:
        _verify_provider_project(connection)
        observations = readback_observations(
            connection=connection,
            session_id=str(campaign.pk),
            from_start_time=campaign.created_at,
            to_start_time=readback_until,
            page_limit=settings.LANGFUSE_READBACK_PAGE_LIMIT,
            max_pages=settings.LANGFUSE_READBACK_MAX_PAGES,
        )
    except LangfuseRejected as exc:
        raise CampaignRejected(str(exc)) from exc
    orders = list(
        campaign.work_orders.select_related("proposal").order_by("created_at")
    )
    if not orders:
        raise CampaignRejected("campaign has no exact work-order population")
    order_by_id = {str(order.pk): order for order in orders}
    grouped: dict[str, list[dict[str, object]]] = {
        str(order.pk): [] for order in orders
    }
    observation_ids: set[str] = set()
    for row in observations:
        metadata = row.get("metadata") if isinstance(row, dict) else None
        order_id = (
            metadata.get("flywheel_work_order_id")
            if isinstance(metadata, dict)
            else None
        )
        order = order_by_id.get(order_id) if isinstance(order_id, str) else None
        if order is None:
            raise CampaignRejected(
                "Langfuse work-order population contains missing or unknown identity"
            )
        provider = _provider_observation(
            row,
            campaign=campaign,
            order=order,
            project_id=connection.project_id,
        )
        if provider["id"] in observation_ids:
            raise CampaignRejected("Langfuse work-order population contains duplicates")
        observation_ids.add(provider["id"])
        grouped[order_id].append(provider)
    if any(not rows for rows in grouped.values()):
        raise CampaignRejected("Langfuse work-order population is incomplete")

    normalized: list[dict[str, object]] = []
    pending_links: list[dict[str, object]] = []
    for order in orders:
        _stored_attestation(order)
        if not _completion_observed(order):
            raise CampaignRejected("work-order completion is not observed")
        rows = grouped[str(order.pk)]
        trace_ids = {row["traceId"] for row in rows}
        if len(trace_ids) != 1:
            raise CampaignRejected("work-order population is not one native trace")
        row_ids = {row["id"] for row in rows}
        if any(
            row["parentObservationId"] is not None
            and row["parentObservationId"] not in row_ids
            for row in rows
        ):
            raise CampaignRejected("work-order observation parentage is incomplete")
        roots = [
            row
            for row in rows
            if row["parentObservationId"] is None
            and row["name"] == "session_task.turn"
        ]
        if len(roots) != 1:
            raise CampaignRejected("work order lacks one native Codex turn root")
        root = roots[0]
        conversation_id, turn_id = _native_turn_identity(root)
        artifact = _primary_artifact(order)
        pending_links.append(
            {
                "order": order,
                "artifact": artifact,
                "trace_id": root["traceId"],
                "observation_id": root["id"],
                "conversation_id": conversation_id,
                "call_id": turn_id,
            }
        )
        normalized.append(
            {
                "work_order_id": str(order.pk),
                "proposal_digest": order.proposal_digest,
                "trace_id": root["traceId"],
                "root_observation_id": root["id"],
                "conversation_id": conversation_id,
                "turn_id": turn_id,
                "observations": [
                    {
                        key: row.get(key)
                        for key in (
                            "id",
                            "traceId",
                            "parentObservationId",
                            "startTime",
                            "endTime",
                            "type",
                            "name",
                            "level",
                            "statusMessage",
                            "providedModelName",
                            "usageDetails",
                            "costDetails",
                        )
                    }
                    for row in sorted(rows, key=lambda item: str(item["id"]))
                ],
            }
        )

    links: list[TraceLink] = []
    with transaction.atomic():
        locked = ResearchCampaign.objects.select_for_update().get(pk=campaign.pk)
        if locked.trace_links.exists():
            raise CampaignRejected("campaign readback is final")
        event_id = uuid.uuid4()
        request = {
            "provider": "langfuse-cloud",
            "project_id": connection.project_id,
            "session_id": str(campaign.pk),
            "from_start_time": campaign.created_at.isoformat(),
            "to_start_time": readback_until.isoformat(),
        }
        response = {
            "schema_version": "campaign-provider-readback/v1",
            "work_orders": normalized,
        }
        event_payload = {
            "id": str(event_id),
            "campaign": str(campaign.pk),
            "work_order": None,
            "kind": RuntimeEvent.Kind.READBACK,
            "generation": 1,
            "request": request,
            "response": response,
            "succeeded": True,
        }
        RuntimeEvent.objects.create(
            id=event_id,
            campaign=locked,
            kind=RuntimeEvent.Kind.READBACK,
            request=request,
            response=response,
            succeeded=True,
            digest=canonical_digest(event_payload),
        )
        for item in pending_links:
            order = item["order"]
            artifact = item["artifact"]
            relation = {
                "campaign": str(campaign.pk),
                "work_order": str(order.pk),
                "artifact": artifact.pk,
                "artifact_digest": artifact.digest,
                **{
                    key: item[key]
                    for key in (
                        "trace_id",
                        "observation_id",
                        "conversation_id",
                        "call_id",
                    )
                },
            }
            links.append(
                TraceLink.objects.create(
                    campaign=locked,
                    work_order=order,
                    artifact=artifact,
                    trace_id=item["trace_id"],
                    observation_id=item["observation_id"],
                    conversation_id=item["conversation_id"],
                    call_id=item["call_id"],
                    digest=canonical_digest(relation),
                )
            )
    return links


def campaign_profile_state(campaign: ResearchCampaign) -> dict[str, object]:
    proposals = list(
        campaign.proposals.select_related(
            "disposition", "parent__disposition"
        ).order_by("created_at")
    )
    orders = list(
        campaign.work_orders.select_related("proposal", "run_spec").order_by(
            "created_at"
        )
    )
    transitions = list(
        campaign.state_transitions.select_related(
            "disposition",
            "work_order__proposal",
            "workbench_artifact",
            "state_artifact",
            "delta_artifact",
        ).order_by("created_at")
    )
    state_rows = [project_transition(item) for item in transitions]
    superseded_state_ids = {
        item.parent_id
        for item in transitions
        if item.parent_id
        and getattr(item, "disposition", None)
        and item.disposition.kind == ResearchStateDisposition.Kind.ACCEPTED
    }
    for row in state_rows:
        row["is_current_accepted"] = bool(
            row["state"] == ResearchStateDisposition.Kind.ACCEPTED
            and row["transition"].pk not in superseded_state_ids
        )
        row["display_state"] = (
            "accepted for continuation · history"
            if row["state"] == ResearchStateDisposition.Kind.ACCEPTED
            and row["transition"].pk in superseded_state_ids
            else (
                "accepted for continuation · current"
                if row["state"] == ResearchStateDisposition.Kind.ACCEPTED
                else row["state"]
            )
        )
    accepted_state_rows = [
        row
        for row in state_rows
        if row["state"] == ResearchStateDisposition.Kind.ACCEPTED
        and row["transition"].pk not in superseded_state_ids
    ]
    order_rows = []
    for order in orders:
        contract_error = None
        try:
            _validate_runtime_contract(order)
        except CampaignRejected as exc:
            contract_error = str(exc)
        events = list(order.runtime_events.order_by("created_at"))
        launch = next(
            (item for item in reversed(events) if item.kind == RuntimeEvent.Kind.LAUNCH),
            None,
        )
        send = next(
            (item for item in reversed(events) if item.kind == RuntimeEvent.Kind.SEND),
            None,
        )
        try:
            ready = bool(
                contract_error is None
                and launch is not None
                and launch.succeeded
                and send is None
                and _target_index(order) > 0
            )
        except CampaignRejected:
            ready = False
        order_rows.append(
            {
                "order": order,
                "launch": launch,
                "send": send,
                "ready": ready,
                "contract_error": contract_error,
                "completion_observed": _completion_observed(order),
                "has_artifacts": order.artifacts.exists(),
            }
        )
    planning_order_rows = [
        row for row in order_rows if row["order"].protocol == "planner"
    ]
    research_order_rows = [
        row for row in order_rows if row["order"].protocol != "planner"
    ]
    last_launch = campaign.runtime_events.filter(
        kind=RuntimeEvent.Kind.LAUNCH,
        succeeded=True,
    ).order_by("-created_at").first()
    last_stop = campaign.runtime_events.filter(
        kind=RuntimeEvent.Kind.STOP,
        succeeded=True,
    ).order_by("-created_at").first()
    proposal_rows = []
    for item in proposals:
        state_mode = (
            item.contract.get("research_state", {}).get("mode")
            if isinstance(item.contract.get("research_state"), dict)
            else None
        )
        available_state_rows = accepted_state_rows
        continuation_block = ""
        if state_mode == "continue":
            try:
                planner_input_state_id = _originating_planner_order(
                    item
                ).input_state_id
            except CampaignRejected:
                planner_input_state_id = None
            available_state_rows = [
                row
                for row in accepted_state_rows
                if row["transition"].pk == planner_input_state_id
            ]
            if not available_state_rows:
                continuation_block = (
                    STALE_PLANNER_INPUT_MESSAGE
                    if accepted_state_rows
                    else "This step requires an accepted research state first."
                )
        proposal_rows.append(
            {
                "proposal": item,
                "state": (
                    item.disposition.kind
                    if hasattr(item, "disposition")
                    else "awaiting director"
                ),
                "authored_by": item.get_author_display(),
                "state_mode": state_mode,
                "is_planner_interpretation": _is_planner_interpretation(item),
                "route_available": _planner_route_available(item),
                "available_state_rows": available_state_rows,
                "continuation_block": continuation_block,
            }
        )
    bound_order_row = next(
        (row for row in order_rows if row["order"].protocol == "bound_work"),
        None,
    )
    bound_acknowledgement = None
    bound_outcome = None
    bound_output_artifacts: dict[str, Artifact] = {}
    if bound_order_row and bound_order_row["has_artifacts"]:
        bound_output_artifacts = {
            item.relative_path: item
            for item in bound_order_row["order"].artifacts.filter(
                relative_path__in=("run-acknowledgement.json", "outcome.json")
            )
        }
        try:
            bound_acknowledgement = json.loads(
                bytes(bound_output_artifacts["run-acknowledgement.json"].content)
            )
            bound_outcome = json.loads(
                bytes(bound_output_artifacts["outcome.json"].content)
            )
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
            bound_acknowledgement = None
            bound_outcome = None
    return {
        "run_spec": getattr(campaign, "run_spec", None),
        "input_artifacts": campaign.input_artifacts.order_by("role", "created_at"),
        "bound_order_row": bound_order_row,
        "bound_acknowledgement": bound_acknowledgement,
        "bound_outcome": bound_outcome,
        "bound_outcome_artifact": bound_output_artifacts.get("outcome.json"),
        "bound_acknowledgement_artifact": bound_output_artifacts.get(
            "run-acknowledgement.json"
        ),
        "all_proposal_rows": proposal_rows,
        "proposal_rows": [
            row
            for row in proposal_rows
            if row["is_planner_interpretation"]
            or (
                row["proposal"].protocol != "planner"
                and row["route_available"]
            )
        ],
        "planning_proposal_rows": [
            row
            for row in proposal_rows
            if row["proposal"].protocol == "planner"
            and not row["is_planner_interpretation"]
        ],
        "planning_order_rows": planning_order_rows,
        "research_order_rows": research_order_rows,
        "runtime_active": bool(
            last_launch
            and (last_stop is None or last_launch.created_at > last_stop.created_at)
        ),
        "planning_results_collectable": any(
            row["completion_observed"] and not row["has_artifacts"]
            for row in planning_order_rows
        ),
        "research_results_collectable": any(
            row["completion_observed"] and not row["has_artifacts"]
            for row in research_order_rows
        ),
        "orders": orders,
        "order_rows": order_rows,
        "runtime_events": campaign.runtime_events.order_by("-created_at"),
        "runtime_history_exists": campaign.runtime_events.exists(),
        "artifacts": campaign.artifacts.select_related("work_order").order_by(
            "observed_at"
        ),
        "artifact_history_exists": campaign.artifacts.exists(),
        "trace_links": campaign.trace_links.select_related(
            "work_order", "artifact"
        ).order_by("created_at"),
        "planner_authorized": any(item.protocol == "planner" for item in orders),
        "state_rows": list(reversed(state_rows)),
        "accepted_state_rows": accepted_state_rows,
        "can_correlate": bool(
            orders
            and campaign.artifacts.filter(
                relative_path="artifact-attestation.json"
            ).count()
            == len(orders)
            and not campaign.trace_links.exists()
        ),
    }
