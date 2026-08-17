from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from os import environ
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from harness.langfuse.transport import LangfuseRejected
from harness.ntm.adapter import ExecutionResult
from product.campaign.models import (
    Artifact,
    Proposal,
    ProposalDisposition,
    ResearchCampaign,
    ResearchStateDisposition,
    ResearchStateTransition,
    RuntimeEvent,
    WorkOrder,
    canonical_bytes,
    canonical_digest,
)
from product.campaign.services import (
    CampaignRejected,
    approve_proposal,
    create_campaign,
    record_proposal,
    request_planner_reentry,
    skill_catalog,
    workbench_catalog,
)
from scenarios.adversarial._tue2_runtime_support import tracked_send_response


JOURNAL_FIELDS = (
    "source_receipts",
    "observations",
    "reasoning_updates",
    "mechanism_updates",
    "uncertainty_updates",
    "claim_updates",
    "claim_ceiling_updates",
    "route_decisions",
    "decision_updates",
)


class MaterialResearchStateTests(TestCase):
    """MECHANICAL_REGRESSION_ONLY for the material state-custody edge."""

    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        settings = self.settings(CAMPAIGN_ROOT=self.temp.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.user = get_user_model().objects.create_user(
            "director", password="local-password"
        )
        self.client.force_login(self.user)

    def create_campaign(self) -> ResearchCampaign:
        campaign = create_campaign(
            director=self.user,
            title="Revenue surprise durability",
            issuer_or_security="Example Semiconductor",
            equities_decision_use=(
                "Decide whether the revenue surprise changes position sizing "
                "or only the next diligence question."
            ),
            evidence_cutoff="2026-05-31",
            question=(
                "Was the surprise durable demand, price or mix, channel "
                "timing, or a stale expectation surface?"
            ),
        )
        response = self.client.post(
            reverse("campaign_approve_planner_programme", args=[campaign.pk])
        )
        self.assertEqual(302, response.status_code)
        self.assertTrue(
            WorkOrder.objects.filter(campaign=campaign, protocol="planner").exists()
        )
        return campaign

    def research_contract(
        self,
        *,
        workbench_index: int,
        mode: str,
        claim_ceiling: str | None = None,
    ) -> dict[str, object]:
        research_frame = next(
            item
            for item in skill_catalog()
            if item["name"] == "research-frame-search-with-domain-mechanisms"
        )
        workbench = workbench_catalog()[workbench_index]
        selected_workbench = {
            key: workbench[key]
            for key in ("workbench_id", "version", "protocol_sha256")
        }
        return {
            "workbenches": [selected_workbench],
            "research_state": {"mode": mode},
            "decision_hinge": "Does the surprise change position sizing?",
            "claim_ceiling": claim_ceiling or (
                "Only the exact comparable-state result or refusal."
                if workbench_index == 0
                else "Only the exact driver identity or refusal."
            ),
            "reasoning_operators": [
                {
                    **research_frame,
                    "failure_tested": "proxy-to-target substitution",
                    "expected_epistemic_delta": (
                        "separate reported change from rival explanations"
                    ),
                    "kill_condition": (
                        "no claim, route, uncertainty, or refusal changes"
                    ),
                }
            ],
        }

    def proposal(
        self,
        campaign: ResearchCampaign,
        *,
        workbench_index: int,
        title: str,
        mode: str,
        claim_ceiling: str | None = None,
    ):
        return record_proposal(
            campaign=campaign,
            author="planner",
            protocol="research_worker",
            title=title,
            task=title,
            contract=self.research_contract(
                workbench_index=workbench_index,
                mode=mode,
                claim_ceiling=claim_ceiling,
            ),
        )

    def planner_proposals(
        self,
        order: WorkOrder,
        *rows: dict[str, object],
    ) -> list[Proposal]:
        plan_content = (
            "# Research programme\n\n"
            "Use the supplied research state to decide what should change next."
        ).encode()
        routes_content = b"".join(
            canonical_bytes(row) + b"\n" for row in rows
        )
        plan = Artifact.objects.create(
            campaign=order.campaign,
            work_order=order,
            kind="plan",
            relative_path="plan.md",
            version=1,
            media_type="text/markdown",
            content=plan_content,
            digest=sha256(plan_content).hexdigest(),
        )
        routes = Artifact.objects.create(
            campaign=order.campaign,
            work_order=order,
            kind="proposals",
            relative_path="proposals.jsonl",
            version=1,
            media_type="application/json",
            content=routes_content,
            digest=sha256(routes_content).hexdigest(),
        )
        attestation_content = canonical_bytes(
            {
                "schema_version": "work-order-artifact-attestation/v1",
                "campaign_id": str(order.campaign_id),
                "work_order_id": str(order.pk),
                "logical_role_id": str(order.logical_role_id),
                "artifacts": [
                    {
                        "relative_path": "plan.md",
                        "byte_length": len(plan_content),
                        "sha256": plan.digest,
                    },
                    {
                        "relative_path": "proposals.jsonl",
                        "byte_length": len(routes_content),
                        "sha256": routes.digest,
                    },
                ],
                "authority": "worker_candidate_attestation",
            }
        )
        Artifact.objects.create(
            campaign=order.campaign,
            work_order=order,
            kind="artifact-attestation",
            relative_path="artifact-attestation.json",
            version=1,
            media_type="application/json",
            content=attestation_content,
            digest=sha256(attestation_content).hexdigest(),
        )
        interpretation = record_proposal(
            campaign=order.campaign,
            author=Proposal.Author.PLANNER,
            protocol="planner",
            title="What I think you mean",
            task=plan_content.decode(),
            contract={
                "authority_limit": "planner_interpretation_only",
                "planning_work_order_id": str(order.pk),
                "plan_artifact": {
                    "artifact_id": plan.pk,
                    "sha256": plan.digest,
                },
                "routes_artifact": {
                    "artifact_id": routes.pk,
                    "sha256": routes.digest,
                },
            },
            _system_interpretation=True,
        )
        approve_proposal(interpretation, user=self.user)
        return [
            record_proposal(
                campaign=order.campaign,
                parent=interpretation,
                author=Proposal.Author.PLANNER,
                protocol=row["protocol"],
                title=row["title"],
                task=row["task"],
                contract=row["contract"],
            )
            for row in rows
        ]

    def grounded_proposal(
        self,
        campaign: ResearchCampaign,
        transition: ResearchStateTransition,
        *,
        workbench_index: int,
        title: str,
        claim_ceiling: str | None = None,
    ) -> Proposal:
        planner = request_planner_reentry(transition, self.user)
        return self.planner_proposals(
            planner,
            {
                "protocol": "research_worker",
                "title": title,
                "task": title,
                "contract": self.research_contract(
                    workbench_index=workbench_index,
                    mode="continue",
                    claim_ceiling=claim_ceiling,
                ),
            },
        )[0]

    def approve(self, campaign, proposal, transition=None) -> WorkOrder:
        data = (
            {"state_basis": "commission"}
            if transition is None
            else {
                "state_basis": "accepted_transition",
                "input_state": str(transition.pk),
            }
        )
        response = self.client.post(
            reverse("campaign_approve_proposal", args=[campaign.pk, proposal.pk]),
            data,
        )
        self.assertEqual(302, response.status_code, response.content)
        return WorkOrder.objects.get(proposal=proposal)

    def initial_state(self, order: WorkOrder) -> dict[str, object]:
        journal = {key: [] for key in JOURNAL_FIELDS}
        journal["source_receipts"] = [
            {
                "receipt_id": "issuer-q1-note",
                "source_name": "Issuer Q1 results",
                "source_kind": "issuer_filing",
                "source_origin": "issuer",
                "url_or_path": "https://example.test/q1-results",
                "locator": "Revenue note",
                "published_at": "2026-05-28",
                "as_of": "2026-05-28",
                "exact_passage": "Prior-period revenue was recast to 100.",
                "access_state": "searched-positive",
            },
            {
                "receipt_id": "channel-sellthrough-route",
                "source_name": "Public channel sell-through evidence",
                "source_kind": "bounded_search_route",
                "source_origin": "independent_channel",
                "url_or_path": "https://example.test/public-channel-search",
                "locator": "Search completed at the evidence cutoff",
                "published_at": None,
                "as_of": "2026-05-31",
                "exact_passage": "",
                "access_state": "searched-negative",
            }
        ]
        journal["observations"] = [
            {
                "observation_id": "reported-prior-fact",
                "statement": "The originally reported prior-period revenue was 95.",
                "authority": "observed_source_claim",
                "source_receipt_ids": ["issuer-q1-note"],
                "payload": {"metric": "revenue", "value": "95", "unit": "USDm"},
            },
            {
                "observation_id": "issuer-recast-assertion",
                "statement": "The issuer asserted a comparable prior value of 100.",
                "authority": "issuer_assertion",
                "source_receipt_ids": ["issuer-q1-note"],
                "payload": {"from": "95", "to": "100", "basis": "issuer_recast"},
            },
            {
                "observation_id": "zero-residual-bridge",
                "statement": "The disclosed recast bridge ties with zero residual.",
                "authority": "deterministic_calculation",
                "source_receipt_ids": ["issuer-q1-note"],
                "payload": {"reported": "95", "adjustments": "5", "recast": "100"},
            },
            {
                "observation_id": "derived-prior-observation",
                "statement": "The comparable prior-period revenue candidate is 100.",
                "authority": "derived_candidate",
                "source_receipt_ids": ["issuer-q1-note"],
                "payload": {
                    "derived_from": [
                        "reported-prior-fact",
                        "issuer-recast-assertion",
                        "zero-residual-bridge",
                    ],
                    "value": "100",
                },
            },
        ]
        journal["reasoning_updates"] = [
            {
                "operator": "research-frame-search-with-domain-mechanisms",
                "failure_tested": "proxy-to-target substitution",
                "realized_delta": "kept four rival explanations live",
                "kill_result": "retain",
            }
        ]
        journal["mechanism_updates"] = [
            {
                "mechanism_id": "durable-demand",
                "label": "Durable unit demand",
                "from_status": "unassessed",
                "to_status": "live",
                "because_observation_ids": ["derived-prior-observation"],
                "missing_discriminator": "sell-through and backlog conversion",
            },
            {
                "mechanism_id": "price-mix",
                "label": "Price or mix",
                "from_status": "unassessed",
                "to_status": "live",
                "because_observation_ids": ["derived-prior-observation"],
                "missing_discriminator": "unit and average-revenue bridge",
            },
        ]
        journal["uncertainty_updates"] = [
            {
                "uncertainty_id": "surprise-mechanism",
                "question": "Which mechanism explains the comparable revenue change?",
                "from_status": "unassessed",
                "to_status": "open",
                "because_observation_ids": ["derived-prior-observation"],
                "next_discriminator": "decompose comparable revenue into drivers",
            }
        ]
        journal["claim_updates"] = [
            {
                "claim_id": "durable-demand-claim",
                "text": "The revenue surprise reflects durable demand.",
                "from_status": "unassessed",
                "to_status": "withheld",
                "because_observation_ids": ["derived-prior-observation"],
                "allowed_language": "Comparable revenue increased.",
                "forbidden_language": "Demand is durable.",
            }
        ]
        journal["route_decisions"] = [
            {
                "route_id": "driver-decomposition",
                "transition": "continue",
                "target_uncertainty_id": "surprise-mechanism",
                "rationale": "Comparable facts now permit driver decomposition.",
                "next_step": "Separate units, price/mix, interaction and residual.",
                "kill_condition": "Comparable-state authority is lost.",
            }
        ]
        journal["decision_updates"] = [
            {
                "changed": False,
                "consequence": "Do not change position sizing yet.",
                "no_action_condition": "Driver and expectation routes remain unresolved.",
                "authority_required": "research_director",
            }
        ]
        return {
            "schema_version": "investor-research-state/v1",
            "campaign_id": str(order.campaign_id),
            "work_order_id": str(order.pk),
            "parent_state_sha256": None,
            "decision_hinge": "Does the surprise change position sizing?",
            "work_order_claim_ceiling": order.proposal.contract["claim_ceiling"],
            "evidence_cutoff": "2026-05-31",
            "produced_by": order.proposal.contract["workbenches"][0],
            "journal": journal,
        }

    def successor_state(
        self, order: WorkOrder, parent: ResearchStateTransition
    ) -> dict[str, object]:
        state = json.loads(bytes(parent.state_artifact.content))
        state.update(
            {
                "work_order_id": str(order.pk),
                "parent_state_sha256": parent.state_artifact.digest,
                "work_order_claim_ceiling": order.proposal.contract["claim_ceiling"],
                "produced_by": order.proposal.contract["workbenches"][0],
            }
        )
        state["journal"]["source_receipts"].append(
            {
                "receipt_id": "issuer-q1-drivers",
                "source_name": "Issuer Q1 operating data",
                "source_kind": "issuer_filing",
                "source_origin": "issuer",
                "url_or_path": "https://example.test/q1-drivers",
                "locator": "Revenue bridge",
                "published_at": "2026-05-28",
                "as_of": "2026-05-28",
                "exact_passage": "Units rose 5%; price and mix added 4%.",
                "access_state": "searched-positive",
            }
        )
        state["journal"]["observations"].append(
            {
                "observation_id": "driver-identity",
                "statement": (
                    "The exact driver identity ties against the issuer-recast "
                    "comparable base without licensing demand."
                ),
                "authority": "deterministic_calculation",
                "source_receipt_ids": ["issuer-q1-note", "issuer-q1-drivers"],
                "payload": {
                    "prior_observation": "derived-prior-observation",
                    "unit_effect": "5",
                    "price_mix": "4",
                    "interaction": "1",
                    "residual": "0",
                },
            }
        )
        state["journal"]["reasoning_updates"].append(
            {
                "operator": "research-frame-search-with-domain-mechanisms",
                "failure_tested": "proxy-to-target substitution",
                "realized_delta": "kept driver attribution below demand truth",
                "kill_result": "retain",
            }
        )
        state["journal"]["mechanism_updates"].append(
            {
                "mechanism_id": "price-mix",
                "label": "Price or mix",
                "from_status": "live",
                "to_status": "strengthened",
                "because_observation_ids": ["driver-identity"],
                "missing_discriminator": "mix versus realized price",
            }
        )
        state["journal"]["uncertainty_updates"].append(
            {
                "uncertainty_id": "surprise-mechanism",
                "question": "Which mechanism explains the comparable revenue change?",
                "from_status": "open",
                "to_status": "open",
                "because_observation_ids": ["driver-identity"],
                "next_discriminator": "compare with cutoff-time expectation surfaces",
            }
        )
        state["journal"]["claim_updates"].append(
            {
                "claim_id": "durable-demand-claim",
                "text": "The revenue surprise reflects durable demand.",
                "from_status": "withheld",
                "to_status": "withheld",
                "because_observation_ids": ["driver-identity"],
                "allowed_language": "The exact arithmetic identity ties.",
                "forbidden_language": "Unit growth proves durable demand.",
            }
        )
        state["journal"]["route_decisions"].append(
            {
                "route_id": "expectation-reconstruction",
                "transition": "continue",
                "target_uncertainty_id": "surprise-mechanism",
                "rationale": "The driver identity does not explain surprise.",
                "next_step": "Reconstruct guidance and consensus at the cutoff.",
                "kill_condition": "No lawful timestamped expectation route exists.",
            }
        )
        state["journal"]["decision_updates"].append(
            {
                "changed": False,
                "consequence": "Keep position sizing unchanged pending expectations.",
                "no_action_condition": "Demand durability remains unlicensed.",
                "authority_required": "research_director",
            }
        )
        return state

    def write_transition(
        self,
        order: WorkOrder,
        state: dict[str, object],
        parent: ResearchStateTransition | None = None,
        *,
        include_workbench_result: bool = True,
    ) -> None:
        workbench_id = order.proposal.contract["workbenches"][0]["workbench_id"]
        state["journal"]["claim_ceiling_updates"].append(
            {
                "work_order_id": str(order.pk),
                "workbench": order.proposal.contract["workbenches"][0],
                "claim_ceiling": order.proposal.contract["claim_ceiling"],
            }
        )
        if workbench_id == "equities/comparable-state-reconstruction/v0":
            workbench_result = {
                "schema_version": "research-state-patch/v0",
                "workbench": order.proposal.contract["workbenches"][0],
                "status": "COMPARABLE",
                "claim_ceiling": order.proposal.contract["claim_ceiling"],
                "source_receipt_ids": ["issuer-q1-note"],
                "observation_ids": [
                    "reported-prior-fact",
                    "issuer-recast-assertion",
                    "zero-residual-bridge",
                    "derived-prior-observation",
                ],
                "comparable_fact_set": {
                    "authority": "issuer_recast",
                    "original_fact_observation_id": "reported-prior-fact",
                    "issuer_assertion_observation_id": "issuer-recast-assertion",
                    "bridge_observation_id": "zero-residual-bridge",
                    "derived_observation_id": "derived-prior-observation",
                    "residual": "0",
                },
                "refusal": None,
            }
        elif workbench_id == "equities/aggregate-driver-attribution/v0":
            upstream = parent.work_order.artifacts.get(
                relative_path="workbench-result.json"
            )
            workbench_result = {
                "schema_version": "driver-state-patch/v0",
                "workbench": order.proposal.contract["workbenches"][0],
                "status": "IDENTITY_TIED",
                "claim_ceiling": order.proposal.contract["claim_ceiling"],
                "source_receipt_ids": [
                    "issuer-q1-note",
                    "issuer-q1-drivers",
                ],
                "observation_ids": [
                    "reported-prior-fact",
                    "issuer-recast-assertion",
                    "zero-residual-bridge",
                    "derived-prior-observation",
                    "driver-identity",
                ],
                "upstream": {
                    "state_sha256": parent.state_artifact.digest,
                    "workbench_result_sha256": upstream.digest,
                    "status": "COMPARABLE",
                    "original_fact_observation_id": "reported-prior-fact",
                    "issuer_assertion_observation_id": "issuer-recast-assertion",
                    "bridge_observation_id": "zero-residual-bridge",
                    "derived_observation_id": "derived-prior-observation",
                },
                "identity": {
                    "method": "two_factor_pvm",
                    "unit_volume": "5",
                    "price_mix": "4",
                    "interaction": "1",
                    "residual": "0",
                },
                "refusal": None,
            }
        else:
            raise AssertionError("fixture lacks an exact workbench result")
        workbench_bytes = canonical_bytes(workbench_result)
        if include_workbench_result:
            state["workbench_result_sha256"] = sha256(workbench_bytes).hexdigest()
        parent_journal = (
            json.loads(bytes(parent.state_artifact.content))["journal"]
            if parent
            else {key: [] for key in JOURNAL_FIELDS}
        )
        appended = {
            key: state["journal"][key][len(parent_journal[key]) :]
            for key in JOURNAL_FIELDS
        }
        state_bytes = json.dumps(state, indent=2).encode()
        delta = {
            "schema_version": "epistemic-delta/v1",
            "campaign_id": str(order.campaign_id),
            "work_order_id": str(order.pk),
            "parent_state_sha256": (
                parent.state_artifact.digest if parent else None
            ),
            "after_state_sha256": sha256(state_bytes).hexdigest(),
            "summary": appended["decision_updates"][-1]["consequence"],
            "appended": appended,
        }
        root = Path(order.campaign.artifact_root) / "work" / str(order.pk) / "out"
        root.mkdir(parents=True, exist_ok=True)
        if include_workbench_result:
            (root / "workbench-result.json").write_bytes(workbench_bytes)
        (root / "research-state.json").write_bytes(state_bytes)
        (root / "epistemic-delta.json").write_bytes(canonical_bytes(delta))
        (root / "branch.md").write_text(
            "# Research result\n\nThe exact state and delta are canonical artifacts.\n"
        )
        self.write_attestation(order)

    def write_attestation(
        self,
        order: WorkOrder,
        *,
        extra: dict[str, object] | None = None,
    ) -> None:
        root = Path(order.campaign.artifact_root) / "work" / str(order.pk) / "out"
        rows = []
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.name == "artifact-attestation.json":
                continue
            content = path.read_bytes()
            rows.append(
                {
                    "relative_path": path.relative_to(root).as_posix(),
                    "byte_length": len(content),
                    "sha256": sha256(content).hexdigest(),
                }
            )
        attestation = {
            "schema_version": "work-order-artifact-attestation/v1",
            "campaign_id": str(order.campaign_id),
            "work_order_id": str(order.pk),
            "logical_role_id": str(order.logical_role_id),
            "artifacts": rows,
            "authority": "worker_candidate_attestation",
            **(extra or {}),
        }
        (root / "artifact-attestation.json").write_bytes(
            canonical_bytes(attestation)
        )

    def collect(self, campaign: ResearchCampaign, expected: int = 302):
        for order in campaign.work_orders.order_by("created_at"):
            output = (
                Path(campaign.artifact_root)
                / "work"
                / str(order.pk)
                / "out"
            )
            if output.is_dir() and not order.artifacts.exists():
                self.write_attestation(order)
                self.mark_mechanical_completion(order)
        response = self.client.post(reverse("campaign_collect", args=[campaign.pk]))
        self.assertEqual(expected, response.status_code, response.content)
        return response

    def mark_mechanical_completion(
        self, order: WorkOrder, *, completion_pane: str = "2"
    ) -> None:
        if order.runtime_events.filter(
            kind=RuntimeEvent.Kind.STATUS,
            succeeded=True,
            response__condition="complete",
        ).exists():
            return
        if not order.runtime_events.filter(
            kind=RuntimeEvent.Kind.SEND, succeeded=True
        ).exists():
            event_id = uuid.uuid4()
            send_payload = {
                "id": str(event_id),
                "campaign": str(order.campaign_id),
                "work_order": str(order.pk),
                "kind": RuntimeEvent.Kind.SEND,
                "generation": 1,
                "request": {
                    "argv": ["mechanical-test-only-send", "--panes=2"]
                },
                "response": tracked_send_response(order),
                "succeeded": True,
            }
            RuntimeEvent.objects.create(
                id=event_id,
                campaign=order.campaign,
                work_order=order,
                kind=RuntimeEvent.Kind.SEND,
                request=send_payload["request"],
                response=send_payload["response"],
                succeeded=True,
                digest=canonical_digest(send_payload),
            )
        event_id = uuid.uuid4()
        completion_payload = {
            "id": str(event_id),
            "campaign": str(order.campaign_id),
            "work_order": str(order.pk),
            "kind": RuntimeEvent.Kind.STATUS,
            "generation": 1,
            "request": {
                "argv": [
                    "mechanical-test-only-completion",
                    f"--panes={completion_pane}",
                ]
            },
            "response": {
                "success": True,
                "session": order.campaign.ntm_session,
                "condition": "complete",
                "agents": [
                    {
                        "pane": "%opaque-provider-pane",
                        "state": "WAITING",
                        "agent_type": "codex",
                    }
                ],
            },
            "succeeded": True,
        }
        RuntimeEvent.objects.create(
            id=event_id,
            campaign=order.campaign,
            work_order=order,
            kind=RuntimeEvent.Kind.STATUS,
            request=completion_payload["request"],
            response=completion_payload["response"],
            succeeded=True,
            digest=canonical_digest(completion_payload),
        )

    def test_ordinary_collection_waits_for_exact_runtime_completion(self) -> None:
        class ControlledNtm:
            message_path: Path | None = None

            def spawn_command(self, *args):
                return ["controlled-launch"]

            def status_command(self, *args):
                return ["controlled-status"]

            def send_command(self, session, index, message, config):
                self.message_path = message
                return ["controlled-send", f"--panes={index}"]

            def completion_command(self, session, index, config):
                return ["controlled-completion", f"--panes={index}"]

            def execute(self, argv, *, environment):
                if argv == ["controlled-launch"]:
                    response = {
                        "success": True,
                        "session": campaign.ntm_session,
                        "agents": [{"title": "researcher"}],
                    }
                elif argv == ["controlled-status"]:
                    response = {
                        "generated_at": "2026-08-04T17:00:00Z",
                        "session": campaign.ntm_session,
                        "exists": True,
                        # Real NTM 1.14 may omit a process-level working
                        # directory while still returning a valid session
                        # status population.
                        "working_directory": "",
                        "panes": [
                            {
                                "title": "researcher",
                                "type": "codex",
                                "command": "codex",
                                "context_model": "gpt-5.6-sol",
                                "index": 2,
                            }
                        ],
                        "agent_counts": {"codex": 1},
                    }
                elif argv[:1] == ["controlled-send"]:
                    response = tracked_send_response(order)
                else:
                    response = {
                        "success": True,
                        "session": campaign.ntm_session,
                        "condition": "complete",
                        "agents": [
                            {
                                "pane": "%opaque-provider-pane",
                                "state": "WAITING",
                                "agent_type": "codex",
                            }
                        ],
                    }
                return ExecutionResult(
                    exit_code=0,
                    stdout=canonical_bytes(response),
                    stderr=b"",
                    response=response,
                )

        campaign = create_campaign(
            director=self.user,
            title="Material worker custody",
            issuer_or_security="Example Semiconductor",
            equities_decision_use="Decide whether deeper underwriting is warranted.",
            evidence_cutoff="2026-05-31",
            question="Which mechanism changes the decision?",
        )
        order = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        control = ControlledNtm()
        target = {
            "FLYWHEEL_LANGFUSE_AUTHORIZATION": "Basic cGstbGYteDpzay1sZi14",
        }
        with (
            self.settings(
                CAMPAIGN_CODEX_BINARY="/usr/bin/true",
                CAMPAIGN_CODEX_MODEL="gpt-5.6-sol",
                LANGFUSE_TARGET_BASE_URL="https://cloud.langfuse.com",
                LANGFUSE_TARGET_PROJECT_ID="project-1",
            ),
            patch("product.campaign.services.adapter", return_value=control),
            patch.dict(environ, target, clear=False),
            patch("product.campaign.services.readback_project_identity"),
        ):
            self.assertEqual(
                302,
                self.client.post(
                    reverse("campaign_launch", args=[campaign.pk, order.pk])
                ).status_code,
            )
            output_root = Path(order.packet["output_contract"]["output_root"])
            self.assertTrue(output_root.is_dir())
            launcher = next(
                (Path(campaign.artifact_root) / "_control").glob("codex-*.sh")
            ).read_text()
            self.assertIn("--sandbox workspace-write", launcher)
            self.assertIn(f"--cd {output_root}", launcher)
            self.assertNotIn("--add-dir", launcher)
            self.assertNotIn("--sandbox read-only", launcher)
            self.assertEqual(
                302,
                self.client.post(
                    reverse("campaign_refresh", args=[campaign.pk, order.pk])
                ).status_code,
            )
            self.assertEqual(
                302,
                self.client.post(
                    reverse("campaign_send", args=[campaign.pk, order.pk])
                ).status_code,
            )
            packet = json.loads(control.message_path.read_bytes())
            output_root = Path(packet["output_contract"]["output_root"])
            self.assertEqual(
                Path(campaign.artifact_root) / "work" / str(order.pk) / "out",
                output_root,
            )
            self.assertTrue(output_root.is_dir())

            self.write_transition(order, self.initial_state(order))
            premature = self.client.post(
                reverse("campaign_collect", args=[campaign.pk])
            )
            self.assertEqual(409, premature.status_code, premature.content)
            self.assertIn(b"completion", premature.content)

            self.assertEqual(
                302,
                self.client.post(
                    reverse("campaign_refresh", args=[campaign.pk, order.pk])
                ).status_code,
            )
            self.assertEqual(
                302,
                self.client.post(
                    reverse("campaign_collect", args=[campaign.pk])
                ).status_code,
            )

        self.assertFalse(output_root.exists())
        self.assertTrue((output_root.parent / "sealed").is_dir())
        self.assertEqual(
            {
                "artifact-attestation.json",
                "branch.md",
                "epistemic-delta.json",
                "research-state.json",
                "workbench-result.json",
            },
            set(order.artifacts.values_list("relative_path", flat=True)),
        )

    def test_collection_rejects_a_nested_mutable_output_population(self) -> None:
        campaign = self.create_campaign()
        order = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(order, self.initial_state(order))
        root = Path(order.packet["output_contract"]["output_root"])
        nested = root / "mutable"
        nested.mkdir()
        (nested / "late.txt").write_text("not part of the flat exact contract")
        self.write_attestation(order)
        self.mark_mechanical_completion(order)

        response = self.client.post(
            reverse("campaign_collect", args=[campaign.pk])
        )

        self.assertEqual(409, response.status_code, response.content)
        self.assertIn(b"regular files", response.content)

    def test_worker_attestation_rejects_provider_identity(self) -> None:
        campaign = self.create_campaign()
        order = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(order, self.initial_state(order))
        self.write_attestation(order, extra={"observation_id": "fabricated"})
        event_id = uuid.uuid4()
        send_payload = {
            "id": str(event_id),
            "campaign": str(campaign.pk),
            "work_order": str(order.pk),
            "kind": RuntimeEvent.Kind.SEND,
            "generation": 1,
            "request": {"argv": ["mechanical-test-send", "--panes=2"]},
            "response": tracked_send_response(order),
            "succeeded": True,
        }
        send = RuntimeEvent.objects.create(
            id=event_id,
            campaign=campaign,
            work_order=order,
            kind=RuntimeEvent.Kind.SEND,
            request=send_payload["request"],
            response=send_payload["response"],
            succeeded=True,
            digest=canonical_digest(send_payload),
        )
        event_id = uuid.uuid4()
        completion_payload = {
            "id": str(event_id),
            "campaign": str(campaign.pk),
            "work_order": str(order.pk),
            "kind": RuntimeEvent.Kind.STATUS,
            "generation": 1,
            "request": {
                "argv": ["mechanical-test-completion", "--panes=2"]
            },
            "response": {
                "success": True,
                "session": campaign.ntm_session,
                "condition": "complete",
                "agents": [
                    {
                        "pane": "%opaque-provider-pane",
                        "state": "WAITING",
                        "agent_type": "codex",
                    }
                ],
            },
            "succeeded": True,
        }
        RuntimeEvent.objects.create(
            id=event_id,
            campaign=campaign,
            work_order=order,
            kind=RuntimeEvent.Kind.STATUS,
            request=completion_payload["request"],
            response=completion_payload["response"],
            succeeded=True,
            digest=canonical_digest(completion_payload),
            created_at=send.created_at,
        )

        response = self.client.post(
            reverse("campaign_collect", args=[campaign.pk])
        )

        self.assertEqual(409, response.status_code, response.content)
        self.assertIn(b"artifact attestation", response.content)

    def test_sent_worker_receives_exact_state_and_cognition_inputs(self) -> None:
        class ControlledNtm:
            message_path: Path | None = None
            launch_environment: dict[str, str] | None = None
            calls = 0

            def spawn_command(self, *args):
                return ["controlled-launch"]

            def status_command(self, *args):
                return ["controlled-status"]

            def send_command(self, session, index, message, config):
                self.message_path = message
                return ["controlled-send", f"--panes={index}"]

            def execute(self, argv, *, environment):
                self.calls += 1
                if argv == ["controlled-launch"]:
                    self.launch_environment = dict(environment)
                    response = {
                        "success": True,
                        "session": campaign.ntm_session,
                        "agents": [{"title": "researcher"}],
                    }
                elif argv == ["controlled-status"]:
                    response = {
                        "generated_at": "2026-08-04T17:00:00Z",
                        "session": campaign.ntm_session,
                        "exists": True,
                        "working_directory": str(Path(campaign.artifact_root)),
                        "panes": [
                            {
                                "title": "researcher",
                                "type": "codex",
                                "command": "codex",
                                "context_model": "gpt-5.6-sol",
                                "index": 2,
                            }
                        ],
                        "agent_counts": {"codex": 1},
                    }
                else:
                    response = tracked_send_response(w2)
                return ExecutionResult(
                    exit_code=0,
                    stdout=canonical_bytes(response),
                    stderr=b"",
                    response=response,
                )

        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(reverse("campaign_accept_state", args=[campaign.pk, first.pk]))
        w2 = self.approve(
            campaign,
            self.grounded_proposal(
                campaign,
                first,
                workbench_index=1,
                title="Decompose the comparable revenue change",
            ),
            transition=first,
        )
        control = ControlledNtm()
        runtime = self.settings(
            CAMPAIGN_CODEX_BINARY="/usr/bin/true",
            CAMPAIGN_CODEX_MODEL="gpt-5.6-sol",
            LANGFUSE_TARGET_BASE_URL="https://cloud.langfuse.com",
            LANGFUSE_TARGET_PROJECT_ID="project-1",
        )
        target = {
            "FLYWHEEL_LANGFUSE_AUTHORIZATION": "Basic cGstbGYteDpzay1sZi14",
        }
        with (
            runtime,
            patch("product.campaign.services.adapter", return_value=control),
        ):
            with (
                patch.dict(environ, target, clear=False),
                patch(
                    "product.campaign.services.readback_project_identity",
                    side_effect=LangfuseRejected(
                        "Langfuse key is not bound to the configured project"
                    ),
                ),
            ):
                mismatch = self.client.post(
                    reverse("campaign_launch", args=[campaign.pk, w2.pk])
                )
                self.assertEqual(409, mismatch.status_code, mismatch.content)
                self.assertIn(b"configured project", mismatch.content)
                self.assertEqual(0, control.calls)
                self.assertFalse(
                    (Path(campaign.artifact_root) / "_control").exists()
                )
            with (
                patch.dict(environ, target, clear=False),
                patch(
                    "product.campaign.services.readback_project_identity"
                ) as project_readback,
            ):
                response = self.client.post(
                    reverse("campaign_launch", args=[campaign.pk, w2.pk])
                )
                self.assertEqual(302, response.status_code, response.content)
                project_readback.assert_called_once()
                self.assertEqual(
                    302,
                    self.client.post(
                        reverse("campaign_refresh", args=[campaign.pk, w2.pk])
                    ).status_code,
                )
                self.assertEqual(
                    302,
                    self.client.post(
                        reverse("campaign_send", args=[campaign.pk, w2.pk])
                    ).status_code,
                )
                project_readback.assert_called_once()

        self.assertIsNotNone(control.message_path)
        self.assertIsNotNone(control.launch_environment)
        self.assertEqual(
            (
                "Authorization=Basic cGstbGYteDpzay1sZi14,"
                "x-langfuse-ingestion-version=4"
            ),
            control.launch_environment["OTEL_EXPORTER_OTLP_TRACES_HEADERS"],
        )
        packet = json.loads(control.message_path.read_bytes())
        state_input = packet["research_state_input"]
        workbench_path = Path(state_input["workbench_result_materialized_path"])
        state_path = Path(state_input["state_materialized_path"])
        delta_path = Path(state_input["delta_materialized_path"])
        w1_result = first.work_order.artifacts.get(
            relative_path="workbench-result.json"
        )
        self.assertEqual(bytes(w1_result.content), workbench_path.read_bytes())
        self.assertEqual(
            w1_result.digest,
            sha256(workbench_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(bytes(first.state_artifact.content), state_path.read_bytes())
        self.assertEqual(bytes(first.delta_artifact.content), delta_path.read_bytes())
        self.assertEqual(first.state_artifact.digest, sha256(state_path.read_bytes()).hexdigest())
        read_kinds = {item["kind"] for item in packet["required_reads"]}
        self.assertEqual(
            {"role_protocol", "workbench_protocol", "reasoning_skill"},
            read_kinds,
        )
        for item in packet["required_reads"]:
            path = Path(item["path"])
            self.assertTrue(path.is_file())
            self.assertEqual(item["sha256"], sha256(path.read_bytes()).hexdigest())

    def test_current_evidence_requires_planner_reentry_before_continuation(
        self,
    ) -> None:
        campaign = self.create_campaign()
        initial_planner = campaign.work_orders.get(protocol="planner")
        root, stale = self.planner_proposals(
            initial_planner,
            {
                "protocol": "research_worker",
                "title": "Reconstruct a comparable revenue state",
                "task": "Reconstruct a comparable revenue state",
                "contract": self.research_contract(
                    workbench_index=0,
                    mode="root",
                ),
            },
            {
                "protocol": "research_worker",
                "title": "Continue the commission-grounded programme",
                "task": "Continue the commission-grounded programme",
                "contract": self.research_contract(
                    workbench_index=1,
                    mode="continue",
                ),
            },
        )
        w1 = self.approve(campaign, root)
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, first.pk])
        )

        response = self.client.post(
            reverse("campaign_approve_proposal", args=[campaign.pk, stale.pk]),
            {
                "state_basis": "accepted_transition",
                "input_state": str(first.pk),
            },
        )
        self.assertEqual(409, response.status_code, response.content)
        self.assertContains(
            response,
            (
                "This proposal was planned before the current evidence was "
                "accepted. Re-plan from current evidence before approving "
                "follow-on research."
            ),
            status_code=409,
        )
        self.assertFalse(WorkOrder.objects.filter(proposal=stale).exists())
        self.assertFalse(
            ProposalDisposition.objects.filter(proposal=stale).exists()
        )

        page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(page, "Re-plan from current evidence")
        self.assertContains(
            page,
            (
                "This proposal was planned before the current evidence was "
                "accepted. Re-plan from current evidence before approving "
                "follow-on research."
            ),
        )
        proposal_count = campaign.proposals.count()
        order_count = campaign.work_orders.count()
        response = self.client.get(
            reverse(
                "campaign_replan_state",
                args=[campaign.pk, first.pk],
            )
        )
        self.assertEqual(405, response.status_code, response.content)
        self.assertEqual(proposal_count, campaign.proposals.count())
        self.assertEqual(order_count, campaign.work_orders.count())
        response = self.client.post(
            reverse(
                "campaign_replan_state",
                args=[campaign.pk, first.pk],
            )
        )
        self.assertEqual(302, response.status_code, response.content)
        planner = campaign.work_orders.get(
            proposal__contract__replans_transition_id=str(first.pk)
        )
        self.assertEqual(first, planner.input_state)
        self.assertEqual(
            WorkOrder.StateBasis.ACCEPTED_TRANSITION,
            planner.state_basis,
        )
        self.assertEqual("planner", planner.protocol)
        self.assertEqual(
            str(first.pk),
            planner.packet["research_state_input"]["transition_id"],
        )
        self.assertEqual(
            first.state_artifact.digest,
            planner.packet["research_state_input"]["state_sha256"],
        )
        self.assertEqual(proposal_count + 1, campaign.proposals.count())
        self.assertEqual(order_count + 1, campaign.work_orders.count())
        self.assertEqual(Proposal.Author.DIRECTOR, planner.proposal.author)
        self.assertFalse(planner.proposal.children.exists())

    def test_continuation_must_match_the_exact_current_planner_input(
        self,
    ) -> None:
        campaign = self.create_campaign()
        initial_planner = campaign.work_orders.get(protocol="planner")
        root = self.planner_proposals(
            initial_planner,
            {
                "protocol": "research_worker",
                "title": "Reconstruct a comparable revenue state",
                "task": "Reconstruct a comparable revenue state",
                "contract": self.research_contract(
                    workbench_index=0,
                    mode="root",
                ),
            },
        )[0]
        w1 = self.approve(campaign, root)
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, first.pk])
        )

        t1_planner = request_planner_reentry(first, self.user)
        advance, stale_after_advance = self.planner_proposals(
            t1_planner,
            {
                "protocol": "research_worker",
                "title": "Decompose the comparable revenue change",
                "task": "Decompose the comparable revenue change",
                "contract": self.research_contract(
                    workbench_index=1,
                    mode="continue",
                ),
            },
            {
                "protocol": "research_worker",
                "title": "Another continuation planned from T1",
                "task": "Another continuation planned from T1",
                "contract": self.research_contract(
                    workbench_index=2,
                    mode="continue",
                ),
            },
        )
        w2 = self.approve(campaign, advance, transition=first)
        self.write_transition(
            w2,
            self.successor_state(w2, first),
            parent=first,
        )
        self.collect(campaign)
        second = ResearchStateTransition.objects.get(work_order=w2)
        self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, second.pk])
        )

        response = self.client.post(
            reverse(
                "campaign_approve_proposal",
                args=[campaign.pk, stale_after_advance.pk],
            ),
            {
                "state_basis": "accepted_transition",
                "input_state": str(second.pk),
            },
        )
        self.assertEqual(409, response.status_code, response.content)
        self.assertContains(
            response,
            (
                "This proposal was planned before the current evidence was "
                "accepted. Re-plan from current evidence before approving "
                "follow-on research."
            ),
            status_code=409,
        )
        self.assertFalse(
            WorkOrder.objects.filter(proposal=stale_after_advance).exists()
        )
        self.assertFalse(
            ProposalDisposition.objects.filter(
                proposal=stale_after_advance
            ).exists()
        )

        proposal_count = campaign.proposals.count()
        order_count = campaign.work_orders.count()
        response = self.client.post(
            reverse(
                "campaign_replan_state",
                args=[campaign.pk, first.pk],
            )
        )
        self.assertEqual(409, response.status_code, response.content)
        self.assertIn(b"accepted successor", response.content)
        self.assertEqual(proposal_count, campaign.proposals.count())
        self.assertEqual(order_count, campaign.work_orders.count())

        current = self.grounded_proposal(
            campaign,
            second,
            workbench_index=2,
            title="Reconstruct the current expectation surface",
        )
        response = self.client.post(
            reverse("campaign_approve_proposal", args=[campaign.pk, current.pk]),
            {
                "state_basis": "accepted_transition",
                "input_state": str(second.pk),
            },
        )
        self.assertEqual(302, response.status_code, response.content)
        self.assertEqual(
            second,
            WorkOrder.objects.get(proposal=current).input_state,
        )

    def test_planner_reentry_requires_the_director_and_a_current_state(
        self,
    ) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, first.pk])
        )
        outsider = get_user_model().objects.create_user(
            "not-director", password="local-password"
        )
        proposal_count = campaign.proposals.count()
        order_count = campaign.work_orders.count()

        with self.assertRaisesMessage(
            CampaignRejected,
            "only the campaign director may act",
        ):
            request_planner_reentry(first, outsider)
        self.assertEqual(proposal_count, campaign.proposals.count())
        self.assertEqual(order_count, campaign.work_orders.count())

        self.client.force_login(outsider)
        response = self.client.post(
            reverse(
                "campaign_replan_state",
                args=[campaign.pk, first.pk],
            )
        )
        self.assertEqual(404, response.status_code, response.content)
        self.assertEqual(proposal_count, campaign.proposals.count())
        self.assertEqual(order_count, campaign.work_orders.count())

    def test_w1_to_w2_preserves_authority_and_is_legible_to_the_director(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)

        response = self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, first.pk])
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            ResearchStateDisposition.Kind.ACCEPTED, first.disposition.kind
        )

        w2_proposal = self.grounded_proposal(
            campaign,
            first,
            workbench_index=1,
            title="Decompose the comparable revenue change",
        )
        w2 = self.approve(campaign, w2_proposal, transition=first)
        self.assertEqual(first, w2.input_state)
        self.assertEqual(
            first.state_artifact.digest,
            w2.packet["research_state_input"]["state_sha256"],
        )

        successor = self.successor_state(w2, first)
        self.write_transition(w2, successor, parent=first)
        self.collect(campaign)
        second = ResearchStateTransition.objects.get(work_order=w2)
        response = self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, second.pk])
        )
        self.assertEqual(302, response.status_code)
        preserved = json.loads(bytes(second.state_artifact.content))
        observation_ids = [
            item["observation_id"] for item in preserved["journal"]["observations"]
        ]
        for required in (
            "reported-prior-fact",
            "issuer-recast-assertion",
            "zero-residual-bridge",
            "derived-prior-observation",
            "driver-identity",
        ):
            self.assertIn(required, observation_ids)
        self.assertEqual(
            [
                {
                    "work_order_id": str(w1.pk),
                    "workbench": w1.proposal.contract["workbenches"][0],
                    "claim_ceiling": w1.proposal.contract["claim_ceiling"],
                },
                {
                    "work_order_id": str(w2.pk),
                    "workbench": w2.proposal.contract["workbenches"][0],
                    "claim_ceiling": w2.proposal.contract["claim_ceiling"],
                },
            ],
            preserved["journal"]["claim_ceiling_updates"],
        )

        page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(page, "Current investment case")
        self.assertContains(page, "What changed")
        self.assertContains(page, "New evidence")
        self.assertContains(page, "Issuer Q1 operating data")
        self.assertContains(page, "Units rose 5%; price and mix added 4%.")
        self.assertContains(
            page,
            "The exact driver identity ties against the issuer-recast comparable base",
        )
        self.assertContains(page, "Price or mix")
        self.assertContains(page, "Demand durability remains unlicensed.")
        self.assertContains(page, "Only the exact driver identity or refusal.")
        self.assertContains(
            page, "compare with cutoff-time expectation surfaces"
        )
        self.assertNotContains(page, "logical_role_id")

        self.client.logout()
        self.client.force_login(self.user)
        restarted = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(restarted, "The exact arithmetic identity ties.")
        self.assertContains(restarted, "accepted for continuation · current")
        self.assertContains(restarted, "accepted for continuation · history")
        self.assertEqual(first, w2.input_state)

        stale_proposal = self.proposal(
            campaign,
            workbench_index=2,
            title="Continue from the superseded comparable state",
            mode="continue",
        )
        response = self.client.post(
            reverse(
                "campaign_approve_proposal",
                args=[campaign.pk, stale_proposal.pk],
            ),
            {
                "state_basis": "accepted_transition",
                "input_state": str(first.pk),
            },
        )
        self.assertEqual(409, response.status_code)
        self.assertIn(b"accepted successor", response.content)
        self.assertFalse(WorkOrder.objects.filter(proposal=stale_proposal).exists())
        self.assertFalse(
            ProposalDisposition.objects.filter(proposal=stale_proposal).exists()
        )

        synthesis = record_proposal(
            campaign=campaign,
            author="planner",
            protocol="synthesis",
            title="Synthesize the accepted investment case",
            task="Reconcile the exact accepted research without selecting an action.",
            contract={},
        )
        page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertNotContains(page, "Use exact supporting record")
        self.assertContains(page, "Use supporting research:")
        response = self.client.post(
            reverse(
                "campaign_approve_proposal",
                args=[campaign.pk, synthesis.pk],
            ),
            {
                "state_basis": "commission",
                "input_artifacts": [str(second.state_artifact_id)],
            },
        )
        self.assertEqual(409, response.status_code)
        self.assertIn(b"typed state-input authority", response.content)
        self.assertFalse(
            ProposalDisposition.objects.filter(proposal=synthesis).exists()
        )
        response = self.client.post(
            reverse(
                "campaign_approve_proposal",
                args=[campaign.pk, synthesis.pk],
            ),
            {
                "state_basis": "commission",
                "supporting_states": [str(second.pk)],
            },
        )
        self.assertEqual(302, response.status_code)
        synthesis_order = WorkOrder.objects.get(proposal=synthesis)
        self.assertEqual(
            sorted(
                [
                    second.workbench_artifact_id,
                    second.state_artifact_id,
                    second.delta_artifact_id,
                ]
            ),
            synthesis_order.input_artifact_ids,
        )
        self.assertEqual(
            second.state_artifact.digest,
            synthesis_order.packet["supporting_research_states"][0][
                "state_sha256"
            ],
        )

    def test_only_synthesis_can_combine_independent_research_states(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        accepted = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, accepted.pk])
        )
        reviewer = record_proposal(
            campaign=campaign,
            author="planner",
            protocol="adversarial_review",
            title="Review the evidence route",
            task="Challenge the route without silently synthesizing it.",
            contract={},
        )

        page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertNotContains(page, "Use supporting research:")
        response = self.client.post(
            reverse(
                "campaign_approve_proposal",
                args=[campaign.pk, reviewer.pk],
            ),
            {
                "state_basis": "commission",
                "supporting_states": [str(accepted.pk)],
            },
        )

        self.assertEqual(409, response.status_code)
        self.assertIn(b"only synthesis", response.content)
        self.assertFalse(WorkOrder.objects.filter(proposal=reviewer).exists())
        self.assertFalse(
            ProposalDisposition.objects.filter(proposal=reviewer).exists()
        )

    def test_only_one_continuation_can_become_the_accepted_successor(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        parent = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, parent.pk])
        )
        first_order = self.approve(
            campaign,
            self.grounded_proposal(
                campaign,
                parent,
                workbench_index=1,
                title="First candidate driver continuation",
            ),
            transition=parent,
        )
        second_order = self.approve(
            campaign,
            self.grounded_proposal(
                campaign,
                parent,
                workbench_index=1,
                title="Second candidate driver continuation",
            ),
            transition=parent,
        )
        self.write_transition(
            first_order,
            self.successor_state(first_order, parent),
            parent=parent,
        )
        self.write_transition(
            second_order,
            self.successor_state(second_order, parent),
            parent=parent,
        )
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=first_order)
        second = ResearchStateTransition.objects.get(work_order=second_order)

        self.assertEqual(
            302,
            self.client.post(
                reverse("campaign_accept_state", args=[campaign.pk, first.pk])
            ).status_code,
        )
        response = self.client.post(
            reverse("campaign_accept_state", args=[campaign.pk, second.pk])
        )

        self.assertEqual(409, response.status_code)
        self.assertIn(b"accepted successor", response.content)
        self.assertFalse(
            ResearchStateDisposition.objects.filter(transition=second).exists()
        )

    def test_generic_state_cannot_replace_the_selected_workbench_result(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(
            w1,
            self.initial_state(w1),
            include_workbench_result=False,
        )

        response = self.collect(campaign, expected=409)

        self.assertIn(b"exact workbench result", response.content)
        self.assertFalse(Artifact.objects.filter(work_order=w1).exists())
        self.assertFalse(
            ResearchStateTransition.objects.filter(work_order=w1).exists()
        )

    def test_arbitrary_json_cannot_impersonate_the_w1_workbench_result(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        output = (
            Path(campaign.artifact_root) / "work" / str(w1.pk) / "out"
        )
        (output / "workbench-result.json").write_text("{}")

        response = self.collect(campaign, expected=409)

        self.assertIn(b"W1 workbench result", response.content)
        self.assertFalse(Artifact.objects.filter(work_order=w1).exists())

    def test_w2_cannot_detach_the_issuer_recast_authority_from_w1(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(reverse("campaign_accept_state", args=[campaign.pk, first.pk]))
        w2 = self.approve(
            campaign,
            self.grounded_proposal(
                campaign,
                first,
                workbench_index=1,
                title="Decompose the comparable revenue change",
            ),
            transition=first,
        )
        state = self.successor_state(w2, first)
        self.write_transition(w2, state, parent=first)
        output = Path(campaign.artifact_root) / "work" / str(w2.pk) / "out"
        result = json.loads((output / "workbench-result.json").read_bytes())
        result["upstream"]["issuer_assertion_observation_id"] = "driver-identity"
        result_bytes = canonical_bytes(result)
        (output / "workbench-result.json").write_bytes(result_bytes)
        state["workbench_result_sha256"] = sha256(result_bytes).hexdigest()
        state_bytes = json.dumps(state, indent=2).encode()
        (output / "research-state.json").write_bytes(state_bytes)
        delta = json.loads((output / "epistemic-delta.json").read_bytes())
        delta["after_state_sha256"] = sha256(state_bytes).hexdigest()
        (output / "epistemic-delta.json").write_bytes(canonical_bytes(delta))

        response = self.collect(campaign, expected=409)

        self.assertIn(b"W2 upstream authority", response.content)
        self.assertFalse(Artifact.objects.filter(work_order=w2).exists())

    def test_semantic_loss_fails_before_partial_custody(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(reverse("campaign_accept_state", args=[campaign.pk, first.pk]))
        w2 = self.approve(
            campaign,
            self.grounded_proposal(
                campaign,
                first,
                workbench_index=1,
                title="Decompose the comparable revenue change",
            ),
            transition=first,
        )
        lossy = self.successor_state(w2, first)
        lossy["journal"]["observations"] = [
            item
            for item in lossy["journal"]["observations"]
            if item["observation_id"] != "issuer-recast-assertion"
        ]
        self.write_transition(w2, lossy, parent=first)
        response = self.collect(campaign, expected=409)
        self.assertIn(b"research state dropped accepted history", response.content)
        self.assertFalse(Artifact.objects.filter(work_order=w2).exists())
        self.assertFalse(ResearchStateTransition.objects.filter(work_order=w2).exists())

    def test_post_cutoff_evidence_fails_before_partial_custody(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(reverse("campaign_accept_state", args=[campaign.pk, first.pk]))
        w2 = self.approve(
            campaign,
            self.grounded_proposal(
                campaign,
                first,
                workbench_index=1,
                title="Decompose the comparable revenue change",
            ),
            transition=first,
        )
        post_cutoff = self.successor_state(w2, first)
        post_cutoff["journal"]["source_receipts"][-1]["published_at"] = "2026-06-01"
        self.write_transition(w2, post_cutoff, parent=first)
        response = self.collect(campaign, expected=409)
        self.assertIn(b"source receipt exceeds the evidence cutoff", response.content)
        self.assertFalse(Artifact.objects.filter(work_order=w2).exists())

    def test_invented_source_origin_fails_before_partial_custody(self) -> None:
        campaign = self.create_campaign()
        w1 = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(w1, self.initial_state(w1))
        self.collect(campaign)
        first = ResearchStateTransition.objects.get(work_order=w1)
        self.client.post(reverse("campaign_accept_state", args=[campaign.pk, first.pk]))
        w2 = self.approve(
            campaign,
            self.grounded_proposal(
                campaign,
                first,
                workbench_index=1,
                title="Decompose the comparable revenue change",
            ),
            transition=first,
        )
        invented = self.successor_state(w2, first)
        invented["journal"]["observations"][-1]["source_receipt_ids"].append(
            "channel-sellthrough-route"
        )
        self.write_transition(w2, invented, parent=first)
        response = self.collect(campaign, expected=409)
        self.assertIn(b"source-receipt custody", response.content)
        self.assertFalse(Artifact.objects.filter(work_order=w2).exists())

    def test_director_challenge_and_rejection_remain_distinct_authority(self) -> None:
        campaign = self.create_campaign()
        order = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Reconstruct a comparable revenue state",
                mode="root",
            ),
        )
        self.write_transition(order, self.initial_state(order))
        self.collect(campaign)
        candidate = ResearchStateTransition.objects.get(work_order=order)

        feedback = "Challenge whether the issuer recast preserves the same scope."
        response = self.client.post(
            reverse("campaign_challenge_state", args=[campaign.pk, candidate.pk]),
            {"feedback": feedback},
        )
        self.assertEqual(302, response.status_code)
        candidate.refresh_from_db()
        self.assertEqual(
            ResearchStateDisposition.Kind.CHALLENGED,
            candidate.disposition.kind,
        )
        review = WorkOrder.objects.get(protocol="adversarial_review")
        self.assertEqual(candidate, review.input_state)
        self.assertEqual(feedback, review.packet["contract"]["director_feedback"])
        output = Path(campaign.artifact_root) / "work" / str(review.pk) / "out"
        output.mkdir(parents=True)
        (output / "review.md").write_text(
            "# Review\n\nBLOCK: the scope bridge needs an independent route.\n"
        )
        route_back = {
            "protocol": "research_worker",
            "title": "Reconstruct the scope bridge independently",
            "task": "Use an independent source route to test the issuer scope bridge.",
            "contract": self.research_contract(workbench_index=0, mode="root"),
        }
        (output / "proposals.jsonl").write_text(
            json.dumps(route_back) + "\n"
        )
        self.collect(campaign)
        proposed_route_back = campaign.proposals.get(
            parent=review.proposal,
            author="reviewer",
            title=route_back["title"],
        )
        self.assertFalse(
            WorkOrder.objects.filter(proposal=proposed_route_back).exists()
        )

        second_order = self.approve(
            campaign,
            self.proposal(
                campaign,
                workbench_index=0,
                title="Independently reconstruct comparability",
                mode="root",
            ),
        )
        second_state = deepcopy(self.initial_state(second_order))
        second_state["journal"]["decision_updates"][-1][
            "consequence"
        ] = "This candidate is not suitable for continuation."
        self.write_transition(second_order, second_state)
        self.collect(campaign)
        rejected = ResearchStateTransition.objects.get(work_order=second_order)
        response = self.client.post(
            reverse("campaign_reject_state", args=[campaign.pk, rejected.pk]),
            {"reason": "The source route is not independent."},
        )
        self.assertEqual(302, response.status_code)

        continuation = self.proposal(
            campaign,
            workbench_index=1,
            title="Continue a rejected state",
            mode="continue",
        )
        response = self.client.post(
            reverse("campaign_approve_proposal", args=[campaign.pk, continuation.pk]),
            {
                "state_basis": "accepted_transition",
                "input_state": str(rejected.pk),
            },
        )
        self.assertEqual(409, response.status_code)
        self.assertFalse(WorkOrder.objects.filter(proposal=continuation).exists())
        self.assertFalse(
            ProposalDisposition.objects.filter(proposal=continuation).exists()
        )
