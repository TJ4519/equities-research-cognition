from hashlib import sha256
import json

import django.db.models.deletion
from django.db import migrations, models


PACKET_FIELDS = (
    "question", "source_identity", "source_url", "source_locator", "exact_passage",
    "context_items", "custody_tree_digest", "source_artifact_digest",
    "evidence_artifact_digest", "projection_version",
)


def demote_existing_cases(apps, _schema_editor):
    Case = apps.get_model("review", "ResearchCase")
    for case in Case.objects.exclude(subject_mode="legacy_fixture_import"):
        mode = "legacy_fixture_import"
        body = {field: getattr(case, field) for field in PACKET_FIELDS}
        body.update(rubric_digest=case.rubric_digest, subject_mode=mode)
        packet_digest = sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        Case.objects.filter(pk=case.pk).update(
            subject_mode=mode,
            external_id=f"legacy-fixture:{case.pk}:{sha256(case.external_id.encode()).hexdigest()}",
            packet_digest=packet_digest,
        )


class Migration(migrations.Migration):
    dependencies = [("review", "0011_remove_consequencedecision_legal_consequence_action_target_and_more")]
    operations = [
        migrations.RunSQL(
            "DROP TRIGGER research_case_append_only ON review_researchcase",
            "CREATE TRIGGER research_case_append_only BEFORE UPDATE OR DELETE ON review_researchcase "
            "FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation()",
        ),
        migrations.RunPython(demote_existing_cases, migrations.RunPython.noop),
        migrations.RunSQL(
            "CREATE TRIGGER research_case_append_only BEFORE UPDATE OR DELETE ON review_researchcase "
            "FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation()",
            "DROP TRIGGER research_case_append_only ON review_researchcase",
        ),
        migrations.AlterField(
            model_name="researchcase", name="subject_mode",
            field=models.CharField(choices=[
                ("legacy_fixture_import", "Legacy fixture — engineering only"),
                ("contract_fixture", "Contract fixture — engineering only"),
                ("langfuse_observed_run", "Langfuse-observed NTM/Codex RIE run"),
            ], max_length=32),
        ),
        migrations.CreateModel(
            name="RunRegistration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("run_id", models.UUIDField(editable=False, unique=True)),
                ("artifact_root", models.TextField(editable=False, unique=True)),
                ("commissioned_question", models.TextField(editable=False)),
                ("review_scope_code", models.CharField(editable=False, max_length=64)),
                ("expected_unit_ids", models.JSONField(editable=False)),
                ("registered_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactSeal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("manifest", models.JSONField(editable=False)),
                ("manifest_digest", models.CharField(editable=False, max_length=64, unique=True)),
                ("sealed_at", models.DateTimeField(auto_now_add=True)),
                ("registration", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="seal", to="review.runregistration")),
            ],
        ),
        migrations.AlterModelOptions(
            name="runregistration",
            options={"base_manager_name": "objects", "default_manager_name": "objects"},
        ),
        migrations.AlterModelOptions(
            name="artifactseal",
            options={"base_manager_name": "objects", "default_manager_name": "objects"},
        ),
        migrations.AlterModelOptions(
            name="researchcase",
            options={"base_manager_name": "objects", "default_manager_name": "objects"},
        ),
        migrations.AlterModelOptions(
            name="queueassignment",
            options={"base_manager_name": "objects", "default_manager_name": "objects"},
        ),
        migrations.AddField(
            model_name="researchcase", name="artifact_seal",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="cases", to="review.artifactseal"),
        ),
        migrations.AddField(model_name="lineagerecord", name="artifact_id", field=models.CharField(blank=True, default="", editable=False, max_length=255)),
        migrations.AddField(model_name="lineagerecord", name="trace_id", field=models.CharField(blank=True, default="", editable=False, max_length=32)),
        migrations.AddField(model_name="lineagerecord", name="span_id", field=models.CharField(blank=True, default="", editable=False, max_length=16)),
        migrations.AddConstraint(
            model_name="researchcase",
            constraint=models.CheckConstraint(
                condition=models.Q(("artifact_seal__isnull", True), ("subject_mode", "legacy_fixture_import")),
                name="l0_research_case_admission_disabled",
            ),
        ),
        migrations.RunSQL(
            "CREATE TRIGGER review_runregistration_append_only BEFORE UPDATE OR DELETE ON review_runregistration FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation(); "
            "CREATE TRIGGER review_artifactseal_append_only BEFORE UPDATE OR DELETE ON review_artifactseal FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation(); "
            "",
            "DROP TRIGGER IF EXISTS review_artifactseal_append_only ON review_artifactseal; "
            "DROP TRIGGER IF EXISTS review_runregistration_append_only ON review_runregistration;",
        ),
    ]
