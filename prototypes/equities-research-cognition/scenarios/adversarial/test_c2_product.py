from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import DatabaseError, close_old_connections, connection, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from product.review.models import (
    AnalystEnrollment,
    ExposureEvent,
    FirstPass,
    LineageRecord,
    QueueAssignment,
    ResearchCase,
)
from product.review.policy import CLAIM_LICENSE_RUBRIC
from product.review.transitions import LockRejected, fingerprint, lock_first_pass


def make_case(username: str = "analyst", question: str = "Does the evidence license the claim?") -> tuple[object, AnalystEnrollment, ResearchCase, QueueAssignment]:
    user = get_user_model().objects.create_user(username, password="local-review-password")
    enrollment = AnalystEnrollment.objects.create(
        user=user,
        scope_code="equities",
        qualification_basis="fixture-only engineering enrollment",
        attested_by="test governor",
    )
    case = ResearchCase.objects.create(
        external_id=f"fixture:{username}",
        subject_mode=ResearchCase.SubjectMode.LEGACY_FIXTURE_IMPORT,
        question=question,
        source_identity="Issuer filing",
        source_url="https://example.com/filing",
        source_locator="MD&A",
        exact_passage="Exact passage",
        context_items=[{"source_identity": "Issuer filing", "source_url": "https://example.com/filing", "locator": "Note 1", "exact_passage": "Exact context"}],
        rubric=CLAIM_LICENSE_RUBRIC,
        custody_tree_digest="a" * 64,
        source_artifact_digest="b" * 64,
        evidence_artifact_digest="c" * 64,
        projection_version="test/v1",
    )
    assignment = QueueAssignment.objects.create(enrollment=enrollment, case=case)
    exact = '{"event":"captured"}'
    for sequence, kind in enumerate(("role", "prompt", "tool", "source", "artifact", "claim_transition", "synthesis", "machine_judgment"), 1):
        LineageRecord.objects.create(
            case=case,
            sequence=sequence,
            kind=kind,
            label=f"Exact {kind}",
            availability="exact",
            locator=f"records/{kind}.json",
            content=exact,
            content_digest=sha256(exact.encode()).hexdigest(),
        )
    LineageRecord.objects.create(
        case=case,
        sequence=9,
        kind="skill",
        label="Skill capture",
        availability="missing",
        locator="No skill record captured",
    )
    return user, enrollment, case, assignment


