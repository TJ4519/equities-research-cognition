from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from product.campaign.model_change.adapter import case_a_profile
from product.campaign.model_change.services import (
    CandidateService,
    InvalidationService,
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
        self.assertContains(response, "The original workbook is unchanged")
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
        _, _, passed = InvalidationService.repair_wrong_source(
            self.owner, blocked, annual
        )
        CandidateService.create(
            passed, self.episode.starting_artifact, case_a_profile()
        )
        response = self.client.get(self.url)
        self.assertContains(response, "36900 → 37378.00000000 USDm")
        self.assertContains(response, "Model!B6")
        self.assertContains(response, "Valuation!B5")
        self.assertContains(response, "Simulate named use")
        self.assertContains(response, "Reject")
        self.assertContains(response, "Request rework")
        self.assertContains(response, "Formula errors")

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
