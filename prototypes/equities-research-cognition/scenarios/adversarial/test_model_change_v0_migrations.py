from __future__ import annotations

from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from django.test import TransactionTestCase, override_settings


OLD = [("campaign", "0004_bound_input_history_append_only")]
HEAD = [("campaign", "0006_model_change_v0_guards")]


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

    def test_populated_reverse_refuses_before_destructive_operations(self) -> None:
        call_command(
            "seed_model_change_v0_case_a",
            username="migration-owner",
            stdout=StringIO(),
        )
        executor = MigrationExecutor(connection)
        with self.assertRaisesRegex(RuntimeError, "refusing destructive"):
            executor.migrate([("campaign", "0005_model_change_v0")])
        tables = set(connection.introspection.table_names())
        self.assertIn("campaign_modelchangeepisode", tables)
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM campaign_modelchangeepisode")
            self.assertEqual(1, cursor.fetchone()[0])
