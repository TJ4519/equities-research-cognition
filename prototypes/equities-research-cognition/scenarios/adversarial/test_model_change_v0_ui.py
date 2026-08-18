from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from unittest.mock import patch

from product.campaign import services as campaign_services
from product.campaign.model_change.adapter import AdapterRejected, case_a_profile
from product.campaign.model_change.services import (
    ModelChangeRejected,
    OutcomeService,
    ProjectionService,
    RepairService,
)
from product.campaign.models import SourceDocumentVersion

from scenarios.adversarial.test_model_change_v0_services import CaseAFixtureMixin


class ModelChangeUiTests(CaseAFixtureMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_login(self.owner)
        self.url = reverse(
            "model_change_episode",
            kwargs={
                "job_id": self.episode.job_id,
                "episode_id": self.episode.pk,
            },
        )

    def test_owner_can_resume_and_complete_distinct_meaning_and_method_actions(self) -> None:
        response = self.client.get(self.url)
        self.assertContains(response, "Confirm the target meaning")
        self.assertNotContains(response, "Run this work")
        response = self.client.post(
            reverse(
                "model_change_confirm_meaning",
                kwargs={"job_id": self.episode.job_id, "episode_id": self.episode.pk},
            ),
            {"confirmed": "on"},
        )
        self.assertEqual(302, response.status_code)
        response = self.client.get(self.url)
        self.assertContains(response, "Authorise the method and source rule")
        self.assertNotContains(response, "Run this work")
        response = self.client.post(
            reverse(
                "model_change_authorize_method",
                kwargs={"job_id": self.episode.job_id, "episode_id": self.episode.pk},
            ),
            {"authorized": "on"},
        )
        self.assertEqual(302, response.status_code)
        response = self.client.get(self.url)
        self.assertContains(response, "Run this work")

    def test_source_exception_is_ordinary_language_and_original_is_unchanged(self) -> None:
        _, _, blocked = self.blocked_path()
        response = self.client.get(self.url)
        self.assertContains(
            response, "The proposed source does not fit this annual target"
        )
        self.assertContains(response, "The original workbook remains unchanged")
        self.assertContains(
            response, "Create a candidate using the filed annual report"
        )
        for forbidden in (
            "BLOCK_WRONG_DOCUMENT_CLASS",
            "model-change-proposal/v0",
            "logical_role_id",
            "trace_id",
            "Casebook",
        ):
            self.assertNotContains(response, forbidden)
        self.assertEqual(0, blocked.candidate_artifacts.count())

    def test_candidate_page_shows_delta_two_consequences_and_three_bounded_choices(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        repair = RepairService.create_candidate_using_filed_report(
            self.owner,
            blocked,
            annual,
            case_a_profile(),
            "candidate-page-test",
        )
        response = self.client.get(self.url)
        self.assertContains(response, "36900 → 37378.00000000 USDm")
        self.assertContains(response, "Model!B6")
        self.assertContains(response, "Valuation!B5")
        self.assertContains(response, "Simulate named use")
        self.assertContains(response, "Reject")
        self.assertContains(response, "Request rework")
        self.assertContains(response, "Formula errors")
        annual = repair.replacement_proposal.source_assertion
        for required in (
            annual.document_version.identity["issuer"],
            annual.document_version.identity["filing_date"],
            annual.document_version.artifact.filename,
            annual.locator,
            str(annual.value),
            annual.unit,
            self.episode.starting_artifact.filename,
            self.episode.starting_artifact.digest,
            repair.candidate.filename,
            repair.candidate.digest,
            self.episode.named_use,
            repair.calculation_receipt.adapter_profile,
            repair.calculation_receipt.engine_identity,
            repair.calculation_receipt.engine_version,
            "The original workbook remains unchanged",
            "same numeric value",
        ):
            self.assertContains(response, required)
        for forbidden in (
            "USE_CANDIDATE",
            "ready to rely on",
            "approved",
            "BLOCK_WRONG_DOCUMENT_CLASS",
            "source_assertion_id",
            "model-change-proposal/v0",
            "NTM",
            "trace_id",
            "Casebook",
        ):
            self.assertNotContains(response, forbidden)

    def test_calculation_failure_is_bounded_and_retryable_after_restart(self) -> None:
        _, _, blocked = self.blocked_path()
        state = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        repair_url = reverse(
            "model_change_use_filed_report",
            kwargs={"job_id": self.episode.job_id, "episode_id": self.episode.pk},
        )
        with patch(
            "product.campaign.model_change.services.adapter.apply",
            side_effect=AdapterRejected("FORCED_APPLY_FAILURE", "forced failure"),
        ):
            response = self.client.post(
                repair_url,
                {"idempotency_key": state["next_action_key"]},
            )
        self.assertEqual(409, response.status_code)
        self.assertContains(
            response,
            "The candidate could not be calculated safely",
            status_code=409,
        )
        self.assertContains(response, "Retry creating the candidate", status_code=409)
        self.assertEqual(0, blocked.amendments.count())
        self.assertEqual(0, self.episode.campaign.input_artifacts.filter(role="candidate").count())
        restarted = self.client.get(self.url)
        self.assertContains(restarted, "Retry creating the candidate")
        retry_state = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        response = self.client.post(
            repair_url,
            {"idempotency_key": retry_state["next_action_key"]},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, self.episode.campaign.input_artifacts.filter(role="candidate").count())

    def test_runtime_failure_and_worker_refusal_show_one_ordinary_retry_action(self) -> None:
        order = self.compile_order()
        run_url = reverse(
            "model_change_run",
            kwargs={"job_id": self.episode.job_id, "episode_id": self.episode.pk},
        )
        with patch(
            "product.campaign.model_change.services.campaign_services.launch_role",
            side_effect=campaign_services.CampaignRejected("forced launch failure"),
        ):
            response = self.client.post(run_url, {})
        self.assertEqual(302, response.status_code)
        restarted = self.client.get(self.url)
        self.assertContains(restarted, "The work could not be completed safely")
        self.assertContains(restarted, "Retry this work")
        self.assertNotContains(restarted, "RUNTIME_FAILED")
        with patch(
            "product.campaign.model_change.services.campaign_services.launch_role",
            side_effect=campaign_services.CampaignRejected("forced successor failure"),
        ):
            response = self.client.post(run_url, {})
        self.assertEqual(302, response.status_code)
        self.assertEqual(2, self.episode.campaign.work_orders.filter(protocol="model_change_v0").count())

        latest_order = self.episode.campaign.work_orders.order_by(
            "created_at", "pk"
        ).last()
        refusal = OutcomeService.record_worker_refusal(
            latest_order,
            {
                "schema": "model-change-refusal/v0",
                "episode_id": str(self.episode.pk),
                "reason": "The captured sources do not support a bounded proposal.",
            },
        )
        restarted = self.client.get(self.url)
        self.assertContains(restarted, refusal.technical_details["reason"])
        self.assertContains(restarted, "Retry this work")

    def test_cross_owner_episode_returns_not_found(self) -> None:
        stranger = get_user_model().objects.create_user(username="ui-stranger")
        self.client.force_login(stranger)
        self.assertEqual(404, self.client.get(self.url).status_code)

    def test_jobs_entry_lists_only_owned_seeded_job(self) -> None:
        response = self.client.get(reverse("model_change_jobs"))
        self.assertContains(response, "Synthetic Micron Technology, Inc.")
        self.assertContains(response, self.episode.starting_artifact.filename)

    @override_settings(MODEL_CHANGE_V0=False)
    def test_feature_flag_off_makes_new_route_dormant(self) -> None:
        self.assertEqual(404, self.client.get(reverse("model_change_jobs")).status_code)
        self.assertEqual(404, self.client.get(self.url).status_code)

    def test_feature_flag_rollback_preserves_block_and_prevents_new_repair(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        before = (
            self.episode.amendments.count(),
            self.episode.model_change_proposals.count(),
            self.episode.campaign.input_artifacts.filter(role="candidate").count(),
        )
        with override_settings(MODEL_CHANGE_V0=False):
            self.assertEqual(404, self.client.get(self.url).status_code)
            with self.assertRaisesRegex(ModelChangeRejected, "unavailable"):
                RepairService.create_candidate_using_filed_report(
                    self.owner,
                    blocked,
                    annual,
                    case_a_profile(),
                    "disabled-repair",
                )
        self.assertEqual(
            before,
            (
                self.episode.amendments.count(),
                self.episode.model_change_proposals.count(),
                self.episode.campaign.input_artifacts.filter(role="candidate").count(),
            ),
        )
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        self.assertEqual(blocked.pk, resumed["decision"].pk)
