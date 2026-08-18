from __future__ import annotations

from io import StringIO
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import uuid

from django.core.management import call_command
from django.db import DatabaseError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from django.test import TransactionTestCase, override_settings


OLD = [("campaign", "0004_bound_input_history_append_only")]
REJECTED_HEAD = [("campaign", "0006_model_change_v0_guards")]
HEAD = [("campaign", "0007_model_change_v0_repair_1")]


class ModelChangeMigrationTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        self.temporary = TemporaryDirectory(prefix="case-a-migration-")
        self.settings_context = override_settings(
            MODEL_CHANGE_V0=True,
            CAMPAIGN_ROOT=Path(self.temporary.name) / "campaigns",
        )
        self.settings_context.enable()

    def tearDown(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        self.settings_context.disable()
        self.temporary.cleanup()
        super().tearDown()

    def test_upgrade_from_0004_preserves_representative_legacy_campaign(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(OLD)
        old_apps = executor.loader.project_state(OLD).apps
        User = old_apps.get_model("auth", "User")
        Campaign = old_apps.get_model("campaign", "ResearchCampaign")
        owner = User.objects.create(username="legacy-owner")
        legacy = Campaign.objects.create(
            director_id=owner.pk,
            title="Legacy campaign",
            issuer_or_security="Synthetic legacy issuer",
            equities_decision_use="Legacy synthetic use",
            evidence_cutoff="2025-01-01",
            commissioned_question="Preserve this row",
            ntm_session="legacy-model-change-migration",
            artifact_root=str(Path(self.temporary.name) / "legacy"),
        )
        executor = MigrationExecutor(connection)
        executor.migrate(HEAD)
        new_apps = executor.loader.project_state(HEAD).apps
        NewCampaign = new_apps.get_model("campaign", "ResearchCampaign")
        self.assertEqual("Legacy campaign", NewCampaign.objects.get(pk=legacy.pk).title)
        self.assertEqual(0, new_apps.get_model("campaign", "ResearchJob").objects.count())

    def test_empty_reverse_to_0004_is_permitted(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(OLD)
        applied = MigrationRecorder(connection).applied_migrations()
        self.assertNotIn(("campaign", "0005_model_change_v0"), applied)
        self.assertNotIn(("campaign", "0006_model_change_v0_guards"), applied)
        self.assertNotIn(("campaign", "0007_model_change_v0_repair_1"), applied)

    def test_upgrade_from_0006_preserves_valid_v0_rows(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(REJECTED_HEAD)
        call_command(
            "seed_model_change_v0_case_a",
            username="valid-v0-owner",
            stdout=StringIO(),
        )
        from product.campaign.models import ModelChangeEpisode

        episode = ModelChangeEpisode.objects.get()
        episode_id = episode.pk
        episode_digest = episode.digest
        artifact_digest = episode.starting_artifact.digest
        executor = MigrationExecutor(connection)
        executor.migrate(HEAD)
        new_apps = executor.loader.project_state(HEAD).apps
        NewEpisode = new_apps.get_model("campaign", "ModelChangeEpisode")
        preserved = NewEpisode.objects.get(pk=episode_id)
        self.assertEqual(episode_digest, preserved.digest)
        NewArtifact = new_apps.get_model("campaign", "ArtifactVersion")
        self.assertEqual(
            artifact_digest,
            NewArtifact.objects.get(pk=preserved.starting_artifact_id).digest,
        )

    def test_upgrade_from_0006_refuses_forged_or_orphaned_candidate(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(REJECTED_HEAD)
        from product.campaign.model_change import services
        from product.campaign.models import (
            ModelChangeEpisode,
            ModelChangeProposal,
            SourceAssertion,
            SourceDocumentVersion,
        )

        call_command(
            "seed_model_change_v0_case_a",
            username="forged-upgrade-owner",
            stdout=StringIO(),
        )
        episode = ModelChangeEpisode.objects.get()
        assertion = SourceAssertion.objects.select_related(
            "document_version"
        ).get(
            document_version__document_class=(
                SourceDocumentVersion.DocumentClass.EARNINGS_RELEASE_8K
            )
        )
        conceptual = episode.conceptual_objects.get()
        manifest = episode.artifact_manifests.get()
        proposal_id = uuid.uuid4()
        closure = "c" * 64
        operation = {
            "kind": manifest.allowed_operation,
            "target_ref": manifest.target_ref,
            "value": str(assertion.value),
            "unit": assertion.unit,
        }
        payload = {
            "id": str(proposal_id),
            "episode": str(episode.pk),
            "parent": None,
            "work_order": None,
            "proposer_kind": ModelChangeProposal.ProposerKind.HOST_DERIVED,
            "conceptual_object": str(conceptual.pk),
            "starting_artifact": str(episode.starting_artifact_id),
            "source_assertion": str(assertion.pk),
            "manifest": str(manifest.pk),
            "input_revision": 1,
            "operation": operation,
            "protocol_version": services.PROTOCOL_VERSION,
            "claim_ceiling": conceptual.claim_ceiling,
            "closure_digest": closure,
        }
        proposal = services._create(
            ModelChangeProposal,
            {
                "id": proposal_id,
                "episode": episode,
                "proposer_kind": ModelChangeProposal.ProposerKind.HOST_DERIVED,
                "conceptual_object": conceptual,
                "starting_artifact": episode.starting_artifact,
                "source_assertion": assertion,
                "manifest": manifest,
                "input_revision": 1,
                "operation": operation,
                "protocol_version": services.PROTOCOL_VERSION,
                "claim_ceiling": conceptual.claim_ceiling,
                "closure_digest": closure,
            },
            payload,
        )
        decision_id = uuid.uuid4()
        candidate_id = uuid.uuid4()
        content = b"forged-orphan-candidate"
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO campaign_admissibilitydecision
                  (id, proposal_id, validator_version, outcome, reason_code,
                   closure_digest, digest, created_at)
                VALUES (%s, %s, 'attacker/v0', 'PASS', 'ATTACKER_PASS', %s, %s, NOW())
                """,
                [decision_id, proposal.pk, closure, "d" * 64],
            )
            cursor.execute(
                """
                INSERT INTO campaign_artifactversion
                  (id, campaign_id, role, filename, media_type, content, digest,
                   parent_id, candidate_from_pass_id, created_at)
                VALUES (%s, %s, 'candidate', 'forged.xlsx', %s, %s, %s, %s, %s, NOW())
                """,
                [
                    candidate_id,
                    episode.campaign_id,
                    episode.starting_artifact.media_type,
                    content,
                    sha256(content).hexdigest(),
                    episode.starting_artifact_id,
                    decision_id,
                ],
            )
        executor = MigrationExecutor(connection)
        with self.assertRaisesRegex(RuntimeError, "forged or orphaned candidate"):
            executor.migrate(HEAD)
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE campaign_researchcampaign CASCADE")
        MigrationExecutor(connection).migrate(HEAD)

    def test_outcome_table_is_direct_sql_append_only(self) -> None:
        from product.campaign.model_change.services import (
            ObjectService,
            OutcomeService,
            PROTOCOL_VERSION,
            WorkCompiler,
        )
        from product.campaign.models import (
            ModelChangeEpisode,
            ObjectDisposition,
            SourceAssertion,
        )

        call_command(
            "seed_model_change_v0_case_a",
            username="outcome-append-only-owner",
            stdout=StringIO(),
        )
        episode = ModelChangeEpisode.objects.get()
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO campaign_modelchangeoutcome
                      (id, episode_id, work_order_id, blocked_decision_id, stage,
                       reason_code, public_message, next_action, closure_digest,
                       attempt_key, protocol_version, technical_details, digest,
                       created_at)
                    VALUES (%s, %s, NULL, NULL, 'RUNTIME_FAILURE', 'FORGED',
                            'No workbook changed.', 'RETRY_WORK', %s, %s,
                            'model-change-v0/2026-08-17', '{}'::jsonb, %s, NOW())
                    """,
                    [uuid.uuid4(), episode.pk, "e" * 64, "f" * 64, "1" * 64],
                )
        owner = episode.job.owner
        conceptual = episode.conceptual_objects.get()
        meaning = ObjectService.disposition(
            owner,
            conceptual,
            ObjectDisposition.Action.CONFIRM_MEANING,
            {"confirmed": True},
        )
        method = ObjectService.disposition(
            owner,
            conceptual,
            ObjectDisposition.Action.AUTHORIZE_METHOD,
            {"method": "reported_value"},
        )
        order = WorkCompiler.compile(
            episode,
            conceptual,
            [meaning, method],
            episode.artifact_manifests.get(),
            list(
                SourceAssertion.objects.select_related(
                    "document_version__artifact"
                )
            ),
            PROTOCOL_VERSION,
        )
        outcome_id = OutcomeService.record_runtime_failure(order, "TEST").pk
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE campaign_modelchangeoutcome SET public_message = 'changed' WHERE id = %s",
                    [outcome_id],
                )
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM campaign_modelchangeoutcome WHERE id = %s",
                    [outcome_id],
                )

    def test_populated_reverse_refuses_before_destructive_operations(self) -> None:
        call_command(
            "seed_model_change_v0_case_a",
            username="migration-owner",
            stdout=StringIO(),
        )
        executor = MigrationExecutor(connection)
        with self.assertRaisesRegex(RuntimeError, "refusing destructive"):
            executor.migrate(REJECTED_HEAD)
        tables = set(connection.introspection.table_names())
        self.assertIn("campaign_modelchangeepisode", tables)
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM campaign_modelchangeepisode")
            self.assertEqual(1, cursor.fetchone()[0])