class LockRevealJourneyTests(TestCase):
    def setUp(self) -> None:
        self.user, self.enrollment, self.case, self.assignment = make_case()

    def payload(self, **changes: str) -> dict[str, str]:
        value = {
            "packet_digest": self.case.packet_digest,
            "rubric_digest": self.case.rubric_digest,
            "decision": "requires_narrowing",
            "rationale": "The evidence supports only the narrower direct-customer claim.",
        }
        value.update(changes)
        return value

    def test_no_reveal_or_exposure_exists_before_authenticated_lock(self) -> None:
        self.client.force_login(self.user)
        self.assertEqual(404, self.client.get(reverse("reveal", args=[self.case.pk])).status_code)
        self.assertFalse(FirstPass.objects.exists())
        self.assertFalse(ExposureEvent.objects.exists())

    def test_anonymous_and_wrong_session_cannot_lock_or_reveal(self) -> None:
        response = self.client.post(reverse("lock", args=[self.case.pk]), self.payload())
        self.assertEqual(302, response.status_code)
        outsider = get_user_model().objects.create_user("outsider")
        AnalystEnrollment.objects.create(user=outsider, scope_code="equities", qualification_basis="test", attested_by="test")
        self.client.force_login(outsider)
        self.assertEqual(404, self.client.post(reverse("lock", args=[self.case.pk]), self.payload()).status_code)
        self.assertEqual(404, self.client.get(reverse("reveal", args=[self.case.pk])).status_code)
        self.assertFalse(FirstPass.objects.exists())

    def test_lock_rejects_a_csrf_token_owned_by_another_authenticated_session(self) -> None:
        source = Client(enforce_csrf_checks=True)
        target = Client(enforce_csrf_checks=True)
        source.force_login(self.user)
        target.force_login(self.user)
        page = source.get(reverse("case", args=[self.case.pk])).content.decode()
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page).group(1)
        payload = self.payload(csrfmiddlewaretoken=token)
        response = target.post(reverse("lock", args=[self.case.pk]), payload)
        self.assertEqual(403, response.status_code)
        self.assertFalse(FirstPass.objects.exists())
        self.assertFalse(ExposureEvent.objects.exists())

    def test_stale_packet_or_rubric_rejects_without_any_mutation(self) -> None:
        self.client.force_login(self.user)
        for field in ("packet_digest", "rubric_digest"):
            with self.subTest(field=field):
                response = self.client.post(reverse("lock", args=[self.case.pk]), self.payload(**{field: "0" * 64}))
                self.assertEqual(409, response.status_code)
                self.assertFalse(FirstPass.objects.exists())
                self.assertFalse(ExposureEvent.objects.exists())

    def test_valid_lock_binds_server_session_and_versions_then_reveals_exact_records(self) -> None:
        self.client.force_login(self.user)
        session_key = self.client.session.session_key
        response = self.client.post(
            reverse("lock", args=[self.case.pk]),
            self.payload(author_user_id="999", reviewer_id="999"),
        )
        self.assertRedirects(response, reverse("reveal", args=[self.case.pk]))
        locked = FirstPass.objects.get()
        self.assertEqual(self.user.pk, locked.author_user_id)
        self.assertEqual(fingerprint(session_key), locked.session_fingerprint)
        self.assertNotEqual(session_key, locked.session_fingerprint)
        self.assertEqual(self.case.packet_digest, locked.packet_digest_snapshot)
        self.assertEqual(self.case.rubric_digest, locked.rubric_digest_snapshot)
        self.assertEqual(self.enrollment.pk, locked.reviewer_scope_snapshot["enrollment_id"])
        self.assertTrue(ExposureEvent.objects.filter(first_pass=locked).exists())
        self.assertEqual(self.case.question, locked.packet_snapshot["question"])
        self.assertEqual(9, len(locked.exposure.lineage_snapshot))
        self.assertTrue(all("content" not in record for record in locked.exposure.lineage_snapshot))
        reveal = self.client.get(reverse("reveal", args=[self.case.pk]))
        body = reveal.content.decode()
        for label in ("Agent role", "Prompt", "Skill", "Tool trace", "Source use", "Artifact evolution", "Claim transition", "Synthesis use", "Machine judgment"):
            self.assertIn(label, body)
        self.assertIn("Exact captured record", body)
        self.assertIn("Open exact captured record", body)
        self.assertNotIn('{"event":"captured"}', body)
        self.assertIn("Missing", body)
        self.assertIn("No exact captured content is available", body)
        self.assertIn("not expert-review evidence", body)
        record = self.client.get(reverse("record", args=[self.case.pk, 1]))
        self.assertContains(record, "{&quot;event&quot;:&quot;captured&quot;}")

    def test_exact_record_drilldown_requires_the_locked_assigned_user(self) -> None:
        self.client.force_login(self.user)
        self.client.post(reverse("lock", args=[self.case.pk]), self.payload())
        outsider, _, _, _ = make_case("record-outsider")
        self.client.force_login(outsider)
        self.assertEqual(404, self.client.get(reverse("record", args=[self.case.pk, 1])).status_code)

    def test_resubmission_and_mutation_fail_closed(self) -> None:
        self.client.force_login(self.user)
        self.assertEqual(302, self.client.post(reverse("lock", args=[self.case.pk]), self.payload()).status_code)
        self.assertEqual(409, self.client.post(reverse("lock", args=[self.case.pk]), self.payload()).status_code)
        locked = FirstPass.objects.get()
        locked.rationale = "changed"
        with self.assertRaises(ValidationError):
            locked.save()
        with self.assertRaises(ValidationError):
            FirstPass.objects.filter(pk=locked.pk).update(rationale="changed")
        with self.assertRaises(ValidationError):
            locked.delete()

    def test_database_rejects_base_manager_history_forgery(self) -> None:
        self.client.force_login(self.user)
        self.client.post(reverse("lock", args=[self.case.pk]), self.payload())
        locked = FirstPass.objects.get()
        lineage = LineageRecord.objects.filter(case=self.case).first()
        probes = (
            ("UPDATE review_firstpass SET rationale = %s WHERE id = %s", ["forged", locked.pk]),
            ("UPDATE review_exposureevent SET lineage_digest = %s WHERE first_pass_id = %s", ["0" * 64, locked.pk]),
            ("UPDATE review_lineagerecord SET content = %s WHERE id = %s", ["forged", lineage.pk]),
            ("UPDATE review_researchcase SET question = %s WHERE id = %s", ["forged", self.case.pk]),
            ("UPDATE review_queueassignment SET enrollment_id = %s WHERE id = %s", [999999, self.assignment.pk]),
        )
        for statement, parameters in probes:
            with self.subTest(statement=statement):
                with self.assertRaises(DatabaseError), transaction.atomic(), connection.cursor() as cursor:
                    cursor.execute(statement, parameters)
        locked.refresh_from_db()
        self.case.refresh_from_db()
        lineage.refresh_from_db()
        self.assertNotEqual("forged", locked.rationale)
        self.assertNotEqual("forged", self.case.question)
        self.assertNotEqual("forged", lineage.content)

    def test_restart_session_reconstructs_locked_material_without_writes(self) -> None:
        self.client.force_login(self.user)
        self.client.post(reverse("lock", args=[self.case.pk]), self.payload())
        counts = (FirstPass.objects.count(), ExposureEvent.objects.count(), LineageRecord.objects.count())
        restarted = Client()
        restarted.force_login(self.user)
        response = restarted.get(reverse("reveal", args=[self.case.pk]))
        self.assertContains(response, "The evidence supports only the narrower direct-customer claim")
        self.assertEqual(counts, (FirstPass.objects.count(), ExposureEvent.objects.count(), LineageRecord.objects.count()))


