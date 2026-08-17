from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError, IntegrityError, close_old_connections, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from product.review.models import (
    AnalystEnrollment,
    ConsequenceDecision,
    CurrentCorrection,
    ExposureEvent,
    FirstPass,
    FutureProposal,
    LineageRecord,
    QueueAssignment,
    ResearchCase,
    ReviewCompletion,
    RubricEvalState,
)
from product.review.policy import CLAIM_LICENSE_RUBRIC
from product.review.transitions import (
    CompletionRejected,
    complete_review,
    lock_first_pass,
)


class AtomicThreeConsequenceTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user("c3-analyst")
        enrollment = AnalystEnrollment.objects.create(
            user=self.user, scope_code="equities", qualification_basis="fixture test", attested_by="test"
        )
        case = ResearchCase.objects.create(
            external_id="c3:fixture",
            subject_mode=ResearchCase.SubjectMode.LEGACY_FIXTURE_IMPORT,
            question="Is the inference licensed?",
            source_identity="Issuer filing",
            source_url="https://example.com/source",
            source_locator="MD&A",
            exact_passage="Exact passage",
            context_items=[{"source_identity": "Issuer filing", "source_url": "https://example.com/source", "locator": "Note", "exact_passage": "Context"}],
            rubric=CLAIM_LICENSE_RUBRIC,
            custody_tree_digest="a" * 64,
            source_artifact_digest="b" * 64,
            evidence_artifact_digest="c" * 64,
            projection_version="c3-test/v1",
        )
        LineageRecord.objects.create(
            case=case, sequence=1, kind="skill", label="Skill capture", availability="missing", locator="not captured"
        )
        assignment = QueueAssignment.objects.create(enrollment=enrollment, case=case)
        self.client.force_login(self.user)
        self.session_key = self.client.session.session_key
        self.first_pass = lock_first_pass(
            assignment_id=assignment.pk,
            user=self.user,
            session_key=self.session_key,
            packet_digest=case.packet_digest,
            rubric_digest=case.rubric_digest,
            decision="requires_narrowing",
            rationale="The inference exceeds the evidence.",
        )

    def request(self) -> dict[str, str]:
        return {
            "first_pass_id": str(self.first_pass.pk),
            "packet_digest": self.first_pass.packet_digest_snapshot,
            "lineage_digest": self.first_pass.exposure.lineage_digest,
            "adjudicated_decision": "requires_narrowing",
            "diagnosis": "The machine did not preserve the direct-customer versus end-demand distinction.",
            "corrected_judgment": "The filing licenses a one-quarter direct-customer concentration claim only.",
            "current_action": "apply_current_correction",
            "current_payload": "Narrow the current report to direct-customer concentration in this quarter.",
            "current_rationale": "The published claim otherwise exceeds the evidence.",
            "rubric_action": "create_eval_candidate",
            "rubric_payload": "Evaluate whether direct-customer and end-demand concentration remain distinct.",
            "rubric_rationale": "This is a recurring scope discriminator.",
            "future_action": "propose_workflow_change",
            "future_payload": "Require a customer-layer scope check before licensing demand-breadth claims.",
            "future_reversibility": "Remove the check and compare protected later cases against the prior workflow.",
            "future_rationale": "The failure arose before synthesis and may recur.",
        }

    def test_third_lane_failure_rolls_back_diagnosis_decisions_and_projections(self) -> None:
        from product.review import transitions

        original = transitions._create_decision
        calls = 0

        def fail_third(*args: object, **kwargs: object):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise RuntimeError("injected third-lane failure")
            return original(*args, **kwargs)

        with patch("product.review.transitions._create_decision", side_effect=fail_third):
            with self.assertRaises(RuntimeError):
                complete_review(user=self.user, session_key=self.session_key, case_id=self.first_pass.assignment.case_id, data=self.request())
        self.assertEqual(0, ReviewCompletion.objects.count())
        self.assertEqual(0, ConsequenceDecision.objects.count())
        self.assertEqual(0, CurrentCorrection.objects.count())
        self.assertEqual(0, RubricEvalState.objects.count())
        self.assertEqual(0, FutureProposal.objects.count())

    def test_invalid_lane_combination_fails_before_the_first_write(self) -> None:
        request = self.request()
        request["current_action"] = "reject_current_correction"
        with self.assertRaises(CompletionRejected):
            complete_review(user=self.user, session_key=self.session_key, case_id=self.first_pass.assignment.case_id, data=request)
        self.assertEqual(0, ReviewCompletion.objects.count())
        self.assertEqual(0, ConsequenceDecision.objects.count())

    def test_every_family_validates_before_writes_and_targets_are_server_derived(self) -> None:
        invalid = (
            {"current_action": "invented", "current_payload": ""},
            {"rubric_action": "create_eval_candidate", "rubric_payload": ""},
            {"future_action": "reject_future_change", "future_payload": "invented", "future_reversibility": ""},
            {"future_action": "propose_prompt_change", "future_reversibility": ""},
        )
        for changes in invalid:
            with self.subTest(changes=changes):
                request = self.request()
                request.update(changes)
                with self.assertRaises(CompletionRejected):
                    complete_review(user=self.user, session_key=self.session_key, case_id=self.first_pass.assignment.case_id, data=request)
                self.assertFalse(ReviewCompletion.objects.exists())
        request = self.request()
        request.update({"current_target": "future_proposal_quarantine", "rubric_target": "current_report_state"})
        completion = complete_review(user=self.user, session_key=self.session_key, case_id=self.first_pass.assignment.case_id, data=request)
        self.assertEqual("current_report_state", completion.decisions.get(family="current").target)
        self.assertEqual("protected_eval_candidate_pool", completion.decisions.get(family="rubric").target)

    def test_three_independent_decisions_materialize_only_their_accepted_effects(self) -> None:
        completion = complete_review(user=self.user, session_key=self.session_key, case_id=self.first_pass.assignment.case_id, data=self.request())
        self.assertEqual(3, completion.decisions.count())
        self.assertEqual(
            {"current": "current_report_state", "rubric": "protected_eval_candidate_pool", "future": "future_proposal_quarantine"},
            {decision.family: decision.target for decision in completion.decisions.all()},
        )
        self.assertIn("Narrow the current report", completion.current_correction.corrected_state)
        self.assertEqual("eval", completion.rubric_eval_state.state_type)
        self.assertEqual("workflow", completion.future_proposal.intervention_type)
        self.assertEqual("inactive_quarantined", completion.future_proposal.status)

    def test_reject_defer_and_absent_lanes_create_no_effect_state(self) -> None:
        request = self.request()
        request.update({
            "current_action": "reject_current_correction",
            "current_payload": "",
            "rubric_action": "absent_rubric_or_eval",
            "rubric_payload": "",
            "future_action": "defer_future_change",
            "future_payload": "",
            "future_reversibility": "",
        })
        completion = complete_review(user=self.user, session_key=self.session_key, case_id=self.first_pass.assignment.case_id, data=request)
        self.assertEqual(3, completion.decisions.count())
        self.assertFalse(CurrentCorrection.objects.exists())
        self.assertFalse(RubricEvalState.objects.exists())
        self.assertFalse(FutureProposal.objects.exists())
    def test_http_completion_is_session_authored_stale_safe_and_restart_stable(self) -> None:
        self.client.force_login(self.user)
        reveal = self.client.get(reverse("reveal", args=[self.first_pass.assignment.case_id]))
        self.assertContains(reveal, "Diagnose and govern consequences")
        stale = self.request()
        stale["lineage_digest"] = "0" * 64
        self.assertEqual(409, self.client.post(reverse("complete", args=[self.first_pass.assignment.case_id]), stale).status_code)
        self.assertFalse(ReviewCompletion.objects.exists())
        response = self.client.post(reverse("complete", args=[self.first_pass.assignment.case_id]), self.request())
        self.assertRedirects(response, reverse("completed", args=[self.first_pass.assignment.case_id]))
        self.assertEqual(409, self.client.post(reverse("complete", args=[self.first_pass.assignment.case_id]), self.request()).status_code)
        completion = ReviewCompletion.objects.get()
        self.assertEqual(self.user.pk, completion.author_user_id)
        self.assertEqual(self.first_pass.session_fingerprint, completion.session_fingerprint)
        counts = (ReviewCompletion.objects.count(), ConsequenceDecision.objects.count(), CurrentCorrection.objects.count(), RubricEvalState.objects.count(), FutureProposal.objects.count())
        restarted = Client()
        restarted.force_login(self.user)
        page = restarted.get(reverse("completed", args=[self.first_pass.assignment.case_id]))
        for text in (
            "The machine did not preserve",
            "current_report_state",
            "protected_eval_candidate_pool",
            "future_proposal_quarantine",
            "Inactive and quarantined",
            "not expert-review evidence",
        ):
            self.assertContains(page, text)
        self.assertEqual(counts, (ReviewCompletion.objects.count(), ConsequenceDecision.objects.count(), CurrentCorrection.objects.count(), RubricEvalState.objects.count(), FutureProposal.objects.count()))

    def test_different_session_cannot_complete_the_locked_review(self) -> None:
        with self.assertRaises(CompletionRejected):
            complete_review(
                user=self.user, session_key="replacement-session",
                case_id=self.first_pass.assignment.case_id, data=self.request(),
            )
        replacement = Client()
        replacement.force_login(self.user)
        self.assertEqual(
            409,
            replacement.post(
                reverse("complete", args=[self.first_pass.assignment.case_id]),
                self.request(),
            ).status_code,
        )
        self.assertFalse(ReviewCompletion.objects.exists())

    def test_different_enrolled_user_cannot_complete_or_read_review(self) -> None:
        outsider = get_user_model().objects.create_user("c3-outsider")
        AnalystEnrollment.objects.create(user=outsider, scope_code="equities", qualification_basis="test", attested_by="test")
        self.client.force_login(outsider)
        case_id = self.first_pass.assignment.case_id
        self.assertEqual(404, self.client.post(reverse("complete", args=[case_id]), self.request()).status_code)
        self.assertEqual(404, self.client.get(reverse("completed", args=[case_id])).status_code)
        self.assertFalse(ReviewCompletion.objects.exists())

    def test_route_case_and_csrf_session_cannot_be_confused(self) -> None:
        original_case = self.first_pass.assignment.case
        enrollment = self.first_pass.assignment.enrollment
        other_case = ResearchCase.objects.create(
            external_id="c3:other",
            subject_mode=original_case.subject_mode,
            question="Other case",
            source_identity=original_case.source_identity,
            source_url=original_case.source_url,
            source_locator=original_case.source_locator,
            exact_passage=original_case.exact_passage,
            context_items=original_case.context_items,
            rubric=original_case.rubric,
            custody_tree_digest="d" * 64,
            source_artifact_digest="e" * 64,
            evidence_artifact_digest="f" * 64,
            projection_version="c3-test/v1",
        )
        other_assignment = QueueAssignment.objects.create(enrollment=enrollment, case=other_case)
        other_first_pass = lock_first_pass(
            assignment_id=other_assignment.pk, user=self.user, session_key="other",
            packet_digest=other_case.packet_digest, rubric_digest=other_case.rubric_digest,
            decision="licensed", rationale="Other first pass",
        )
        confused = self.request()
        confused.update({
            "first_pass_id": str(other_first_pass.pk),
            "packet_digest": other_first_pass.packet_digest_snapshot,
            "lineage_digest": other_first_pass.exposure.lineage_digest,
        })
        self.client.force_login(self.user)
        self.assertEqual(409, self.client.post(reverse("complete", args=[original_case.pk]), confused).status_code)
        self.assertFalse(ReviewCompletion.objects.exists())

        source = Client(enforce_csrf_checks=True)
        target = Client(enforce_csrf_checks=True)
        source.force_login(self.user)
        target.force_login(self.user)
        page = source.get(reverse("reveal", args=[original_case.pk])).content.decode()
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page).group(1)
        csrf_confused = self.request()
        csrf_confused["csrfmiddlewaretoken"] = token
        self.assertEqual(403, target.post(reverse("complete", args=[original_case.pk]), csrf_confused).status_code)
        self.assertFalse(ReviewCompletion.objects.exists())

    def test_completion_history_rejects_base_manager_mutation(self) -> None:
        completion = complete_review(user=self.user, session_key=self.session_key, case_id=self.first_pass.assignment.case_id, data=self.request())
        probes = (
            lambda: ReviewCompletion._base_manager.filter(pk=completion.pk).update(diagnosis="forged"),
            lambda: ConsequenceDecision._base_manager.filter(completion=completion).update(target="forged"),
            lambda: CurrentCorrection._base_manager.filter(completion=completion).update(corrected_state="forged"),
            lambda: RubricEvalState._base_manager.filter(completion=completion).update(proposed_state="forged"),
            lambda: FutureProposal._base_manager.filter(completion=completion).update(status="active"),
        )
        for probe in probes:
            with self.assertRaises(DatabaseError), transaction.atomic():
                probe()
        completion.refresh_from_db()
        self.assertNotEqual("forged", completion.diagnosis)
        self.assertEqual("inactive_quarantined", FutureProposal.objects.get().status)

    def test_postgresql_rejects_forged_authority_and_active_future_rows(self) -> None:
        request = self.request()
        request.update({
            "current_action": "reject_current_correction", "current_payload": "",
            "rubric_action": "absent_rubric_or_eval", "rubric_payload": "",
            "future_action": "absent_future_change", "future_payload": "", "future_reversibility": "",
        })
        completion = complete_review(user=self.user, session_key=self.session_key, case_id=self.first_pass.assignment.case_id, data=request)
        invalid_rows = (
            lambda: ConsequenceDecision._base_manager.bulk_create([ConsequenceDecision(completion=completion, family="forged", action="activate_future", target="current_report_state", rationale="forged")]),
            lambda: RubricEvalState._base_manager.bulk_create([RubricEvalState(completion=completion, state_type="authority", proposed_state="forged")]),
            lambda: FutureProposal._base_manager.bulk_create([FutureProposal(completion=completion, intervention_type="workflow", proposed_change="forged", reversibility_plan="none", status="active")]),
        )
        for insert in invalid_rows:
            with self.assertRaises(IntegrityError), transaction.atomic():
                insert()
        self.assertFalse(RubricEvalState.objects.exists())
        self.assertFalse(FutureProposal.objects.exists())


