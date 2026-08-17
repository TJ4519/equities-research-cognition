from __future__ import annotations

from copy import deepcopy
import json
from os import environ
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.urls import reverse

from harness.ntm.adapter import ExecutionResult
from product.campaign.models import (
    ResearchCampaign,
    RuntimeEvent,
    WorkOrder,
    canonical_bytes,
    canonical_digest,
)
from product.campaign.services import (
    _completion_observed,
    _launch_response_succeeded,
    _runtime_event,
    create_campaign,
    record_proposal,
    skill_catalog,
    workbench_catalog,
)
from scenarios.adversarial._tue2_runtime_support import tracked_send_response


class RuntimeProviderTests(TestCase):
    """MECHANICAL_REGRESSION_ONLY for runtime and provider boundaries."""

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

    def test_exact_ntm_kill_receipt_is_not_a_generic_success(self) -> None:
        campaign = self.create_campaign()

        def stop_event(session: str) -> RuntimeEvent:
            response = {
                "killed": True,
                "session": session,
                "generated_at": "2026-08-05T10:48:51Z",
            }
            return _runtime_event(
                campaign=campaign,
                order=None,
                kind=RuntimeEvent.Kind.STOP,
                argv=["controlled-stop"],
                result=ExecutionResult(0, b"", b"", response),
            )

        self.assertFalse(stop_event("another-campaign").succeeded)
        self.assertTrue(stop_event(campaign.ntm_session).succeeded)

    def test_completion_for_another_selected_pane_is_not_this_work_order(self) -> None:
        campaign = self.create_campaign()
        order = campaign.work_orders.get(protocol="planner")
        send_id = uuid.uuid4()
        send_payload = {
            "id": str(send_id),
            "campaign": str(order.campaign_id),
            "work_order": str(order.pk),
            "kind": RuntimeEvent.Kind.SEND,
            "generation": 1,
            "request": {"argv": ["mechanical-test-only-send", "--panes=2"]},
            "response": tracked_send_response(order, "2"),
            "succeeded": True,
        }
        RuntimeEvent.objects.create(
            id=send_id,
            campaign=order.campaign,
            work_order=order,
            kind=RuntimeEvent.Kind.SEND,
            request=send_payload["request"],
            response=send_payload["response"],
            succeeded=True,
            digest=canonical_digest(send_payload),
        )
        completion_id = uuid.uuid4()
        completion_payload = {
            "id": str(completion_id),
            "campaign": str(order.campaign_id),
            "work_order": str(order.pk),
            "kind": RuntimeEvent.Kind.STATUS,
            "generation": 1,
            "request": {
                "argv": ["mechanical-test-only-completion", "--panes=3"],
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
            id=completion_id,
            campaign=order.campaign,
            work_order=order,
            kind=RuntimeEvent.Kind.STATUS,
            request=completion_payload["request"],
            response=completion_payload["response"],
            succeeded=True,
            digest=canonical_digest(completion_payload),
        )

        self.assertFalse(_completion_observed(order))

    def test_launch_receipt_for_another_session_is_not_success(self) -> None:
        campaign = self.create_campaign()

        self.assertFalse(
            _launch_response_succeeded(
                {
                    "success": True,
                    "session": "another-campaign",
                    "agents": [{"title": "planner"}],
                },
                session=campaign.ntm_session,
            )
        )

    def test_tracked_send_timeout_is_not_a_successful_dispatch(self) -> None:
        class ControlledNtm:
            def spawn_command(self, *args):
                return ["controlled-launch"]

            def status_command(self, *args):
                return ["controlled-status"]

            def send_command(self, session, index, message, config):
                return ["controlled-send", f"--panes={index}"]

            def execute(self, argv, *, environment):
                if argv == ["controlled-launch"]:
                    response = {
                        "success": True,
                        "session": campaign.ntm_session,
                        "agents": [{"title": "planner"}],
                    }
                elif argv == ["controlled-status"]:
                    response = {
                        "generated_at": "2026-08-04T17:00:00Z",
                        "session": campaign.ntm_session,
                        "exists": True,
                        "working_directory": str(Path(campaign.artifact_root)),
                        "panes": [
                            {
                                "title": "planner",
                                "type": "codex",
                                "command": "codex",
                                "context_model": "gpt-5.6-sol",
                                "index": 2,
                            }
                        ],
                        "agent_counts": {"codex": 1},
                    }
                else:
                    response = tracked_send_response(order)
                    response["success"] = False
                    response["ack"]["success"] = False
                    response["ack"]["confirmations"] = []
                    response["ack"]["pending"] = ["2"]
                    response["ack"]["timed_out"] = True
                return ExecutionResult(
                    exit_code=0,
                    stdout=canonical_bytes(response),
                    stderr=b"",
                    response=response,
                )

        campaign = self.create_campaign()
        order = campaign.work_orders.get(protocol="planner")
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
            self.client.post(
                reverse("campaign_launch", args=[campaign.pk, order.pk])
            )
            self.client.post(
                reverse("campaign_refresh", args=[campaign.pk, order.pk])
            )
            response = self.client.post(
                reverse("campaign_send", args=[campaign.pk, order.pk])
            )

        self.assertEqual(302, response.status_code, response.content)
        send = order.runtime_events.get(kind=RuntimeEvent.Kind.SEND)
        self.assertFalse(send.succeeded)
        page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(page, "Dispatch was not acknowledged")
        self.assertContains(page, "execution outcome is unknown")
        self.assertNotContains(page, "No research was started")

    def test_progress_refresh_targets_the_selected_older_work_order(self) -> None:
        class ControlledNtm:
            def spawn_command(self, *args):
                return ["launch-planner"]

            def add_command(self, *args):
                return ["launch-researcher"]

            def status_command(self, *args):
                return ["readiness"]

            def send_command(self, session, index, message, config):
                return ["send", f"--panes={index}"]

            def completion_command(self, session, index, config):
                return ["completion", f"--panes={index}"]

            def execute(self, argv, *, environment):
                if argv == ["launch-planner"]:
                    response = {
                        "success": True,
                        "session": campaign.ntm_session,
                        "agents": [{"title": "planner-pane"}],
                    }
                elif argv == ["launch-researcher"]:
                    response = {
                        "session": campaign.ntm_session,
                        "new_panes": [
                            {
                                "type": "cod",
                                "title": "researcher-pane",
                                "command": "run-researcher",
                            }
                        ],
                        "added_codex": 1,
                        "total_added": 1,
                        "generated_at": "2026-08-04T17:00:00Z",
                    }
                elif argv == ["readiness"]:
                    response = {
                        "generated_at": "2026-08-04T17:00:00Z",
                        "session": campaign.ntm_session,
                        "exists": True,
                        "working_directory": str(Path(campaign.artifact_root)),
                        "panes": [
                            {
                                "title": "planner-pane",
                                "type": "codex",
                                "command": "codex",
                                "context_model": "gpt-5.6-sol",
                                "index": 2,
                            },
                            {
                                "title": "researcher-pane",
                                "type": "codex",
                                "command": "codex",
                                "context_model": "gpt-5.6-sol",
                                "index": 3,
                            },
                        ],
                        "agent_counts": {"codex": 2},
                    }
                elif argv[0] == "send":
                    pane = argv[1].split("=", 1)[1]
                    selected = planner if pane == "2" else researcher
                    response = tracked_send_response(selected, pane)
                else:
                    pane = argv[1].split("=", 1)[1]
                    response = {
                        "success": True,
                        "session": campaign.ntm_session,
                        "condition": "complete",
                        "agents": [
                            {
                                "pane": f"%opaque-{pane}",
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

        campaign = self.create_campaign()
        planner = campaign.work_orders.get(protocol="planner")
        workbench = workbench_catalog()[0]
        research_frame = next(
            item
            for item in skill_catalog()
            if item["name"] == "research-frame-search-with-domain-mechanisms"
        )
        proposal = record_proposal(
            campaign=campaign,
            author="planner",
            protocol="research_worker",
            title="Reconstruct a comparable revenue state",
            task="Reconstruct a comparable revenue state",
            contract={
                "workbenches": [
                    {
                        key: workbench[key]
                        for key in (
                            "workbench_id",
                            "version",
                            "protocol_sha256",
                        )
                    }
                ],
                "research_state": {"mode": "root"},
                "decision_hinge": "Does the surprise change position sizing?",
                "claim_ceiling": (
                    "Only the exact comparable-state result or refusal."
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
            },
        )
        approval = self.client.post(
            reverse(
                "campaign_approve_proposal",
                args=[campaign.pk, proposal.pk],
            ),
            {"state_basis": "commission"},
        )
        self.assertEqual(302, approval.status_code, approval.content)
        researcher = WorkOrder.objects.get(proposal=proposal)
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
            for order in (planner, researcher):
                self.client.post(
                    reverse("campaign_launch", args=[campaign.pk, order.pk])
                )
                self.client.post(
                    reverse("campaign_refresh", args=[campaign.pk, order.pk])
                )
                self.client.post(
                    reverse("campaign_send", args=[campaign.pk, order.pk])
                )
            response = self.client.post(
                reverse("campaign_refresh", args=[campaign.pk, planner.pk])
            )

        self.assertEqual(302, response.status_code, response.content)
        self.assertTrue(
            researcher.runtime_events.get(kind=RuntimeEvent.Kind.LAUNCH).succeeded
        )
        completion = campaign.runtime_events.order_by("-created_at").first()
        self.assertEqual(planner, completion.work_order)
        self.assertEqual(
            "2",
            next(
                item.split("=", 1)[1]
                for item in completion.request["argv"]
                if item.startswith("--panes=")
            ),
        )
        self.assertEqual(
            "%opaque-2", completion.response["agents"][0]["pane"]
        )

    def test_pre_contract_work_order_is_inspectable_but_not_launchable(self) -> None:
        class ControlledNtm:
            calls = 0

            def spawn_command(self, *args):
                return ["should-not-run"]

            def execute(self, argv, *, environment):
                self.calls += 1
                return ExecutionResult(0, b"{}", b"", {})

        campaign = self.create_campaign()
        order = campaign.work_orders.get(protocol="planner")
        legacy_packet = deepcopy(order.packet)
        legacy_packet.pop("output_contract")
        legacy_digest = canonical_digest(
            {
                "id": str(order.pk),
                "campaign": str(order.campaign_id),
                "proposal": str(order.proposal_id),
                "logical_role_id": str(order.logical_role_id),
                "protocol": order.protocol,
                "proposal_digest": order.proposal_digest,
                "input_artifact_ids": order.input_artifact_ids,
                "state_basis": order.state_basis,
                "input_state": None,
                "packet": legacy_packet,
            }
        )
        table = connection.ops.quote_name(WorkOrder._meta.db_table)
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {table} SET packet = %s, digest = %s WHERE id = %s",
                [json.dumps(legacy_packet), legacy_digest, order.pk],
            )
        order.refresh_from_db()
        control = ControlledNtm()
        target = {
            "FLYWHEEL_LANGFUSE_AUTHORIZATION": "Basic cGstbGYteDpzay1sZi14",
        }
        page = self.client.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(page, "predates the current execution contract")
        self.assertNotContains(
            page,
            reverse("campaign_launch", args=[campaign.pk, order.pk]),
        )
        with (
            self.settings(
                CAMPAIGN_CODEX_BINARY="/usr/bin/true",
                LANGFUSE_TARGET_BASE_URL="https://cloud.langfuse.com",
                LANGFUSE_TARGET_PROJECT_ID="project-1",
            ),
            patch("product.campaign.services.adapter", return_value=control),
            patch.dict(environ, target, clear=False),
            patch("product.campaign.services.readback_project_identity"),
        ):
            response = self.client.post(
                reverse("campaign_launch", args=[campaign.pk, order.pk])
            )
        self.assertEqual(409, response.status_code, response.content)
        self.assertIn(b"new work order", response.content)
        self.assertEqual(0, control.calls)

    def test_launch_rejects_drift_in_a_referenced_skill_file(self) -> None:
        class ControlledNtm:
            def spawn_command(self, *args):
                return ["controlled-launch"]

            def execute(self, argv, *, environment):
                return ExecutionResult(
                    exit_code=0,
                    stdout=b'{"success":true,"agents":[{"title":"planner"}]}',
                    stderr=b"",
                    response={
                        "success": True,
                        "agents": [{"title": "planner"}],
                    },
                )

        skill_root = Path(self.temp.name) / "skills"
        installed = Path.home() / ".codex" / "skills"
        for name in (
            "research-frame-search-with-domain-mechanisms",
            "modes-of-reasoning-panel",
        ):
            copytree(installed / name, skill_root / name)
        runtime = self.settings(
            CAMPAIGN_CODEX_BINARY="/usr/bin/true",
            CAMPAIGN_CODEX_MODEL="gpt-5.6-sol",
            CAMPAIGN_CODEX_SKILL_ROOT=skill_root,
            LANGFUSE_TARGET_BASE_URL="https://cloud.langfuse.com",
            LANGFUSE_TARGET_PROJECT_ID="project-1",
        )
        with runtime:
            campaign = self.create_campaign()
            planner = WorkOrder.objects.get(campaign=campaign, protocol="planner")
            target = {
                "FLYWHEEL_LANGFUSE_AUTHORIZATION": (
                    "Basic cGstbGYteDpzay1sZi14"
                ),
            }
            referenced = (
                skill_root
                / "research-frame-search-with-domain-mechanisms"
                / "references"
                / "claim-calibration.md"
            )
            referenced.write_text(
                referenced.read_text() + "\nunauthorized drift\n"
            )
            with (
                patch(
                    "product.campaign.services.adapter",
                    return_value=ControlledNtm(),
                ),
                patch.dict(environ, target, clear=False),
                patch("product.campaign.services.readback_project_identity"),
            ):
                response = self.client.post(
                    reverse("campaign_launch", args=[campaign.pk, planner.pk])
                )

        self.assertEqual(409, response.status_code, response.content)
        self.assertIn(b"skill package", response.content)

    def test_launch_without_langfuse_configuration_fails_as_a_product_state(
        self,
    ) -> None:
        campaign = self.create_campaign()
        planner = WorkOrder.objects.get(campaign=campaign, protocol="planner")

        with patch.dict(environ, {}, clear=True):
            response = self.client.post(
                reverse("campaign_launch", args=[campaign.pk, planner.pk])
            )

        self.assertEqual(409, response.status_code, response.content)
        self.assertContains(
            response,
            "Langfuse target project is absent or invalid",
            status_code=409,
        )
        self.assertContains(
            response,
            "No Codex session has started",
            status_code=409,
        )
        self.assertEqual(0, campaign.runtime_events.count())
