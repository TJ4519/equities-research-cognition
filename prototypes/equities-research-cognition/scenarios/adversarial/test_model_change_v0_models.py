from __future__ import annotations

from hashlib import sha256
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import DatabaseError, connection, transaction
from django.test import TestCase

from product.campaign.model_change import services
from product.campaign.models import (
    ArtifactVersion,
    ConceptualObjectVersion,
    ModelChangeEpisode,
    ResearchJob,
    SourceAssertion,
    canonical_decimal,
    canonical_digest,
)

from scenarios.adversarial.test_model_change_v0_services import CaseAFixtureMixin


class ModelChangeModelTests(CaseAFixtureMixin, TestCase):
    def test_episode_has_exact_campaign_owner_and_starting_artifact(self) -> None:
        self.assertEqual(self.owner.pk, self.episode.campaign.director_id)
        self.assertEqual(self.owner.pk, self.episode.job.owner_id)
        self.assertEqual(
            self.episode.campaign_id, self.episode.starting_artifact.campaign_id
        )
        self.assertEqual(1, ModelChangeEpisode.objects.count())

    def test_orm_and_direct_sql_reject_mutation(self) -> None:
        self.episode.job.company_ref = "changed"
        with self.assertRaisesRegex(ValidationError, "append-only"):
            self.episode.job.save()
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE campaign_researchjob SET company_ref = %s WHERE id = %s",
                    ["changed", self.episode.job_id],
                )
        self.episode.job.refresh_from_db()
        self.assertNotEqual("changed", self.episode.job.company_ref)

    def test_direct_sql_candidate_without_pass_is_rejected(self) -> None:
        parent = self.episode.starting_artifact
        content = b"not-a-candidate"
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO campaign_artifactversion
                      (id, campaign_id, role, filename, media_type, content,
                       digest, parent_id, candidate_from_pass_id, created_at)
                    VALUES (%s, %s, 'candidate', %s, %s, %s, %s, %s, NULL, NOW())
                    """,
                    [
                        uuid.uuid4(),
                        self.episode.campaign_id,
                        "hostile.xlsx",
                        parent.media_type,
                        content,
                        sha256(content).hexdigest(),
                        parent.pk,
                    ],
                )
        self.assertEqual(0, ArtifactVersion.objects.filter(role="candidate").count())

    def test_owner_isolation_discloses_no_cross_owner_episode(self) -> None:
        stranger = get_user_model().objects.create_user(username="stranger")
        with self.assertRaisesRegex(services.ModelChangeRejected, "unavailable"):
            services.ProjectionService.resume(
                stranger, self.episode.job_id, self.episode.pk
            )

    def test_case_b_assumption_grammar_and_case_c_unbound_structure_are_representable(self) -> None:
        assumption_id = uuid.uuid4()
        meaning = {
            "reported_charge": "host-captured",
            "recurring_share_assumption": {
                "author": "human",
                "scope": "synthetic FY2025 charge",
                "rationale": "scenario only",
                "change_condition": "new attributed assumption",
            },
            "derived_adjustment": "deterministic",
        }
        payload = services._object_payload(
            assumption_id,
            self.episode,
            parent=self.object,
            manifest=self.manifest,
            binding_status=ConceptualObjectVersion.BindingStatus.PROPOSED,
            economic_meaning=meaning,
            method_policy=self.object.method_policy,
            claim_ceiling=self.object.claim_ceiling,
        )
        assumption = services._create(
            ConceptualObjectVersion,
            {
                "id": assumption_id,
                "episode": self.episode,
                "parent": self.object,
                "manifest": self.manifest,
                "binding_status": ConceptualObjectVersion.BindingStatus.PROPOSED,
                "economic_meaning": meaning,
                "method_policy": self.object.method_policy,
                "claim_ceiling": self.object.claim_ceiling,
            },
            payload,
        )
        _, replacement, _ = services.InvalidationService.amend(
            self.owner,
            assumption,
            {"recurring_share_assumption": {"author": "human", "scope": "revised"}},
        )
        self.assertEqual(assumption.pk, replacement.parent_id)

        structure_id = uuid.uuid4()
        structure_payload = services._object_payload(
            structure_id,
            self.episode,
            parent=None,
            manifest=None,
            binding_status=ConceptualObjectVersion.BindingStatus.PROPOSED_STRUCTURE,
            economic_meaning={"requested_structure": "new segment row"},
            method_policy={},
            claim_ceiling="Unsupported structure proposal only.",
        )
        structure = services._create(
            ConceptualObjectVersion,
            {
                "id": structure_id,
                "episode": self.episode,
                "binding_status": ConceptualObjectVersion.BindingStatus.PROPOSED_STRUCTURE,
                "economic_meaning": structure_payload["economic_meaning"],
                "method_policy": {},
                "claim_ceiling": structure_payload["claim_ceiling"],
            },
            structure_payload,
        )
        self.assertIsNone(structure.manifest_id)
        self.assertEqual("PROPOSED_STRUCTURE", structure.binding_status)

    def test_source_bytes_and_assertion_digest_are_exact(self) -> None:
        self.episode.full_clean()
        self.manifest.full_clean()
        self.object.full_clean()
        for assertion in SourceAssertion.objects.select_related(
            "document_version__artifact"
        ):
            assertion.document_version.full_clean()
            assertion.full_clean()
            artifact = assertion.document_version.artifact
            self.assertEqual(sha256(bytes(artifact.content)).hexdigest(), artifact.digest)
            expected = canonical_digest(
                {
                    "id": str(assertion.pk),
                    "document_version": str(assertion.document_version_id),
                    "document_sha256": assertion.document_version.digest,
                    "locator": assertion.locator,
                    "value": canonical_decimal(assertion.value),
                    "unit": assertion.unit,
                    "dimensions": assertion.dimensions,
                }
            )
            self.assertEqual(expected, assertion.digest)