class ConcurrentCompletionTests(TransactionTestCase):
    def test_two_sessions_cannot_both_complete_one_review(self) -> None:
        user = get_user_model().objects.create_user("c3-concurrent")
        enrollment = AnalystEnrollment.objects.create(user=user, scope_code="equities", qualification_basis="test", attested_by="test")
        case = ResearchCase.objects.create(
            external_id="c3:concurrent", subject_mode=ResearchCase.SubjectMode.LEGACY_FIXTURE_IMPORT,
            question="Concurrent case", source_identity="Filing", source_url="https://example.com/concurrent",
            source_locator="MD&A", exact_passage="Passage", context_items=[], rubric=CLAIM_LICENSE_RUBRIC,
            custody_tree_digest="1" * 64, source_artifact_digest="2" * 64,
            evidence_artifact_digest="3" * 64, projection_version="test/v1",
        )
        assignment = QueueAssignment.objects.create(enrollment=enrollment, case=case)
        first_pass = lock_first_pass(
            assignment_id=assignment.pk, user=user, session_key="lock", packet_digest=case.packet_digest,
            rubric_digest=case.rubric_digest, decision="licensed", rationale="Concurrent first pass",
        )
        data = {
            "first_pass_id": str(first_pass.pk), "packet_digest": first_pass.packet_digest_snapshot,
            "lineage_digest": first_pass.exposure.lineage_digest, "adjudicated_decision": "licensed",
            "diagnosis": "No residual found.", "corrected_judgment": "The bounded claim is licensed.",
            "current_action": "absent_current_correction", "current_payload": "", "current_rationale": "No current change.",
            "rubric_action": "absent_rubric_or_eval", "rubric_payload": "", "rubric_rationale": "No rubric change.",
            "future_action": "absent_future_change", "future_payload": "", "future_reversibility": "", "future_rationale": "No future change.",
        }

        def attempt(session_key: str) -> str:
            close_old_connections()
            try:
                thread_user = get_user_model().objects.get(pk=user.pk)
                complete_review(user=thread_user, session_key=session_key, case_id=case.pk, data=data)
                return "accepted"
            except CompletionRejected:
                return "rejected"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, ("lock", "lock")))
        self.assertEqual(["accepted", "rejected"], sorted(outcomes))
        self.assertEqual(1, ReviewCompletion.objects.count())
        self.assertEqual(3, ConsequenceDecision.objects.count())
