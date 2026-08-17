from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from os import environ
from pathlib import Path
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase
from django.urls import reverse

from product.campaign.models import (
    Proposal,
    ProposalDisposition,
    Artifact,
    ResearchCampaign,
    RuntimeEvent,
    TraceLink,
    WorkOrder,
    canonical_bytes,
    canonical_digest,
)
from product.campaign.services import (
    CampaignRejected,
    approve_proposal,
    correlate_campaign,
    create_campaign,
    record_proposal,
    skill_catalog,
    workbench_catalog,
)
from harness.langfuse.transport import LangfuseConnection
from scenarios.adversarial._tue2_runtime_support import tracked_send_response


def write_worker_attestation(order: WorkOrder, output: Path) -> None:
    rows = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        if path.name == "artifact-attestation.json":
            continue
        content = path.read_bytes()
        rows.append(
            {
                "relative_path": path.relative_to(output).as_posix(),
                "byte_length": len(content),
                "sha256": sha256(content).hexdigest(),
            }
        )
    (output / "artifact-attestation.json").write_bytes(
        canonical_bytes(
            {
                "schema_version": "work-order-artifact-attestation/v1",
                "campaign_id": str(order.campaign_id),
                "work_order_id": str(order.pk),
                "logical_role_id": str(order.logical_role_id),
                "artifacts": rows,
                "authority": "worker_candidate_attestation",
            }
        )
    )


