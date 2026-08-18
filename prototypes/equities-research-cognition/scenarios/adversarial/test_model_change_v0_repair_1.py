from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from threading import Barrier
import uuid
from unittest.mock import patch

from django.db import DatabaseError, close_old_connections, connection, transaction
from django.test import TransactionTestCase

from product.campaign.model_change.adapter import AdapterRejected, case_a_profile
from product.campaign.model_change.services import (
    CandidateService,
    EvidenceService,
    InvalidationService,
    ModelChangeRejected,
    ProjectionService,
    ProposalParser,
    RepairService,
    _repair_key,
)
from product.campaign.models import (
    AdmissibilityDecision,
    ArtifactVersion,
    CalculationReceipt,
    InvalidationEvent,
    ModelChangeOutcome,
    ModelChangeProposal,
    SourceAssertion,
    SourceDocumentVersion,
)

from scenarios.adversarial.test_model_change_v0_services import CaseAFixtureMixin


class ModelChangeRepairAuthorityTests(CaseAFixtureMixin, TransactionTestCase):
    reset_sequences = True

    def _insert_candidate(self, *, decision, content=b"hostile-candidate"):
        candidate_id = uuid.uuid4()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO campaign_artifactversion
                  (id, campaign_id, role, filename, media_type, content,
                   digest, parent_id, candidate_from_pass_id, created_at)
                VALUES (%s, %s, 'candidate', %s, %s, %s, %s, %s, %s, NOW())
                """,
                [
                    candidate_id,
                    self.episode.campaign_id,
                    "hostile.xlsx",
                    self.episode.starting_artifact.media_type,
                    content,
                    sha256(content).hexdigest(),
                    self.episode.starting_artifact_id,
                    decision.pk,
                ],
            )
        return candidate_id, sha256(content).hexdigest()

    def _insert_receipt(
        self,
        *,
        candidate_id,
        candidate_digest,
        pass_decision,
        episode_id=None,
        manifest_id=None,
        pass_decision_id=None,
        receipt_candidate_id=None,
        closure_digest=None,
        input_digest=None,
        output_digest=None,
        formula_errors="[]",
    ):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO campaign_calculationreceipt
                  (id, episode_id, candidate_id, pass_decision_id, manifest_id,
                   adapter_version, adapter_profile, engine_identity,
                   engine_version, timeout_seconds, environment,
                   operation_receipt, input_digest, output_digest,
                   consequences, warnings, formula_errors, closure_digest,
                   digest, created_at)
                VALUES
                  (%s, %s, %s, %s, %s, 'hostile-adapter/v1', 'hostile-profile',
                   'hostile-engine', '1', 30, '{}'::jsonb, '{}'::jsonb,
                   %s, %s, '[{},{}]'::jsonb, '[]'::jsonb, %s::jsonb,
                   %s, %s, NOW())
                """,
                [
                    uuid.uuid4(),
                    episode_id or self.episode.pk,
                    receipt_candidate_id or candidate_id,
                    pass_decision_id or pass_decision.pk,
                    manifest_id or pass_decision.proposal.manifest_id,
                    input_digest or self.episode.starting_artifact.digest,
                    output_digest or candidate_digest,
                    formula_errors,
                    closure_digest or pass_decision.closure_digest,
                    uuid.uuid4().hex * 2,
                ],
            )

    def test_postgresql_recomputes_decision_and_candidate_authority(self) -> None:
        order, _, blocked = self.blocked_path()
        self.assertEqual("BLOCK_WRONG_DOCUMENT_CLASS", blocked.reason_code)
        attacker_proposal = ProposalParser.parse(self.worker_value(order), order.packet)
        for validator, outcome, reason, closure in (
            (
                "model-change-admissibility/v1",
                "PASS",
                "PASS_EXACT_CLOSURE",
                attacker_proposal.closure_digest,
            ),
            (
                "attacker/v0",
                "BLOCK",
                "BLOCK_WRONG_DOCUMENT_CLASS",
                attacker_proposal.closure_digest,
            ),
            (
                "model-change-admissibility/v1",
                "BLOCK",
                "ATTACKER_FALSE_REASON",
                attacker_proposal.closure_digest,
            ),
            (
                "model-change-admissibility/v1",
                "BLOCK",
                "BLOCK_WRONG_DOCUMENT_CLASS",
                "0" * 64,
            ),
        ):
            with self.assertRaises(DatabaseError), transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO campaign_admissibilitydecision
                          (id, proposal_id, validator_version, outcome, reason_code,
                           closure_digest, digest, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        """,
                        [
                            uuid.uuid4(),
                            attacker_proposal.pk,
                            validator,
                            outcome,
                            reason,
                            closure,
                            uuid.uuid4().hex * 2,
                        ],
                    )
        with self.assertRaises(DatabaseError), transaction.atomic():
            self._insert_candidate(decision=blocked)
        self.assertEqual(
            0, ArtifactVersion.objects.filter(role=ArtifactVersion.Role.CANDIDATE).count()
        )

    def test_direct_sql_stale_proposal_cannot_acquire_decision_authority(self) -> None:
        order = self.compile_order()
        proposal = ProposalParser.parse(self.worker_value(order), order.packet)
        InvalidationService.amend(
            self.owner,
            self.object,
            {"description": "A later attributed synthetic meaning"},
        )
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO campaign_admissibilitydecision
                      (id, proposal_id, validator_version, outcome, reason_code,
                       closure_digest, digest, created_at)
                    VALUES (%s, %s, 'model-change-admissibility/v1', 'PASS',
                            'PASS_EXACT_CLOSURE', %s, %s, NOW())
                    """,
                    [
                        uuid.uuid4(),
                        proposal.pk,
                        proposal.closure_digest,
                        uuid.uuid4().hex * 2,
                    ],
                )

    def test_receipt_guard_rejects_every_mismatched_custody_field(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        profile_id = case_a_profile()["profile_id"]
        idempotency_key = "receipt-custody"
        repair_key = _repair_key(
            blocked=blocked,
            annual_assertion=annual,
            actor=self.owner,
            adapter_profile=profile_id,
            idempotency_key=idempotency_key,
        )
        _, _, passed = InvalidationService._repair_wrong_source(
            self.owner,
            blocked,
            annual,
            repair_key=repair_key,
            adapter_profile=profile_id,
            idempotency_key=idempotency_key,
        )
        attacks = (
            {"pass_decision_id": blocked.pk},
            {"manifest_id": uuid.uuid4()},
            {"receipt_candidate_id": uuid.uuid4()},
            {"episode_id": uuid.uuid4()},
            {"closure_digest": "0" * 64},
            {"input_digest": "1" * 64},
            {"output_digest": "2" * 64},
            {"formula_errors": '["#VALUE!"]'},
        )
        for index, attack in enumerate(attacks):
            with self.subTest(attack=attack), self.assertRaises(DatabaseError):
                with transaction.atomic():
                    candidate_id, candidate_digest = self._insert_candidate(
                        decision=passed,
                        content=f"hostile-receipt-{index}".encode(),
                    )
                    self._insert_receipt(
                        candidate_id=candidate_id,
                        candidate_digest=candidate_digest,
                        pass_decision=passed,
                        **attack,
                    )
        self.assertEqual(
            0, ArtifactVersion.objects.filter(role=ArtifactVersion.Role.CANDIDATE).count()
        )

    def test_candidate_without_matching_receipt_fails_at_commit(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        profile_id = case_a_profile()["profile_id"]
        idempotency_key = "orphan-candidate-attack"
        repair_key = _repair_key(
            blocked=blocked,
            annual_assertion=annual,
            actor=self.owner,
            adapter_profile=profile_id,
            idempotency_key=idempotency_key,
        )
        _, _, passed = InvalidationService._repair_wrong_source(
            self.owner,
            blocked,
            annual,
            repair_key=repair_key,
            adapter_profile=profile_id,
            idempotency_key=idempotency_key,
        )
        self.assertEqual(AdmissibilityDecision.Outcome.PASS, passed.outcome)
        with self.assertRaises(DatabaseError), transaction.atomic():
            self._insert_candidate(decision=passed)
        self.assertEqual(
            0, ArtifactVersion.objects.filter(role=ArtifactVersion.Role.CANDIDATE).count()
        )

    def test_sequential_repair_and_candidate_retry_return_one_exact_chain(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        first = RepairService.create_candidate_using_filed_report(
            self.owner,
            blocked,
            annual,
            case_a_profile(),
            "sequential-idempotency",
        )
        second = RepairService.create_candidate_using_filed_report(
            self.owner,
            blocked,
            annual,
            case_a_profile(),
            "sequential-idempotency",
        )
        duplicate_candidate = CandidateService.create(
            first.pass_decision,
            self.episode.starting_artifact,
            case_a_profile(),
        )
        self.assertEqual("created", first.created_or_existing)
        self.assertEqual("existing", second.created_or_existing)
        self.assertEqual(first.amendment.pk, second.amendment.pk)
        self.assertEqual(first.replacement_proposal.pk, second.replacement_proposal.pk)
        self.assertEqual(first.pass_decision.pk, second.pass_decision.pk)
        self.assertEqual(first.candidate.pk, second.candidate.pk)
        self.assertEqual(first.calculation_receipt.pk, second.calculation_receipt.pk)
        self.assertEqual(first.candidate.pk, duplicate_candidate[0].pk)
        self.assertEqual(first.calculation_receipt.pk, duplicate_candidate[2].pk)
        self.assertEqual(1, blocked.amendments.count())
        self.assertEqual(1, ModelChangeProposal.objects.filter(parent=blocked.proposal).count())
        self.assertEqual(1, ArtifactVersion.objects.filter(role="candidate").count())
        self.assertEqual(1, CalculationReceipt.objects.count())
        with self.assertRaises(DatabaseError), transaction.atomic():
            self._insert_candidate(
                decision=first.pass_decision,
                content=b"duplicate-candidate-for-one-pass",
            )
        for statement, identity in (
            (
                "UPDATE campaign_amendment SET rationale = 'forged' WHERE id = %s",
                first.amendment.pk,
            ),
            (
                "DELETE FROM campaign_modelchangeproposal WHERE id = %s",
                first.replacement_proposal.pk,
            ),
        ):
            with self.assertRaises(DatabaseError), transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(statement, [identity])
        alternate_annual = EvidenceService.assert_value(
            annual.document_version,
            f"{annual.locator}; hostile alternate locator",
            format(annual.value.normalize(), "f"),
            annual.dimensions,
        )
        conflicting_profile = dict(case_a_profile())
        conflicting_profile["profile_id"] = "hostile-conflicting-profile"
        for conflicting_assertion, profile, key in (
            (annual, case_a_profile(), "conflicting-idempotency"),
            (annual, conflicting_profile, "sequential-idempotency"),
            (alternate_annual, case_a_profile(), "sequential-idempotency"),
        ):
            with self.assertRaisesRegex(
                ModelChangeRejected, "different filed-report repair"
            ):
                RepairService.create_candidate_using_filed_report(
                    self.owner,
                    blocked,
                    conflicting_assertion,
                    profile,
                    key,
                )

    def test_stale_or_invalidated_block_cannot_be_repaired(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        _, replacement_object, _ = InvalidationService.amend(
            self.owner,
            self.object,
            {"description": "A later attributed meaning"},
        )
        with self.assertRaisesRegex(ModelChangeRejected, "no longer current"):
            RepairService.create_candidate_using_filed_report(
                self.owner,
                blocked,
                annual,
                case_a_profile(),
                "stale-block",
            )
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        self.assertEqual(replacement_object.pk, resumed["current_object"].pk)
        self.assertIsNone(resumed["decision"])

    def test_concurrent_identical_repairs_converge_on_one_chain(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        barrier = Barrier(2)

        def repair_once():
            close_old_connections()
            try:
                local_block = AdmissibilityDecision.objects.get(pk=blocked.pk)
                local_annual = SourceAssertion.objects.select_related(
                    "document_version"
                ).get(pk=annual.pk)
                local_owner = local_block.proposal.episode.job.owner
                barrier.wait(timeout=10)
                result = RepairService.create_candidate_using_filed_report(
                    local_owner,
                    local_block,
                    local_annual,
                    case_a_profile(),
                    "concurrent-idempotency",
                )
                return (
                    result.amendment.pk,
                    result.replacement_proposal.pk,
                    result.pass_decision.pk,
                    result.candidate.pk,
                    result.calculation_receipt.pk,
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: repair_once(), range(2)))
        self.assertEqual(results[0], results[1])
        self.assertEqual(1, blocked.amendments.count())
        self.assertEqual(1, ModelChangeProposal.objects.filter(parent=blocked.proposal).count())
        self.assertEqual(1, ArtifactVersion.objects.filter(role="candidate").count())
        self.assertEqual(1, CalculationReceipt.objects.count())

    def test_apply_calculate_and_compare_failures_leave_block_retryable(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        for boundary in ("apply", "calculate", "compare"):
            with self.subTest(boundary=boundary), patch(
                f"product.campaign.model_change.services.adapter.{boundary}",
                side_effect=AdapterRejected(
                    f"FORCED_{boundary.upper()}_FAILURE",
                    f"forced {boundary} failure",
                ),
            ):
                result = RepairService.create_candidate_using_filed_report(
                    self.owner,
                    blocked,
                    annual,
                    case_a_profile(),
                    f"forced-{boundary}-failure",
                )
                self.assertEqual("failure", result.created_or_existing)
                self.assertEqual(
                    ModelChangeOutcome.Stage.CALCULATION_FAILURE,
                    result.outcome.stage,
                )
                self.assertEqual(0, blocked.amendments.count())
                self.assertEqual(
                    0,
                    ModelChangeProposal.objects.filter(parent=blocked.proposal).count(),
                )
                self.assertEqual(0, ArtifactVersion.objects.filter(role="candidate").count())
                self.assertEqual(0, CalculationReceipt.objects.count())
                resumed = ProjectionService.resume(
                    self.owner, self.episode.job_id, self.episode.pk
                )
                self.assertEqual(blocked.pk, resumed["decision"].pk)
                self.assertEqual(result.outcome.pk, resumed["technical_outcome"].pk)
                self.assertEqual("RETRY_CANDIDATE", resumed["next_action"])
        repaired = RepairService.create_candidate_using_filed_report(
            self.owner,
            blocked,
            annual,
            case_a_profile(),
            "restored-adapter",
        )
        self.assertIsNotNone(repaired.candidate)
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        self.assertIsNone(resumed["technical_outcome"])
        self.assertEqual(repaired.candidate.pk, resumed["candidate"].pk)

    def test_formula_error_is_a_recoverable_non_dispositionable_failure(self) -> None:
        _, _, blocked = self.blocked_path()
        annual = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        with patch(
            "product.campaign.model_change.services.adapter.calculate",
            return_value=(
                b"not-admitted",
                {
                    "formula_errors": ["#VALUE!"],
                    "warnings": [],
                },
            ),
        ):
            result = RepairService.create_candidate_using_filed_report(
                self.owner,
                blocked,
                annual,
                case_a_profile(),
                "formula-error",
            )
        self.assertEqual("FORMULA_ERRORS", result.outcome.reason_code)
        self.assertEqual(0, ArtifactVersion.objects.filter(role="candidate").count())
        self.assertEqual(0, CalculationReceipt.objects.count())
        self.assertFalse(self.episode.artifact_dispositions.exists())
