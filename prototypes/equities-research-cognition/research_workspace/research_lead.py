from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .errors import AuthorityError, IntegrityError, ValidationError
from .ntm_research import NtmControl
from .service import ResearchWorkspace
from .store import StoredObject
from .util import require_string_list, require_text


PLAN_BRANCH_KINDS = {"research", "challenge", "artifact", "rederivation"}
PLAN_CONTEXT_KINDS = {"discovery", "support"}


@dataclass(frozen=True)
class LeadLaunch:
    context_id: str
    branch_id: str
    binding_id: str
    instruction_id: str
    session: str
    pane: int


@dataclass(frozen=True)
class MaterialisedProposal:
    plan_artifact_id: str
    proposal_id: str
    branch_id: str
    decision_id: str


class ResearchLead:
    """Run and materialise a model-written research plan.

    The lead plan is a provisional artifact. The analyst approves individual
    proposals. The host verifies method, context kind, professional objects,
    dependencies, and authority before creating a persistent research branch.
    """

    def __init__(self, workspace: ResearchWorkspace) -> None:
        self.workspace = workspace

    @staticmethod
    def plan_contract() -> dict[str, Any]:
        return {
            "schema": "research-plan/v1",
            "summary": "ordinary-language account of the proposed research",
            "proposals": [
                {
                    "proposal_id": "stable id within this plan",
                    "title": "ordinary-language work title",
                    "question": "one professional question",
                    "branch_kind": "research | challenge | artifact | rederivation",
                    "context_kind": "discovery | support",
                    "method_id": "host-issued method id",
                    "professional_object_ids": ["host-issued ids"],
                    "evidence_needs": [],
                    "input_object_ids": [],
                    "expected_outputs": [],
                    "authority_ceiling": "provisional scope",
                    "depends_on": [],
                    "stop_conditions": [],
                    "rationale": "why this branch could change the answer",
                }
            ],
            "unresolved_questions": [],
        }

    def start(
        self,
        *,
        episode_id: str,
        commission_id: str,
        method_id: str,
        professional_object_ids: list[str],
        controller: NtmControl,
        codex_binary: Path,
        model: str,
        actor: str,
        session: str | None = None,
    ) -> LeadLaunch:
        episode = self.workspace._require_kind(episode_id, "episode")
        commission = self.workspace._require_kind(commission_id, "commission")
        if commission.payload["episode_id"] != episode_id:
            raise ValidationError("lead commission belongs to another episode")
        if method_id not in commission.payload["method_ids"]:
            raise AuthorityError("confirmed commission does not permit the lead method")
        professional_object_ids = require_string_list(
            professional_object_ids,
            "lead professional objects",
        )
        context = self.workspace.build_context(
            episode_id=episode_id,
            commission_id=commission_id,
            method_id=method_id,
            purpose="Propose the smallest research programme that could change the answer",
            assertion_ids=[],
            professional_object_ids=professional_object_ids,
            required_action="plan_research",
            allowed_tools=["source_request"],
            output_contract={
                "schema": "research-lead-output/v1",
                "artifact_kind": "research_plan",
                "artifact_path": "artifacts/research-plan.json",
                "contract": self.plan_contract(),
                "claims": False,
                "memory": False,
            },
        )
        question = (
            "Read the exact confirmed commission and prior perspective. Propose the "
            "smallest set of independently disposable research branches that could "
            "change the professional answer. Do not conduct the proposed research. "
            "Write one artifact at outbox/artifacts/research-plan.json using the "
            "research-plan/v1 contract in the context output contract. Return it as "
            "artifact kind research_plan. Produce no supported claim and no memory "
            "proposal. Preserve unresolved professional judgment."
        )
        branch = self.workspace.create_research_branch(
            episode_id=episode_id,
            commission_id=commission_id,
            method_id=method_id,
            branch_kind="lead",
            title="Propose the research programme",
            question=question,
            context_ids=[context.id],
            expected_outputs=["research_plan"],
            authority_ceiling="proposals_only",
            created_by=actor,
        )
        launch = self.workspace.launch_research_branch(
            branch_id=branch.id,
            controller=controller,
            codex_binary=codex_binary,
            model=model,
            role_name="research_lead",
            actor=actor,
            session=session,
        )
        return LeadLaunch(
            context_id=context.id,
            branch_id=branch.id,
            binding_id=launch.binding_id,
            instruction_id=launch.instruction_id,
            session=launch.session,
            pane=launch.pane,
        )

    def _read_plan(self, artifact_id: str) -> tuple[StoredObject, dict[str, Any]]:
        artifact = self.workspace._require_kind(artifact_id, "artifact")
        if artifact.payload["kind"] != "research_plan":
            raise ValidationError("artifact is not a research plan")
        blob = self.workspace.store.get_blob(artifact.payload["blob_digest"])
        try:
            value = json.loads(self.workspace.store.read_blob(blob.digest))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IntegrityError("research plan artifact is not valid UTF-8 JSON") from exc
        if not isinstance(value, dict) or value.get("schema") != "research-plan/v1":
            raise ValidationError("research plan has the wrong schema")
        return artifact, value

    def validate_plan(self, artifact_id: str) -> dict[str, Any]:
        artifact, plan = self._read_plan(artifact_id)
        episode = self.workspace._require_kind(artifact.payload["episode_id"], "episode")
        summary = require_text(plan.get("summary"), "research plan summary")
        proposals = plan.get("proposals")
        if not isinstance(proposals, list) or not proposals:
            raise ValidationError("research plan requires at least one proposal")
        unresolved = require_string_list(
            plan.get("unresolved_questions", []),
            "research plan unresolved questions",
            allow_empty=True,
        )
        normalised: list[dict[str, Any]] = []
        proposal_ids: set[str] = set()
        for raw in proposals:
            if not isinstance(raw, dict):
                raise ValidationError("research plan proposal must be an object")
            proposal_id = require_text(raw.get("proposal_id"), "plan proposal id")
            if proposal_id in proposal_ids:
                raise ValidationError("research plan proposal ids must be unique")
            proposal_ids.add(proposal_id)
            branch_kind = require_text(raw.get("branch_kind"), "plan branch kind")
            context_kind = require_text(raw.get("context_kind"), "plan context kind")
            if branch_kind not in PLAN_BRANCH_KINDS:
                raise ValidationError("research plan names an unsupported branch kind")
            if context_kind not in PLAN_CONTEXT_KINDS:
                raise ValidationError("research plan names an unsupported context kind")
            method_id = require_text(raw.get("method_id"), "plan method id")
            self.workspace._require_kind(method_id, "method")
            object_ids = require_string_list(
                raw.get("professional_object_ids", []),
                "plan professional objects",
            )
            for object_id in object_ids:
                item = self.workspace._require_kind(object_id, "professional_object")
                if item.payload["mandate_id"] != episode.payload["mandate_id"]:
                    raise ValidationError("plan professional object crosses mandate")
                if item.payload["authority"] not in {"human_confirmed", "policy"}:
                    raise AuthorityError(
                        "research plan may not rely on model-proposed professional meaning"
                    )
            depends_on = require_string_list(
                raw.get("depends_on", []),
                "plan dependencies",
                allow_empty=True,
            )
            input_ids = require_string_list(
                raw.get("input_object_ids", []),
                "plan input objects",
                allow_empty=True,
            )
            for input_id in input_ids:
                item = self.workspace.store.get_object(input_id)
                item_episode = item.payload.get("episode_id")
                if item_episode is not None and item_episode != episode.id:
                    raise ValidationError("plan input crosses episode")
            evidence_needs = raw.get("evidence_needs", [])
            if not isinstance(evidence_needs, list):
                raise ValidationError("plan evidence needs must be a list")
            normalised.append(
                {
                    "proposal_id": proposal_id,
                    "title": require_text(raw.get("title"), "plan proposal title"),
                    "question": require_text(raw.get("question"), "plan question"),
                    "branch_kind": branch_kind,
                    "context_kind": context_kind,
                    "method_id": method_id,
                    "professional_object_ids": object_ids,
                    "evidence_needs": evidence_needs,
                    "input_object_ids": input_ids,
                    "expected_outputs": require_string_list(
                        raw.get("expected_outputs", []),
                        "plan expected outputs",
                    ),
                    "authority_ceiling": require_text(
                        raw.get("authority_ceiling"),
                        "plan authority ceiling",
                    ),
                    "depends_on": depends_on,
                    "stop_conditions": require_string_list(
                        raw.get("stop_conditions", []),
                        "plan stop conditions",
                        allow_empty=True,
                    ),
                    "rationale": require_text(
                        raw.get("rationale"),
                        "plan rationale",
                    ),
                }
            )
        for proposal in normalised:
            unknown = set(proposal["depends_on"]) - proposal_ids
            if unknown:
                raise ValidationError(
                    "research plan dependency names an unknown proposal: "
                    + ", ".join(sorted(unknown))
                )
        self._require_acyclic(normalised)
        return {
            "schema": "research-plan/v1",
            "artifact_id": artifact.id,
            "episode_id": episode.id,
            "summary": summary,
            "proposals": normalised,
            "unresolved_questions": unresolved,
        }

    @staticmethod
    def _require_acyclic(proposals: list[dict[str, Any]]) -> None:
        graph = {
            proposal["proposal_id"]: set(proposal["depends_on"])
            for proposal in proposals
        }
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise ValidationError("research plan dependency graph is cyclic")
            if node in visited:
                return
            visiting.add(node)
            for dependency in graph[node]:
                visit(dependency)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node)

    def _approved_proposal_ids(self, artifact_id: str) -> set[str]:
        result: set[str] = set()
        for decision in self.workspace.store.list_objects("decision"):
            if decision.payload["target_id"] != artifact_id:
                continue
            if decision.payload["action"] != "approve_plan_proposal":
                continue
            proposal_id = decision.payload.get("grant", {}).get("proposal_id")
            if isinstance(proposal_id, str):
                result.add(proposal_id)
        return result

    def materialise_proposal(
        self,
        *,
        artifact_id: str,
        proposal_id: str,
        context_ids: list[str],
        actor: str,
    ) -> MaterialisedProposal:
        plan = self.validate_plan(artifact_id)
        artifact = self.workspace._require_kind(artifact_id, "artifact")
        proposal = next(
            (
                item
                for item in plan["proposals"]
                if item["proposal_id"] == proposal_id
            ),
            None,
        )
        if proposal is None:
            raise ValidationError("research plan does not contain this proposal")
        approved = self._approved_proposal_ids(artifact_id)
        missing = set(proposal["depends_on"]) - approved
        if missing:
            raise AuthorityError(
                "research plan dependencies remain unapproved: "
                + ", ".join(sorted(missing))
            )
        context_ids = require_string_list(context_ids, "proposal contexts")
        for context_id in context_ids:
            context = self.workspace._require_kind(context_id, "context")
            if context.payload["episode_id"] != plan["episode_id"]:
                raise ValidationError("proposal context crosses episode")
            if context.payload["method_id"] != proposal["method_id"]:
                raise ValidationError("proposal context uses another method")
            if context.payload.get("context_kind", "support") != proposal["context_kind"]:
                raise ValidationError("proposal context has the wrong authority kind")
            missing_objects = set(proposal["professional_object_ids"]) - set(
                context.payload["professional_object_ids"]
            )
            if missing_objects:
                raise ValidationError(
                    "proposal context omits professional objects: "
                    + ", ".join(sorted(missing_objects))
                )
        lead_branch_id = artifact.payload.get("metadata", {}).get("branch_id")
        if not isinstance(lead_branch_id, str):
            raise IntegrityError("research plan artifact lacks its lead branch")
        branch = self.workspace.create_research_branch(
            episode_id=plan["episode_id"],
            commission_id=self.workspace._require_kind(
                lead_branch_id,
                "research_branch",
            ).payload["commission_id"],
            method_id=proposal["method_id"],
            branch_kind=proposal["branch_kind"],
            title=proposal["title"],
            question=(
                proposal["question"]
                + " Stop when any of these conditions holds: "
                + "; ".join(proposal["stop_conditions"])
                if proposal["stop_conditions"]
                else proposal["question"]
            ),
            context_ids=context_ids,
            expected_outputs=proposal["expected_outputs"],
            authority_ceiling=proposal["authority_ceiling"],
            created_by=actor,
            input_object_ids=[artifact_id, *proposal["input_object_ids"]],
            parent_branch_id=lead_branch_id,
        )
        decision = self.workspace.record_decision(
            episode_id=plan["episode_id"],
            target_id=artifact_id,
            action="approve_plan_proposal",
            purpose=proposal["title"],
            actor=actor,
            grant={
                "proposal_id": proposal_id,
                "branch_id": branch.id,
                "context_ids": context_ids,
                "authority_ceiling": proposal["authority_ceiling"],
            },
        )
        self.workspace.store.put_relation(
            artifact_id,
            "materialised_as_branch",
            branch.id,
        )
        self.workspace.store.put_relation(
            decision.id,
            "authorised_branch",
            branch.id,
        )
        return MaterialisedProposal(
            plan_artifact_id=artifact_id,
            proposal_id=proposal_id,
            branch_id=branch.id,
            decision_id=decision.id,
        )