class LineageValidationTests(TestCase):
    def test_exact_and_unavailable_states_cannot_be_mislabeled(self) -> None:
        _, _, case, _ = make_case("lineage")
        with self.assertRaises(ValidationError):
            LineageRecord.objects.create(case=case, sequence=20, kind="skill", label="false exact", availability="exact", locator="x")
        with self.assertRaises(ValidationError):
            LineageRecord.objects.create(case=case, sequence=21, kind="skill", label="false missing", availability="missing", locator="x", content="invented")
        with self.assertRaises(ValidationError):
            LineageRecord.objects.create(case=case, sequence=22, kind="tool", label="stale digest", availability="exact", locator="x", content="captured", content_digest="0" * 64)
        with self.assertRaises(ValidationError):
            LineageRecord.objects.create(case=case, sequence=23, kind="tool", label="empty digest only", availability="digest_only", locator="x")

    def test_unicode_packet_uses_one_canonical_digest_at_lock(self) -> None:
        user, _, case, assignment = make_case("unicode", "Does £100 — or an issuer’s wording — change the claim?")
        locked = lock_first_pass(
            assignment_id=assignment.pk,
            user=user,
            session_key="unicode-session",
            packet_digest=case.packet_digest,
            rubric_digest=case.rubric_digest,
            decision="ambiguous",
            rationale="The Unicode-bearing packet remains version-consistent.",
        )
        self.assertEqual(case.question, locked.packet_snapshot["question"])

class ConcurrentLockTests(TransactionTestCase):
    reset_sequences = True

    def test_two_sessions_cannot_both_lock_the_same_assignment(self) -> None:
        user, _, case, assignment = make_case("concurrent")

        def attempt(session_key: str) -> str:
            close_old_connections()
            try:
                thread_user = get_user_model().objects.get(pk=user.pk)
                lock_first_pass(
                    assignment_id=assignment.pk,
                    user=thread_user,
                    session_key=session_key,
                    packet_digest=case.packet_digest,
                    rubric_digest=case.rubric_digest,
                    decision="licensed",
                    rationale="Independent concurrent submission",
                )
                return "accepted"
            except LockRejected:
                return "rejected"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, ("session-one", "session-two")))
        self.assertEqual(["accepted", "rejected"], sorted(outcomes))
        self.assertEqual(1, FirstPass.objects.count())
        self.assertEqual(1, ExposureEvent.objects.count())
