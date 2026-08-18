from __future__ import annotations

from hashlib import sha256
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import uuid

from django.core.management import call_command
from django.test import TestCase, override_settings

from product.campaign.model_change.adapter import AdapterRejected, case_a_profile
from product.campaign.model_change.services import (
    AdmissibilityGate,
    CandidateService,
    CorrectionService,
    DispositionService,
    InvalidationService,
    ModelChangeRejected,
    ObjectService,
    PROTOCOL_VERSION,
    ProjectionService,
    ProposalParser,
    RepairService,
    WorkCompiler,
)
from product.campaign.models import (
    AdmissibilityDecision,
    ArtifactDisposition,
    ArtifactVersion,
    InvalidationEvent,
    ArtifactManifestVersion,
    ConceptualObjectVersion,
    ModelChangeProposal,
    ModelChangeEpisode,
    ObjectDisposition,
    SourceAssertion,
    SourceDocumentVersion,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


class CaseAFixtureMixin:
    def setUp(self) -> None:
        super().setUp()
        self.temporary = TemporaryDirectory(prefix="case-a-test-")
        self.settings_context = override_settings(
            MODEL_CHANGE_V0=True,
            CAMPAIGN_ROOT=Path(self.temporary.name) / "campaigns",
        )
        self.settings_context.enable()
        call_command(
            "seed_model_change_v0_case_a",
            username="case-a-test-owner",
            stdout=StringIO(),
        )
        self.episode = ModelChangeEpisode.objects.select_related(
            "job__owner", "campaign", "starting_artifact"
        ).get()
        self.owner = self.episode.job.owner
        self.object = self.episode.conceptual_objects.get()
        self.manifest = self.episode.artifact_manifests.get()
        self.assertions = list(
            SourceAssertion.objects.select_related(
                "document_version__artifact"
            ).order_by("document_version__document_class")
        )

    def tearDown(self) -> None:
        self.settings_context.disable()
        self.temporary.cleanup()
        super().tearDown()

    def compile_order(self):
        meaning = ObjectService.disposition(
            self.owner,
            self.object,
            ObjectDisposition.Action.CONFIRM_MEANING,
            {"confirmed": True},
        )
        method = ObjectService.disposition(
            self.owner,
            self.object,
            ObjectDisposition.Action.AUTHORIZE_METHOD,
            {
                "method": "reported_value",
                "source_rule": "filed_annual_report_for_annual_target",
            },
        )
        return WorkCompiler.compile(
            self.episode,
            self.object,
            [meaning, method],
            self.manifest,
            self.assertions,
            PROTOCOL_VERSION,
        )

    def worker_value(self, order, document_class="EARNINGS_RELEASE_8K"):
        assertion = next(
            row
            for row in order.packet["source_assertions"]
            if row["document_class"] == document_class
        )
        return {
            "schema": "model-change-proposal/v0",
            "episode_id": order.packet["episode"]["id"],
            "episode_digest": order.packet["episode"]["sha256"],
            "input_revision": order.packet["episode"]["input_revision"],
            "conceptual_object_id": order.packet["conceptual_object"]["id"],
            "conceptual_object_digest": order.packet["conceptual_object"]["sha256"],
            "starting_artifact_id": order.packet["starting_artifact"]["id"],
            "starting_artifact_digest": order.packet["starting_artifact"]["sha256"],
            "source_assertion_id": assertion["id"],
            "operation": {
                "kind": order.packet["manifest"]["allowed_operation"],
                "target_ref": order.packet["manifest"]["target_ref"],
                "value": assertion["value"],
                "unit": assertion["unit"],
            },
            "claim_ceiling": order.packet["conceptual_object"]["claim_ceiling"],
        }

    def blocked_path(self):
        order = self.compile_order()
        proposal = ProposalParser.parse(self.worker_value(order), order.packet)
        decision = AdmissibilityGate.evaluate(
            proposal, order.packet["closure_digest"]
        )
        return order, proposal, decision


class ModelChangeServiceTests(CaseAFixtureMixin, TestCase):
    def test_joined_block_repair_candidate_disposition_correction_and_restart(self) -> None:
        original = bytes(self.episode.starting_artifact.content)
        order, proposal, blocked = self.blocked_path()
        self.assertEqual("BLOCK_WRONG_DOCUMENT_CLASS", blocked.reason_code)
        self.assertEqual(0, ArtifactVersion.objects.filter(role="candidate").count())
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
            "joined-service-test",
        )
        amendment = repair.amendment
        replacement = repair.replacement_proposal
        passed = repair.pass_decision
        candidate = repair.candidate
        calculation = repair.calculation_receipt
        self.assertEqual(AdmissibilityDecision.Outcome.PASS, passed.outcome)
        self.assertNotEqual(proposal.closure_digest, replacement.closure_digest)
        self.assertTrue(
            InvalidationEvent.objects.filter(
                amendment=amendment,
                descendant_type=InvalidationEvent.DescendantType.DECISION,
                descendant_id=blocked.pk,
            ).exists()
        )
        operation = calculation.operation_receipt
        self.assertEqual(self.episode.starting_artifact_id, candidate.parent_id)
        self.assertEqual(passed.pk, candidate.candidate_from_pass_id)
        self.assertEqual(original, bytes(self.episode.starting_artifact.content))
        self.assertEqual(2, len(calculation.consequences))
        self.assertEqual([], calculation.formula_errors)
        self.assertEqual(self.manifest.digest, operation["manifest_sha256"])
        disposition = DispositionService.record(
            self.owner,
            candidate,
            self.episode.named_use,
            ArtifactDisposition.Kind.SIMULATE_NAMED_USE,
        )
        correction = CorrectionService.seed(
            blocked,
            amendment,
            replacement,
            candidate,
            {
                "protocol": PROTOCOL_VERSION,
                "adapter_profile": case_a_profile()["profile_id"],
            },
        )
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        self.assertEqual(candidate.pk, resumed["candidate"].pk)
        self.assertEqual(disposition.pk, resumed["disposition"].pk)
        self.assertEqual(blocked.pk, correction.blocked_decision_id)
        self.assertEqual(
            sha256(bytes(candidate.content)).hexdigest(), candidate.digest
        )

    def test_equal_value_sources_remain_distinct_and_model_uses_host_identities(self) -> None:
        self.assertEqual({"37378.00000000"}, {str(item.value) for item in self.assertions})
        self.assertEqual(2, len({item.digest for item in self.assertions}))
        order = self.compile_order()
        attacked = self.worker_value(order)
        attacked["source_assertion_id"] = "00000000-0000-0000-0000-000000000000"
        with self.assertRaisesRegex(ModelChangeRejected, "source assertion"):
            ProposalParser.parse(attacked, order.packet)
        attacked = self.worker_value(order)
        attacked["starting_artifact_digest"] = "0" * 64
        with self.assertRaisesRegex(ModelChangeRejected, "identity"):
            ProposalParser.parse(attacked, order.packet)

    def test_stale_closure_blocks_and_material_amendment_invalidates_descendants(self) -> None:
        order = self.compile_order()
        proposal = ProposalParser.parse(self.worker_value(order), order.packet)
        amendment, replacement, events = InvalidationService.amend(
            self.owner, self.object, {"description": "Amended synthetic meaning"}
        )
        stale = AdmissibilityGate.evaluate(proposal, "0" * 64)
        self.assertEqual("BLOCK_STALE_CLOSURE", stale.reason_code)
        self.assertEqual(self.object.pk, replacement.parent_id)
        self.assertTrue(events)
        self.assertTrue(
            InvalidationEvent.objects.filter(
                amendment=amendment,
                descendant_type=InvalidationEvent.DescendantType.PROPOSAL,
                descendant_id=proposal.pk,
            ).exists()
        )
        with self.assertRaisesRegex(ModelChangeRejected, "current exact pass"):
            CandidateService.create(stale, self.episode.starting_artifact, case_a_profile())

    def test_structural_operation_refuses_before_candidate(self) -> None:
        order = self.compile_order()
        value = self.worker_value(order)
        value["operation"]["kind"] = "insert_row"
        with self.assertRaises(ModelChangeRejected):
            ProposalParser.parse(value, order.packet)
        from product.campaign.model_change import adapter

        with self.assertRaises(AdapterRejected) as raised:
            adapter.apply(
                bytes(self.episode.starting_artifact.content),
                [
                    {
                        "kind": "insert_row",
                        "target_ref": "FY25_REVENUE_USDM",
                        "value": "37378",
                        "unit": "USDm",
                    }
                ],
                self.manifest.digest,
                case_a_profile(),
                expected_inspection_digest=self.manifest.inspection_digest,
            )
        self.assertEqual("UNSUPPORTED_STRUCTURAL_OPERATION", raised.exception.reason_code)
        self.assertEqual(0, ArtifactVersion.objects.filter(role="candidate").count())

    def test_preliminary_target_accepts_8k_without_global_document_preference(self) -> None:
        from product.campaign.model_change import services

        manifest_id = uuid.uuid4()
        observed = {
            "adapter_profile": self.manifest.adapter_profile,
            "adapter_version": self.manifest.adapter_version,
            "target_ref": services.PRELIMINARY_TARGET,
            "target_address": self.manifest.target_address,
            "target_value": "36900",
            "target_unit": "USDm",
            "allowed_operation": "set_numeric_value",
            "dependency_closure": self.manifest.dependency_closure,
            "formula_bindings": self.manifest.formula_bindings,
            "inspection_digest": self.manifest.inspection_digest,
            "warnings": [],
        }
        manifest = services._create(
            ArtifactManifestVersion,
            {
                "id": manifest_id,
                "episode": self.episode,
                "artifact": self.episode.starting_artifact,
                **observed,
                "support_status": ArtifactManifestVersion.Support.SUPPORTED,
            },
            services._manifest_payload(
                manifest_id, self.episode, self.episode.starting_artifact, observed
            ),
        )
        manifest.refresh_from_db()
        object_id = uuid.uuid4()
        meaning = {
            "target": services.PRELIMINARY_TARGET,
            "description": "Preliminary FY2025 earnings-flash revenue",
            "period": "FY2025",
            "unit": "USDm",
        }
        conceptual = services._create(
            ConceptualObjectVersion,
            {
                "id": object_id,
                "episode": self.episode,
                "manifest": manifest,
                "binding_status": ConceptualObjectVersion.BindingStatus.PROPOSED,
                "economic_meaning": meaning,
                "method_policy": {"method": "reported_value"},
                "claim_ceiling": self.object.claim_ceiling,
            },
            services._object_payload(
                object_id,
                self.episode,
                parent=None,
                manifest=manifest,
                binding_status=ConceptualObjectVersion.BindingStatus.PROPOSED,
                economic_meaning=meaning,
                method_policy={"method": "reported_value"},
                claim_ceiling=self.object.claim_ceiling,
            ),
        )
        assertion = next(
            item
            for item in self.assertions
            if item.document_version.document_class
            == SourceDocumentVersion.DocumentClass.EARNINGS_RELEASE_8K
        )
        meaning_authority = ObjectService.disposition(
            self.owner,
            conceptual,
            ObjectDisposition.Action.CONFIRM_MEANING,
            {"confirmed": True},
        )
        method_authority = ObjectService.disposition(
            self.owner,
            conceptual,
            ObjectDisposition.Action.AUTHORIZE_METHOD,
            {"method": "reported_value", "source_rule": "captured-source-per-target"},
        )
        order = WorkCompiler.compile(
            self.episode,
            conceptual,
            [meaning_authority, method_authority],
            manifest,
            self.assertions,
            PROTOCOL_VERSION,
        )
        proposal = ProposalParser.parse(
            self.worker_value(
                order,
                SourceDocumentVersion.DocumentClass.EARNINGS_RELEASE_8K,
            ),
            order.packet,
        )
        decision = AdmissibilityGate.evaluate(
            proposal, str(order.packet["closure_digest"])
        )
        self.assertEqual(AdmissibilityDecision.Outcome.PASS, decision.outcome)
