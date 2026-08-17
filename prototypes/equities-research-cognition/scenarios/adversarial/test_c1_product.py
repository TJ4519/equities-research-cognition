from __future__ import annotations

from copy import deepcopy
from html import unescape
import re

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from product.review.models import AnalystEnrollment, QueueAssignment, ResearchCase
from product.review.policy import CLAIM_LICENSE_RUBRIC


FORBIDDEN_BLIND_CUES = (
    "provisional judgment",
    "comparison judgment",
    "selector route",
    "residual allocation",
    "trace id",
    "agent role",
    "prompt version",
    "otel-native",
    "legacy fixture",
    "engineering",
)


class BlindPacketJourneyTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        users = get_user_model()
        cls.analyst = users.objects.create_user("analyst", password="correct horse battery staple")
        cls.outsider = users.objects.create_user("outsider", password="correct horse battery staple")
        cls.visitor = users.objects.create_user("visitor", password="correct horse battery staple")
        cls.enrollment = AnalystEnrollment.objects.create(
            user=cls.analyst,
            scope_code="equities",
            qualification_basis="fixture-only engineering enrollment",
            attested_by="test governor",
        )
        AnalystEnrollment.objects.create(
            user=cls.outsider,
            scope_code="equities",
            qualification_basis="fixture-only engineering enrollment",
            attested_by="test governor",
        )
        cls.case = ResearchCase.objects.create(
            external_id="legacy-fixture:nvda-concentration-001",
            subject_mode=ResearchCase.SubjectMode.LEGACY_FIXTURE_IMPORT,
            question="Does the cited evidence license broad, unconcentrated end demand?",
            source_identity="NVIDIA Corporation Form 10-Q for the quarter ended April 26, 2026",
            source_url="https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm",
            source_locator="MD&A, Concentration of Revenue",
            exact_passage="three direct customers represented 21%, 17%, and 16% of total revenue",
            context_items=[
                {
                    "source_identity": "NVIDIA Corporation Form 10-Q for the quarter ended April 26, 2026",
                    "source_url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm",
                    "locator": "MD&A, Revenue by Market Platform",
                    "exact_passage": "Hyperscaler revenue increased sequentially and remained at approximately 50% of Data Center revenue, while the remaining 50% came from a continued diversification of customers",
                },
                {
                    "source_identity": "NVIDIA Corporation Form 10-Q for the quarter ended April 26, 2026",
                    "source_url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm",
                    "locator": "MD&A, Concentration of Revenue",
                    "exact_passage": "one AI research and deployment company contributed to a meaningful amount of our revenue",
                },
            ],
            rubric=CLAIM_LICENSE_RUBRIC,
            custody_tree_digest="a" * 64,
            source_artifact_digest="b" * 64,
            evidence_artifact_digest="c" * 64,
            projection_version="test-packet/v1",
        )
        QueueAssignment.objects.create(enrollment=cls.enrollment, case=cls.case)

    def test_anonymous_visitor_receives_no_case_content(self) -> None:
        for url in (reverse("queue"), reverse("case", args=[self.case.pk])):
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertEqual(200, response.status_code)
                body = response.content.decode().lower()
                self.assertIn("sign in", body)
                self.assertNotIn("nvidia", body)
                self.assertNotIn("three direct customers", body)

    def test_server_session_and_enrollment_own_access(self) -> None:
        self.client.force_login(self.visitor)
        self.assertEqual(403, self.client.get(reverse("queue")).status_code)
        self.client.force_login(self.outsider)
        response = self.client.get(
            reverse("case", args=[self.case.pk]),
            {"reviewer_id": self.enrollment.pk, "username": self.analyst.username},
        )
        self.assertEqual(404, response.status_code)

    def test_enrolled_session_sees_complete_cue_free_packet(self) -> None:
        self.client.force_login(self.analyst)
        queue = self.client.get(reverse("queue"))
        self.assertContains(queue, "1 case in your review queue")
        response = self.client.get(reverse("case", args=[self.case.pk]))
        self.assertEqual(200, response.status_code)
        body = unescape(response.content.decode()).lower()
        for required in (
            self.case.question,
            self.case.source_identity,
            self.case.source_url.replace("&", "&amp;"),
            self.case.source_locator,
            self.case.exact_passage,
            "licensed",
            "requires narrowing",
            "reject",
            "ambiguous",
        ):
            self.assertIn(required.lower(), body)
        for item in self.case.context_items:
            self.assertIn(item["source_identity"].lower(), body)
            self.assertIn(item["locator"].lower(), body)
            self.assertIn(item["exact_passage"].lower(), body)
        for cue in FORBIDDEN_BLIND_CUES:
            self.assertNotIn(cue, body)

    def test_get_is_domain_read_only(self) -> None:
        self.client.force_login(self.analyst)
        before = {
            "case": deepcopy(ResearchCase.objects.values().get(pk=self.case.pk)),
            "assignment_count": QueueAssignment.objects.count(),
        }
        response = self.client.get(reverse("case", args=[self.case.pk]))
        self.assertEqual(200, response.status_code)
        after = {
            "case": ResearchCase.objects.values().get(pk=self.case.pk),
            "assignment_count": QueueAssignment.objects.count(),
        }
        self.assertEqual(before, after)

    def test_password_change_invalidates_the_old_session(self) -> None:
        self.client.login(username="analyst", password="correct horse battery staple")
        self.analyst.set_password("new local password")
        self.analyst.save()
        response = self.client.get(reverse("case", args=[self.case.pk]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('case', args=[self.case.pk])}")

    def test_revoked_enrollment_invalidates_an_authenticated_session(self) -> None:
        self.client.force_login(self.analyst)
        AnalystEnrollment.objects.filter(pk=self.enrollment.pk).update(is_active=False)
        self.assertEqual(403, self.client.get(reverse("case", args=[self.case.pk])).status_code)


class CsrfBoundaryTests(TestCase):
    def test_login_rejects_missing_csrf(self) -> None:
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("login"), {"username": "nobody", "password": "bad"})
        self.assertEqual(403, response.status_code)

    def test_csrf_token_from_another_session_is_rejected(self) -> None:
        source = Client(enforce_csrf_checks=True)
        target = Client(enforce_csrf_checks=True)
        login = source.get(reverse("login")).content.decode()
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login).group(1)
        response = target.post(
            reverse("login"),
            {"username": "nobody", "password": "bad", "csrfmiddlewaretoken": token},
        )
        self.assertEqual(403, response.status_code)