def mark_mechanical_completion(order: WorkOrder) -> None:
    event_id = uuid.uuid4()
    send_payload = {
        "id": str(event_id),
        "campaign": str(order.campaign_id),
        "work_order": str(order.pk),
        "kind": RuntimeEvent.Kind.SEND,
        "generation": 1,
        "request": {"argv": ["mechanical-test-only-send", "--panes=2"]},
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
            "argv": ["mechanical-test-only-completion", "--panes=2"]
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


def record_runtime_event(
    *,
    campaign: ResearchCampaign,
    order: WorkOrder | None,
    kind: str,
    response: dict[str, object],
) -> RuntimeEvent:
    event_id = uuid.uuid4()
    payload = {
        "id": str(event_id),
        "campaign": str(campaign.pk),
        "work_order": str(order.pk) if order else None,
        "kind": kind,
        "generation": 1,
        "request": {"argv": ["mechanical-lifecycle-check"]},
        "response": response,
        "succeeded": True,
    }
    return RuntimeEvent.objects.create(
        id=event_id,
        campaign=campaign,
        work_order=order,
        kind=kind,
        request=payload["request"],
        response=response,
        succeeded=True,
        digest=canonical_digest(payload),
    )


def research_contract(**extra):
    workbench = workbench_catalog()[0]
    reasoning = next(
        item
        for item in skill_catalog()
        if item["name"] == "research-frame-search-with-domain-mechanisms"
    )
    return {
        "workbenches": [
            {
                key: workbench[key]
                for key in ("workbench_id", "version", "protocol_sha256")
            }
        ],
        "research_state": {"mode": "root"},
        "decision_hinge": "Does this evidence change the commissioned decision?",
        "claim_ceiling": "Preserve only the exact bounded research contribution.",
        "reasoning_operators": [
            {
                **reasoning,
                "failure_tested": "proxy-to-target substitution",
                "expected_epistemic_delta": "preserve a bounded claim",
                "kill_condition": "no research state changes",
            }
        ],
        **extra,
    }


class LeanCampaignFacadeTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            "director", password="local-password"
        )
        self.client.force_login(self.user)

    def create_campaign(self) -> ResearchCampaign:
        # Historical TUE campaigns remain inspectable but are no longer the
        # ordinary job-creation path.
        return create_campaign(
            director=self.user,
            title="NVIDIA earnings quality",
            issuer_or_security="NVIDIA Corporation",
            equities_decision_use="Decide whether the revenue surprise changes the position.",
            evidence_cutoff="2026-05-31",
            question=(
                "Was the revenue surprise durable demand, price or mix, "
                "channel timing, or stale expectations?"
            ),
        )

    def test_casebook_preserves_human_language_and_hides_runtime_ontology(self) -> None:
        campaign = self.create_campaign()

        page = self.client.get(reverse("campaign", args=[campaign.pk]))

        self.assertContains(page, "NVIDIA earnings quality")
        self.assertContains(page, "What must be decided")
        self.assertContains(page, "Design the research programme")
        for implementation_noun in (
            "role_instance_id",
            "artifact_id",
            "packet",
            "pane",
            "tmux",
        ):
            self.assertNotContains(page, implementation_noun)

    def test_planning_permission_is_not_approved_research_and_runtime_block_is_visible(
        self,
    ) -> None:
        campaign = self.create_campaign()
        response = self.client.post(
            reverse("campaign_approve_planner_programme", args=[campaign.pk])
        )
        self.assertEqual(302, response.status_code)
        planner = WorkOrder.objects.get(campaign=campaign, protocol="planner")

        with patch.dict(environ, {}, clear=True):
            page = self.client.get(reverse("campaign", args=[campaign.pk]))

        self.assertContains(page, "Programme design authorized")
        self.assertContains(page, "No planner-produced research plan exists yet.")
        self.assertNotContains(page, "Approved research")
        self.assertContains(page, "Research runtime is not ready")
        self.assertContains(page, "Langfuse target project is absent or invalid")
        self.assertContains(page, str(planner.proposal_id))
        self.assertContains(page, planner.proposal.digest)
        self.assertNotContains(page, "Start this research step")
        self.assertNotContains(page, "Collect new research results")
        self.assertNotContains(page, "Stop this campaign runtime")
        self.assertEqual(0, campaign.runtime_events.count())

    def test_missing_current_runtime_config_does_not_erase_prior_history(
        self,
    ) -> None:
        campaign = self.create_campaign()
        self.client.post(
            reverse("campaign_approve_planner_programme", args=[campaign.pk])
        )
        planner = WorkOrder.objects.get(campaign=campaign, protocol="planner")
        record_runtime_event(
            campaign=campaign,
            order=planner,
            kind=RuntimeEvent.Kind.LAUNCH,
            response={"success": True},
        )

        with patch.dict(environ, {}, clear=True):
            page = self.client.get(reverse("campaign", args=[campaign.pk]))

        self.assertContains(page, "Existing history remains visible below.")
        self.assertNotContains(
            page,
            "No Codex session has started and no research output exists.",
        )

    def test_runtime_controls_follow_current_lifecycle_and_work_stage(
        self,
    ) -> None:
        campaign = self.create_campaign()
        self.client.post(
            reverse("campaign_approve_planner_programme", args=[campaign.pk])
        )
        planner = WorkOrder.objects.get(campaign=campaign, protocol="planner")
        mark_mechanical_completion(planner)
        proposal = record_proposal(
            campaign=campaign,
            author="planner",
            protocol="research_worker",
            title="Test one material research branch",
            task="Research the commissioned decision hinge.",
            contract=research_contract(),
        )
        approve_proposal(proposal, user=self.user)

        with patch.dict(environ, {}, clear=True):
            page = self.client.get(reverse("campaign", args=[campaign.pk]))

        self.assertContains(page, "Collect the planner's research design")
        self.assertNotContains(page, "Collect new research results")
        self.assertNotContains(page, "Stop this campaign runtime")

        record_runtime_event(
            campaign=campaign,
            order=planner,
            kind=RuntimeEvent.Kind.LAUNCH,
            response={"success": True},
        )
        record_runtime_event(
            campaign=campaign,
            order=None,
            kind=RuntimeEvent.Kind.STOP,
            response={"success": True},
        )
        with patch.dict(environ, {}, clear=True):
            stopped_page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertNotContains(stopped_page, "Stop this campaign runtime")

    def test_failed_start_returns_the_casebook_with_the_exact_non_action(
        self,
    ) -> None:
        campaign = self.create_campaign()
        response = self.client.post(
            reverse("campaign_approve_planner_programme", args=[campaign.pk])
        )
        self.assertEqual(302, response.status_code)
        planner = WorkOrder.objects.get(campaign=campaign, protocol="planner")

        with patch.dict(environ, {}, clear=True):
            page = self.client.post(
                reverse("campaign_launch", args=[campaign.pk, planner.pk])
            )

        self.assertEqual(409, page.status_code)
        self.assertContains(page, "NVIDIA earnings quality", status_code=409)
        self.assertContains(page, "Research did not start", status_code=409)
        self.assertContains(
            page,
            "No Codex session has started",
            status_code=409,
        )
        self.assertContains(
            page,
            "Langfuse target project is absent or invalid",
            status_code=409,
        )
        self.assertNotContains(
            page,
            "Start this research step",
            status_code=409,
        )
        self.assertEqual(0, campaign.runtime_events.count())

    def test_work_order_freezes_the_exact_output_custody_contract(self) -> None:
        campaign = self.create_campaign()
        proposal = record_proposal(
            campaign=campaign,
            author="planner",
            protocol="research_worker",
            title="Reconstruct comparable state",
            task="Produce the exact comparable-state result.",
            contract=research_contract(),
        )

        order = approve_proposal(proposal, user=self.user)

        expected_root = (
            Path(campaign.artifact_root)
            / "work"
            / str(order.pk)
            / "out"
        )
        self.assertEqual(
            {
                "schema_version": "work-order-output/v1",
                "output_root": str(expected_root),
                "campaign_relative_root": f"work/{order.pk}/out",
                "write_policy": "write_only_beneath_output_root",
                "required_paths": [
                    "branch.md",
                    "epistemic-delta.json",
                    "research-state.json",
                    "workbench-result.json",
                ],
                "primary_path": "branch.md",
                "attestation_path": "artifact-attestation.json",
                "population_policy": "regular_files_at_output_root_only",
            },
            order.packet["output_contract"],
        )
        self.assertFalse(expected_root.exists())

    def test_planner_framing_gates_routes_and_preserves_revision_lineage(
        self,
    ) -> None:
        campaign = self.create_campaign()
        self.client.post(
            reverse("campaign_approve_planner_programme", args=[campaign.pk])
        )
        planner = WorkOrder.objects.get(campaign=campaign, protocol="planner")
        output = Path(planner.packet["output_contract"]["output_root"])
        output.mkdir(parents=True)
        framing = (
            "Decision hinge: durable demand versus an expectation error.\n\n"
            "Stop if cutoff-time expectations cannot be reconstructed."
        )
        (output / "plan.md").write_text(framing)
        (output / "proposals.jsonl").write_text(
            json.dumps(
                {
                    "protocol": "research_worker",
                    "title": "Reconstruct cutoff-time expectations",
                    "task": "Separate guidance, consensus, and narrative.",
                    "contract": research_contract(),
                }
            )
            + "\n"
        )
        write_worker_attestation(planner, output)
        mark_mechanical_completion(planner)
        self.client.post(reverse("campaign_collect", args=[campaign.pk]))
        interpretation = Proposal.objects.get(
            contract__authority_limit="planner_interpretation_only"
        )
        expectation_route = Proposal.objects.get(
            title="Reconstruct cutoff-time expectations"
        )
        self.assertEqual(interpretation, expectation_route.parent)
        with self.assertRaises(CampaignRejected):
            record_proposal(
                campaign=campaign,
                author=Proposal.Author.PLANNER,
                protocol="planner",
                title="Counterfeit interpretation",
                task=framing,
                contract=interpretation.contract,
            )
        page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(page, "What I think you mean")
        self.assertContains(page, framing)
        self.assertNotContains(page, "Approve this research step")
        self.assertEqual(
            409,
            self.client.post(
                reverse(
                    "campaign_approve_proposal",
                    args=[campaign.pk, expectation_route.pk],
                )
            ).status_code,
        )

        savepoint = transaction.savepoint()
        try:
            self.client.post(
                reverse(
                    "campaign_approve_proposal",
                    args=[campaign.pk, interpretation.pk],
                )
            )
            self.assertFalse(
                WorkOrder.objects.filter(proposal=interpretation).exists()
            )
            page = self.client.get(reverse("campaign", args=[campaign.pk]))
            self.assertContains(page, "Reconstruct cutoff-time expectations")
            self.assertContains(page, "Approve this research step")
            self.assertEqual(
                302,
                self.client.post(
                    reverse(
                        "campaign_approve_proposal",
                        args=[campaign.pk, expectation_route.pk],
                    )
                ).status_code,
            )
            self.assertTrue(
                WorkOrder.objects.filter(proposal=expectation_route).exists()
            )
        finally:
            transaction.savepoint_rollback(savepoint)

        interpretation = Proposal.objects.get(pk=interpretation.pk)
        expectation_route = Proposal.objects.get(pk=expectation_route.pk)
        feedback = (
            "  You omitted the channel-inventory rival. Preserve it, and state "
            "what evidence would distinguish pull-forward.  \n"
        )
        self.client.post(
            reverse(
                "campaign_request_proposal_revision",
                args=[campaign.pk, interpretation.pk],
            ),
            {"feedback": feedback},
        )
        interpretation.refresh_from_db()
        self.assertEqual(feedback, interpretation.disposition.feedback)
        revision_order = WorkOrder.objects.get(
            proposal__contract__revises_proposal_id=str(interpretation.pk)
        )
        expected_inputs = sorted(
            [
                interpretation.contract["plan_artifact"]["artifact_id"],
                interpretation.contract["routes_artifact"]["artifact_id"],
            ]
        )
        self.assertEqual(expected_inputs, revision_order.input_artifact_ids)
        self.assertEqual(
            feedback, revision_order.packet["contract"]["director_feedback"]
        )
        for key in ("workbench_catalog", "skill_catalog", "reasoning_operators"):
            self.assertEqual(
                planner.packet["contract"][key],
                revision_order.packet["contract"][key],
            )
        self.assertEqual(
            planner.packet["required_reads"],
            revision_order.packet["required_reads"],
        )
        self.assertEqual(
            expected_inputs,
            sorted(row["artifact_id"] for row in revision_order.packet["inputs"]),
        )
        self.assertEqual(
            409,
            self.client.post(
                reverse(
                    "campaign_approve_proposal",
                    args=[campaign.pk, expectation_route.pk],
                )
            ).status_code,
        )

    def test_reject_revision_and_rewrite_are_exact_separate_authority_acts(self) -> None:
        campaign = self.create_campaign()
        rejected = record_proposal(
            campaign=campaign,
            author="planner",
            protocol="research_worker",
            title="Use channel inventory to test pull-forward",
            task="Compare distributor inventory and sell-through at the cutoff.",
            contract=research_contract(
                claim_ceiling="supports_or_blocks_pull_forward"
            ),
        )

        response = self.client.post(
            reverse("campaign_reject_proposal", args=[campaign.pk, rejected.pk]),
            {"reason": "The source route is not independent."},
        )
        self.assertEqual(302, response.status_code)
        rejected.refresh_from_db()
        self.assertEqual(
            ProposalDisposition.Kind.REJECTED,
            rejected.disposition.kind,
        )
        self.assertFalse(WorkOrder.objects.filter(proposal=rejected).exists())

        revisable = record_proposal(
            campaign=campaign,
            author="planner",
            protocol="research_worker",
            title="Reconstruct consensus freshness",
            task="Recover revisions before the evidence cutoff.",
            contract=research_contract(
                claim_ceiling="expectation_staleness_only"
            ),
        )
        feedback = "Separate published consensus from narrative and positioning."
        response = self.client.post(
            reverse(
                "campaign_request_proposal_revision",
                args=[campaign.pk, revisable.pk],
            ),
            {"feedback": feedback},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(feedback, revisable.disposition.feedback)
        revision_order = WorkOrder.objects.get(
            proposal__contract__revises_proposal_id=str(revisable.pk)
        )
        self.assertEqual("planner", revision_order.protocol)
        self.assertEqual(
            feedback,
            revision_order.packet["contract"]["director_feedback"],
        )
        output = (
            Path(campaign.artifact_root)
            / "work"
            / str(revision_order.pk)
            / "out"
        )
        output.mkdir(parents=True)
        proposal_row = {
            "protocol": "research_worker",
            "title": "Reconstruct cutoff-time expectations",
            "task": "Separate consensus, guidance, narrative and positioning.",
            "contract": research_contract(
                claim_ceiling="expectation_staleness_only"
            ),
        }
        (output / "plan.md").write_text(
            "# Revised programme\n\nReconstruct cutoff-time expectations.\n"
        )
        (output / "proposals.jsonl").write_text(json.dumps(proposal_row) + "\n")
        write_worker_attestation(revision_order, output)
        mark_mechanical_completion(revision_order)
        self.assertEqual(
            302,
            self.client.post(reverse("campaign_collect", args=[campaign.pk])).status_code,
        )
        planner_child = Proposal.objects.get(
            parent=revisable,
            author=Proposal.Author.PLANNER,
        )
        self.assertFalse(WorkOrder.objects.filter(proposal=planner_child).exists())

        response = self.client.post(
            reverse("campaign_rewrite_proposal", args=[campaign.pk, revisable.pk]),
            {
                "target_role": "research_worker",
                "task": "Reconstruct only cutoff-time consensus and guidance.",
                "rationale": "Avoid post-event backfit.",
            },
        )
        self.assertEqual(302, response.status_code)
        child = Proposal.objects.get(
            parent=revisable,
            author=Proposal.Author.DIRECTOR,
        )
        self.assertEqual("director", child.author)
        self.assertFalse(WorkOrder.objects.filter(proposal=child).exists())

        response = self.client.post(
            reverse("campaign_approve_proposal", args=[campaign.pk, child.pk]),
            {"instance_mode": "fresh"},
        )
        self.assertEqual(302, response.status_code)
        order = WorkOrder.objects.get(proposal=child)
        self.assertEqual(child.digest, order.proposal_digest)
        page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(page, feedback)
        self.assertContains(page, "Reconstruct only cutoff-time consensus and guidance.")

    def test_provider_population_joins_worker_attested_bytes_without_provider_ids(
        self,
    ) -> None:
        campaign = self.create_campaign()
        proposal = record_proposal(
            campaign=campaign,
            author="planner",
            protocol="research_worker",
            title="Reconstruct comparable state",
            task="Produce the exact comparable-state result.",
            contract=research_contract(),
        )
        order = approve_proposal(proposal, user=self.user)
        outputs = {
            "branch.md": b"# Comparable state\n",
            "workbench-result.json": b'{"status":"UNRECONCILED"}',
            "research-state.json": b'{"state":"candidate"}',
            "epistemic-delta.json": b'{"delta":"refusal"}',
        }
        artifacts = {}
        for relative_path, content in outputs.items():
            artifacts[relative_path] = Artifact.objects.create(
                campaign=campaign,
                work_order=order,
                kind=Path(relative_path).stem,
                relative_path=relative_path,
                version=1,
                media_type=(
                    "application/json"
                    if relative_path.endswith(".json")
                    else "text/markdown"
                ),
                content=content,
                digest=sha256(content).hexdigest(),
            )
        attestation = {
            "schema_version": "work-order-artifact-attestation/v1",
            "campaign_id": str(campaign.pk),
            "work_order_id": str(order.pk),
            "logical_role_id": str(order.logical_role_id),
            "artifacts": [
                {
                    "relative_path": relative_path,
                    "byte_length": len(content),
                    "sha256": sha256(content).hexdigest(),
                }
                for relative_path, content in sorted(outputs.items())
            ],
            "authority": "worker_candidate_attestation",
        }
        attestation_bytes = json.dumps(
            attestation, sort_keys=True, separators=(",", ":")
        ).encode()
        Artifact.objects.create(
            campaign=campaign,
            work_order=order,
            kind="artifact-attestation",
            relative_path="artifact-attestation.json",
            version=1,
            media_type="application/json",
            content=attestation_bytes,
            digest=sha256(attestation_bytes).hexdigest(),
        )
        mark_mechanical_completion(order)
        provider_metadata = {
            "flywheel_run_id": str(campaign.pk),
            "flywheel_work_order_id": str(order.pk),
            "flywheel_work_order_proposal_digest": order.proposal_digest,
            "flywheel_role_instance": str(order.logical_role_id),
            "flywheel_role_contract": order.packet["required_reads"][0]["sha256"],
            "attributes": {
                "thread.id": "conversation-1",
                "turn.id": "turn-1",
            },
            "resourceAttributes": {},
        }
        provider = [
            {
                "id": "1" * 16,
                "traceId": "a" * 32,
                "startTime": "2026-05-31T10:00:00Z",
                "endTime": "2026-05-31T10:00:02Z",
                "projectId": "project",
                "parentObservationId": None,
                "type": "SPAN",
                "name": "session_task.turn",
                "level": "DEFAULT",
                "statusMessage": None,
                "sessionId": str(campaign.pk),
                "metadata": provider_metadata,
            },
            {
                "id": "2" * 16,
                "traceId": "a" * 32,
                "startTime": "2026-05-31T10:00:01Z",
                "endTime": "2026-05-31T10:00:02Z",
                "projectId": "project",
                "parentObservationId": "1" * 16,
                "type": "GENERATION",
                "name": "codex.response",
                "level": "DEFAULT",
                "statusMessage": None,
                "sessionId": str(campaign.pk),
                "metadata": provider_metadata,
                "providedModelName": "gpt-5.6-sol",
                "usageDetails": {"input": 12, "output": 4},
            },
        ]
        with self.settings(
            LANGFUSE_TARGET_BASE_URL="https://cloud.langfuse.com",
            LANGFUSE_TARGET_PROJECT_ID="project",
        ):
            with (
                patch(
                    "product.campaign.services.readback_project_identity"
                ),
                patch(
                    "product.campaign.services.readback_observations",
                    return_value=provider,
                ),
            ):
                with self.assertRaisesRegex(
                    CampaignRejected,
                    "does not match the configured project",
                ):
                    correlate_campaign(
                        campaign,
                        self.user,
                        LangfuseConnection(
                            "https://cloud.langfuse.com",
                            "wrong-project",
                            "Basic cGstbGYteDpzay1sZi14",
                        ),
                    )
                incomplete = [{**provider[0], "metadata": {
                    key: value
                    for key, value in provider_metadata.items()
                    if key != "flywheel_work_order_id"
                }}]
                with patch(
                    "product.campaign.services.readback_observations",
                    return_value=incomplete,
                ):
                    with self.assertRaisesRegex(
                        CampaignRejected,
                        "work-order population",
                    ):
                        correlate_campaign(
                            campaign,
                            self.user,
                            LangfuseConnection(
                                "https://cloud.langfuse.com",
                                "project",
                                "Basic cGstbGYteDpzay1sZi14",
                            ),
                        )
                links = correlate_campaign(
                    campaign,
                    self.user,
                    LangfuseConnection(
                        "https://cloud.langfuse.com",
                        "project",
                        "Basic cGstbGYteDpzay1sZi14",
                    ),
                )

        self.assertEqual(artifacts["branch.md"], links[0].artifact)
        self.assertEqual("1" * 16, links[0].observation_id)
        self.assertEqual("conversation-1", links[0].conversation_id)
        self.assertEqual("turn-1", links[0].call_id)
