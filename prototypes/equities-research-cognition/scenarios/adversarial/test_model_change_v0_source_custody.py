from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
import uuid

from django.contrib.auth import get_user_model
from django.db import DatabaseError, connection, transaction
from django.test import TransactionTestCase

from product.campaign.model_change.adapter import case_a_profile
from product.campaign.model_change.services import (
    EvidenceService,
    ModelChangeRejected,
    RepairService,
)
from product.campaign.models import (
    AdmissibilityDecision,
    Amendment,
    ArtifactVersion,
    CalculationReceipt,
    CorrectionRecord,
    ModelChangeProposal,
    ResearchCampaign,
    SourceAssertion,
    SourceDocumentVersion,
    canonical_digest,
)
from scenarios.adversarial.test_model_change_v0_services import CaseAFixtureMixin


class ModelChangeSourceCustodyTests(CaseAFixtureMixin, TransactionTestCase):
    reset_sequences = True

    def _other_campaign(self, *, same_owner: bool) -> ResearchCampaign:
        director = self.owner
        if not same_owner:
            director = get_user_model().objects.create(
                username=f"foreign-owner-{uuid.uuid4()}"
            )
        return ResearchCampaign.objects.create(
            director=director,
            title="Synthetic other campaign",
            issuer_or_security="Synthetic other issuer",
            equities_decision_use="Synthetic test only",
            evidence_cutoff=date(2025, 10, 3),
            commissioned_question="Exercise source custody",
            ntm_session=f"source-custody-{uuid.uuid4()}",
            artifact_root=f"/tmp/source-custody-{uuid.uuid4()}",
        )

    def _artifact(self, campaign: ResearchCampaign, *, role: str) -> ArtifactVersion:
        content = f"source-custody-{uuid.uuid4()}".encode()
        return ArtifactVersion.objects.create(
            campaign=campaign,
            role=role,
            filename=f"source-{uuid.uuid4()}.txt",
            media_type="text/plain",
            content=content,
            digest=sha256(content).hexdigest(),
        )

    def _insert_document(self, artifact: ArtifactVersion) -> uuid.UUID:
        document_id = uuid.uuid4()
        identity = {
            "filename": artifact.filename,
            "document_class": "FILED_ANNUAL_REPORT_10K",
            "filing_date": "2025-10-03",
            "issuer": "Synthetic issuer",
        }
        access_context = {"fixture_status": "public_synthetic_test_only"}
        digest = canonical_digest(
            {
                "id": str(document_id),
                "episode": str(self.episode.pk),
                "artifact": str(artifact.pk),
                "artifact_sha256": artifact.digest,
                "document_class": "FILED_ANNUAL_REPORT_10K",
                "identity": identity,
                "access_context": access_context,
            }
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO campaign_sourcedocumentversion
                  (id, episode_id, artifact_id, document_class, identity,
                   access_context, digest, created_at)
                VALUES (%s, %s, %s, 'FILED_ANNUAL_REPORT_10K',
                        %s::jsonb, %s::jsonb, %s, NOW())
                """,
                [
                    document_id,
                    self.episode.pk,
                    artifact.pk,
                    json.dumps(identity),
                    json.dumps(access_context),
                    digest,
                ],
            )
        return document_id

    def _assert_no_repair_authority(self) -> None:
        self.assertEqual(0, Amendment.objects.count())
        self.assertEqual(0, ArtifactVersion.objects.filter(role="candidate").count())
        self.assertEqual(0, CalculationReceipt.objects.count())
        self.assertEqual(0, CorrectionRecord.objects.count())

    def test_direct_sql_rejects_cross_owner_source_document(self) -> None:
        artifact = self._artifact(self._other_campaign(same_owner=False), role="source")
        with self.assertRaises(DatabaseError), transaction.atomic():
            self._insert_document(artifact)
        self._assert_no_repair_authority()

    def test_direct_sql_rejects_same_owner_different_campaign_document(self) -> None:
        artifact = self._artifact(self._other_campaign(same_owner=True), role="source")
        with self.assertRaises(DatabaseError), transaction.atomic():
            self._insert_document(artifact)
        self._assert_no_repair_authority()

    def test_direct_sql_rejects_same_campaign_non_source_document(self) -> None:
        with self.assertRaises(DatabaseError), transaction.atomic():
            self._insert_document(self.episode.starting_artifact)
        self._assert_no_repair_authority()

    def test_assertion_guard_rechecks_an_existing_invalid_document(self) -> None:
        artifact = self._artifact(self._other_campaign(same_owner=False), role="source")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE campaign_sourcedocumentversion "
                    "DISABLE TRIGGER model_change_source_document_guard_v2"
                )
            document_id = self._insert_document(artifact)
        finally:
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE campaign_sourcedocumentversion "
                    "ENABLE TRIGGER model_change_source_document_guard_v2"
                )
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO campaign_sourceassertion
                      (id, document_version_id, locator, value, unit,
                       dimensions, digest, created_at)
                    VALUES (%s, %s, 'synthetic row', 37378, 'USDm',
                            '{}'::jsonb, %s, NOW())
                    """,
                    [uuid.uuid4(), document_id, uuid.uuid4().hex * 2],
                )
        self._assert_no_repair_authority()

    def test_service_refuses_preexisting_invalid_chain_before_repair(self) -> None:
        _, _, blocked = self.blocked_path()
        artifact = self._artifact(self._other_campaign(same_owner=False), role="source")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE campaign_sourcedocumentversion "
                    "DISABLE TRIGGER model_change_source_document_guard_v2"
                )
                cursor.execute(
                    "ALTER TABLE campaign_sourceassertion "
                    "DISABLE TRIGGER model_change_source_assertion_guard_v2"
                )
            document_id = self._insert_document(artifact)
            assertion_id = uuid.uuid4()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO campaign_sourceassertion
                      (id, document_version_id, locator, value, unit,
                       dimensions, digest, created_at)
                    VALUES (%s, %s, 'synthetic row', 37378, 'USDm',
                            '{"metric":"revenue","period":"FY2025","unit":"USDm"}'::jsonb,
                            %s, NOW())
                    """,
                    [assertion_id, document_id, uuid.uuid4().hex * 2],
                )
        finally:
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE campaign_sourceassertion "
                    "ENABLE TRIGGER model_change_source_assertion_guard_v2"
                )
                cursor.execute(
                    "ALTER TABLE campaign_sourcedocumentversion "
                    "ENABLE TRIGGER model_change_source_document_guard_v2"
                )
        assertion = SourceAssertion.objects.select_related(
            "document_version__artifact__campaign"
        ).get(pk=assertion_id)
        baseline_proposals = ModelChangeProposal.objects.count()
        baseline_decisions = AdmissibilityDecision.objects.count()
        with self.assertRaisesRegex(ModelChangeRejected, "unavailable"):
            RepairService.create_candidate_using_filed_report(
                self.owner,
                blocked,
                assertion,
                case_a_profile(),
                "invalid-custody-service",
            )
        self.assertEqual(baseline_proposals, ModelChangeProposal.objects.count())
        self.assertEqual(baseline_decisions, AdmissibilityDecision.objects.count())
        self._assert_no_repair_authority()

    def test_v2_decision_and_candidate_recheck_forced_invalid_chain(self) -> None:
        _, legal_proposal, _ = self.blocked_path()
        artifact = self._artifact(self._other_campaign(same_owner=False), role="source")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE campaign_sourcedocumentversion "
                    "DISABLE TRIGGER model_change_source_document_guard_v2"
                )
                cursor.execute(
                    "ALTER TABLE campaign_sourceassertion "
                    "DISABLE TRIGGER model_change_source_assertion_guard_v2"
                )
            document_id = self._insert_document(artifact)
            assertion_id = uuid.uuid4()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO campaign_sourceassertion
                      (id, document_version_id, locator, value, unit,
                       dimensions, digest, created_at)
                    VALUES (%s, %s, 'synthetic row', 37378, 'USDm',
                            '{"metric":"revenue","period":"FY2025","unit":"USDm"}'::jsonb,
                            %s, NOW())
                    """,
                    [assertion_id, document_id, uuid.uuid4().hex * 2],
                )
        finally:
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE campaign_sourceassertion "
                    "ENABLE TRIGGER model_change_source_assertion_guard_v2"
                )
                cursor.execute(
                    "ALTER TABLE campaign_sourcedocumentversion "
                    "ENABLE TRIGGER model_change_source_document_guard_v2"
                )
        proposal_id = uuid.uuid4()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO campaign_modelchangeproposal
                  (id, episode_id, parent_id, work_order_id, proposer_kind,
                   conceptual_object_id, starting_artifact_id,
                   source_assertion_id, manifest_id, input_revision, operation,
                   protocol_version, claim_ceiling, closure_digest, digest,
                   created_at)
                SELECT %s, episode_id, NULL, work_order_id, proposer_kind,
                       conceptual_object_id, starting_artifact_id, %s,
                       manifest_id, input_revision, operation, protocol_version,
                       claim_ceiling, closure_digest, %s, NOW()
                FROM campaign_modelchangeproposal WHERE id = %s
                """,
                [proposal_id, assertion_id, uuid.uuid4().hex * 2, legal_proposal.pk],
            )
        forged_decision_id = uuid.uuid4()
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO campaign_admissibilitydecision
                      (id, proposal_id, validator_version, outcome, reason_code,
                       closure_digest, digest, created_at)
                    VALUES (%s, %s, 'model-change-admissibility/v2', 'PASS',
                            'PASS_EXACT_CLOSURE', %s, %s, NOW())
                    """,
                    [
                        forged_decision_id,
                        proposal_id,
                        legal_proposal.closure_digest,
                        uuid.uuid4().hex * 2,
                    ],
                )
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE campaign_admissibilitydecision "
                    "DISABLE TRIGGER model_change_decision_guard_v2"
                )
                cursor.execute(
                    """
                    INSERT INTO campaign_admissibilitydecision
                      (id, proposal_id, validator_version, outcome, reason_code,
                       closure_digest, digest, created_at)
                    VALUES (%s, %s, 'model-change-admissibility/v2', 'PASS',
                            'PASS_EXACT_CLOSURE', %s, %s, NOW())
                    """,
                    [
                        forged_decision_id,
                        proposal_id,
                        legal_proposal.closure_digest,
                        uuid.uuid4().hex * 2,
                    ],
                )
        finally:
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE campaign_admissibilitydecision "
                    "ENABLE TRIGGER model_change_decision_guard_v2"
                )
        candidate_content = b"forged-candidate-over-foreign-source"
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO campaign_artifactversion
                      (id, campaign_id, role, filename, media_type, content,
                       digest, parent_id, candidate_from_pass_id, created_at)
                    VALUES (%s, %s, 'candidate', 'forged.xlsx', %s, %s, %s,
                            %s, %s, NOW())
                    """,
                    [
                        uuid.uuid4(),
                        self.episode.campaign_id,
                        self.episode.starting_artifact.media_type,
                        candidate_content,
                        sha256(candidate_content).hexdigest(),
                        self.episode.starting_artifact_id,
                        forged_decision_id,
                    ],
                )
        self.assertEqual(0, ArtifactVersion.objects.filter(role="candidate").count())
        self.assertEqual(0, CalculationReceipt.objects.count())

    def test_legal_same_campaign_block_and_repair_use_v2_authority(self) -> None:
        _, _, blocked = self.blocked_path()
        self.assertEqual("model-change-admissibility/v2", blocked.validator_version)
        self.assertEqual("BLOCK_WRONG_DOCUMENT_CLASS", blocked.reason_code)
        annual = next(
            assertion
            for assertion in self.assertions
            if assertion.document_version.document_class
            == SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K
        )
        repaired = RepairService.create_candidate_using_filed_report(
            self.owner,
            blocked,
            annual,
            case_a_profile(),
            "legal-source-custody",
        )
        self.assertEqual("model-change-admissibility/v2", repaired.pass_decision.validator_version)
        self.assertEqual("PASS_EXACT_CLOSURE", repaired.pass_decision.reason_code)
        self.assertEqual(1, ArtifactVersion.objects.filter(role="candidate").count())
        self.assertEqual(1, CalculationReceipt.objects.count())

    def test_legal_same_campaign_capture_and_assertion_succeeds(self) -> None:
        document = EvidenceService.capture(
            b"fresh same-campaign source bytes",
            {
                "episode_id": str(self.episode.pk),
                "filename": "fresh-10k.txt",
                "document_class": "FILED_ANNUAL_REPORT_10K",
                "filing_date": "2025-10-03",
                "issuer": "Synthetic issuer",
            },
            {"fixture_status": "public_synthetic_test_only"},
        )
        assertion = EvidenceService.assert_value(
            document,
            "synthetic row",
            "37378",
            {"metric": "revenue", "period": "FY2025", "unit": "USDm"},
        )
        self.assertEqual(self.episode.campaign_id, document.artifact.campaign_id)
        self.assertEqual(document.pk, assertion.document_version_id)
