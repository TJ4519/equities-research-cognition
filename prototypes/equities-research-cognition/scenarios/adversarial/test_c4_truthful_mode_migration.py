from hashlib import sha256

from django.db import DatabaseError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from product.review.models import ResearchCase, digest


class CleanCutoverMigrationTests(TransactionTestCase):
    migrate_from = [("review", "0011_remove_consequencedecision_legal_consequence_action_target_and_more")]
    migrate_to = [("review", "0015_separate_admission_assignment")]

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def test_cutover_preserves_review_history_only_as_legacy_fixture(self):
        apps = self.migrate(self.migrate_from)
        User = apps.get_model("auth", "User")
        user = User.objects.create(username="migration-reviewer", is_active=True)
        enrollment = apps.get_model("review", "AnalystEnrollment").objects.create(
            user=user, scope_code="equities", qualification_basis="migration fixture", attested_by="test",
        )
        rubric = [{"label": "requires narrowing", "criterion": "Narrow the claim."}]
        body = {
            "question": "Does this passage license the claim?", "source_identity": "Issuer filing",
            "source_url": "https://example.com/filing", "source_locator": "p. 7",
            "exact_passage": "Exact passage.", "context_items": [{
                "source_identity": "Issuer filing", "source_url": "https://example.com/filing",
                "locator": "p. 8", "exact_passage": "Context.",
            }], "custody_tree_digest": "a" * 64, "source_artifact_digest": "b" * 64,
            "evidence_artifact_digest": "c" * 64, "projection_version": "migration-test/v1",
        }
        rubric_digest = digest(rubric)
        old_mode = "otel_native_run"
        Case = apps.get_model("review", "ResearchCase")
        case = Case.objects.create(
            external_id="otel-native:historical", subject_mode=old_mode, rubric=rubric,
            rubric_digest=rubric_digest,
            packet_digest=digest({**body, "rubric_digest": rubric_digest, "subject_mode": old_mode}),
            **body,
        )
        long_case = Case.objects.create(
            external_id="x" * 255, subject_mode=old_mode, rubric=rubric,
            rubric_digest=rubric_digest,
            packet_digest=digest({**body, "rubric_digest": rubric_digest, "subject_mode": old_mode}),
            **body,
        )
        collision_case = Case.objects.create(
            external_id=f"legacy-fixture:{case.pk}:otel-native:historical",
            subject_mode=old_mode, rubric=rubric, rubric_digest=rubric_digest,
            packet_digest=digest({**body, "rubric_digest": rubric_digest, "subject_mode": old_mode}),
            **body,
        )
        assignment = apps.get_model("review", "QueueAssignment").objects.create(
            enrollment=enrollment, case=case,
        )
        first_pass = apps.get_model("review", "FirstPass").objects.create(
            assignment=assignment, author_user=user, session_fingerprint="d" * 64,
            reviewer_scope_snapshot={"enrollment_id": enrollment.pk, "scope_code": "equities"},
            packet_digest_snapshot=case.packet_digest, rubric_digest_snapshot=rubric_digest,
            subject_mode_snapshot=old_mode,
            packet_snapshot={"question": case.question, "subject_mode": old_mode},
            decision="requires_narrowing", rationale="Historical locked rationale.",
        )
        apps.get_model("review", "ExposureEvent").objects.create(
            first_pass=first_pass, lineage_digest="e" * 64, lineage_snapshot=[],
        )

        try:
            current_apps = self.migrate(self.migrate_to)
            current = ResearchCase.objects.get(pk=case.pk)
            self.assertEqual("legacy_fixture_import", current.subject_mode)
            self.assertEqual(
                f"legacy-fixture:{case.pk}:{sha256('otel-native:historical'.encode()).hexdigest()}",
                current.external_id,
            )
            self.assertEqual(digest(current.packet_body()), current.packet_digest)
            self.assertIsNone(current.artifact_seal_id)
            migrated_ids = list(
                ResearchCase.objects.filter(pk__in=(long_case.pk, collision_case.pk))
                .values_list("external_id", flat=True)
            )
            self.assertEqual(2, len(set(migrated_ids)))
            self.assertTrue(all(value.startswith("legacy-fixture:") and len(value) <= 255 for value in migrated_ids))
            self.assertEqual(old_mode, current.queueassignment_set.get().first_pass.subject_mode_snapshot)
            for rejected in (
                "EpisodeRegistration", "EpisodeRoleBinding", "EpisodeSeal", "EpisodeAdmission",
            ):
                with self.assertRaises(LookupError):
                    current_apps.get_model("review", rejected)
            self.assertEqual(
                0, current_apps.get_model("review", "PopulationAdmission").objects.count(),
            )
            with self.assertRaises(DatabaseError), transaction.atomic(), connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE review_researchcase SET question = %s WHERE id = %s",
                    ["forbidden", case.pk],
                )
        finally:
            self.migrate(self.migrate_to)
