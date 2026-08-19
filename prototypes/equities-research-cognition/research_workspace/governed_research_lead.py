from __future__ import annotations

from dataclasses import dataclass

from .errors import AuthorityError, IntegrityError, ValidationError
from .research_lead import MaterialisedProposal, ResearchLead
from .util import require_string_list


@dataclass(frozen=True)
class ApprovedPlanBranch:
    proposal_id: str
    branch_id: str
    result_id: str | None


class GovernedResearchLead(ResearchLead):
    """Materialise plan proposals only from completed dependency state."""

    def _approved_plan_branches(self, artifact_id: str) -> dict[str, ApprovedPlanBranch]:
        result: dict[str, ApprovedPlanBranch] = {}
        for decision in self.workspace.store.list_objects("decision"):
            if decision.payload["target_id"] != artifact_id:
                continue
            if decision.payload["action"] != "approve_plan_proposal":
                continue
            grant = decision.payload.get("grant", {})
            proposal_id = grant.get("proposal_id")
            branch_id = grant.get("branch_id")
            if not isinstance(proposal_id, str) or not isinstance(branch_id, str):
                raise IntegrityError("plan-proposal decision lacks exact branch identity")
            state = self.workspace.branch_state(branch_id)
            result[proposal_id] = ApprovedPlanBranch(
                proposal_id=proposal_id,
                branch_id=branch_id,
                result_id=state.get("result_id"),
            )
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
            (item for item in plan["proposals"] if item["proposal_id"] == proposal_id),
            None,
        )
        if proposal is None:
            raise ValidationError("research plan does not contain this proposal")
        lead_branch_id = artifact.payload.get("metadata", {}).get("branch_id")
        if not isinstance(lead_branch_id, str):
            raise IntegrityError("research plan artifact lacks its lead branch")
        lead_branch = self.workspace._require_kind(lead_branch_id, "research_branch")
        commission = self.workspace._require_kind(
            lead_branch.payload["commission_id"],
            "commission",
        )
        if proposal["method_id"] not in commission.payload["method_ids"]:
            raise AuthorityError("plan proposal uses a method outside the commission")

        approved = self._approved_plan_branches(artifact_id)
        dependency_result_ids: list[str] = []
        dependency_branch_ids: list[str] = []
        for dependency_id in proposal["depends_on"]:
            dependency = approved.get(dependency_id)
            if dependency is None:
                raise AuthorityError(
                    f"research plan dependency remains unapproved: {dependency_id}"
                )
            if dependency.result_id is None:
                raise AuthorityError(
                    f"research plan dependency has not completed: {dependency_id}"
                )
            dependency_branch_ids.append(dependency.branch_id)
            dependency_result_ids.append(dependency.result_id)

        context_ids = require_string_list(context_ids, "proposal contexts")
        for context_id in context_ids:
            context = self.workspace._require_kind(context_id, "context")
            if context.payload["episode_id"] != plan["episode_id"]:
                raise ValidationError("proposal context crosses episode")
            if context.payload["commission_id"] != commission.id:
                raise ValidationError("proposal context uses another commission")
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

        branch = self.workspace.create_research_branch(
            episode_id=plan["episode_id"],
            commission_id=commission.id,
            method_id=proposal["method_id"],
            branch_kind=proposal["branch_kind"],
            title=proposal["title"],
            question=(
                proposal["question"]
                + (
                    " Stop when any of these conditions holds: "
                    + "; ".join(proposal["stop_conditions"])
                    if proposal["stop_conditions"]
                    else ""
                )
            ),
            context_ids=context_ids,
            expected_outputs=proposal["expected_outputs"],
            authority_ceiling=proposal["authority_ceiling"],
            created_by=actor,
            input_object_ids=[
                artifact_id,
                *proposal["input_object_ids"],
                *dependency_result_ids,
            ],
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
                "dependency_branch_ids": dependency_branch_ids,
                "dependency_result_ids": dependency_result_ids,
                "authority_ceiling": proposal["authority_ceiling"],
            },
        )
        self.workspace.store.put_relation(
            artifact_id,
            "materialised_as_branch",
            branch.id,
        )
        self.workspace.store.put_relation(decision.id, "authorised_branch", branch.id)
        for result_id in dependency_result_ids:
            self.workspace.store.put_relation(result_id, "feeds_branch", branch.id)
        return MaterialisedProposal(
            plan_artifact_id=artifact_id,
            proposal_id=proposal_id,
            branch_id=branch.id,
            decision_id=decision.id,
        )
