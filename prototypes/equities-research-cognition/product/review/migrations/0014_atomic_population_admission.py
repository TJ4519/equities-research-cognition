import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("review", "0013_lineagerecord_provenance")]
    operations = [
        migrations.CreateModel(
            name="JudgmentUnit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("unit_id", models.CharField(max_length=255)),
                ("provisional", models.JSONField(editable=False)),
                ("comparison", models.JSONField(editable=False)),
                ("transition", models.JSONField(editable=False)),
            ],
            options={"base_manager_name": "objects", "default_manager_name": "objects"},
        ),
        migrations.CreateModel(
            name="PopulationAdmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("idempotency_key", models.CharField(max_length=64)),
                ("request_digest", models.CharField(editable=False, max_length=64)),
                ("evidence_mode", models.CharField(choices=[
                    ("contract_fixture", "Contract fixture — engineering only"),
                    ("native_observed_run", "Native-observed NTM/Codex RIE run"),
                    ("langfuse_observed_run", "Langfuse-observed NTM/Codex RIE run"),
                ], max_length=32)),
                ("runtime_receipt", models.JSONField(editable=False)),
                ("runtime_digest", models.CharField(editable=False, max_length=64)),
                ("admitted_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"base_manager_name": "objects", "default_manager_name": "objects"},
        ),
        migrations.RemoveConstraint(
            model_name="researchcase", name="l0_research_case_admission_disabled",
        ),
        migrations.AlterField(
            model_name="lineagerecord", name="kind",
            field=models.CharField(choices=[
                ("role", "Agent role"), ("prompt", "Prompt"), ("skill", "Skill"),
                ("tool", "Tool trace"), ("source", "Source use"),
                ("artifact", "Artifact evolution"),
                ("claim_transition", "Claim transition"),
                ("synthesis", "Synthesis use"),
                ("machine_judgment", "Machine judgment"),
                ("runtime", "Exact runtime correlation"),
            ], max_length=32),
        ),
        migrations.AlterField(
            model_name="researchcase", name="subject_mode",
            field=models.CharField(choices=[
                ("legacy_fixture_import", "Legacy fixture — engineering only"),
                ("contract_fixture", "Contract fixture — engineering only"),
                ("native_observed_run", "Native-observed NTM/Codex RIE run"),
                ("langfuse_observed_run", "Langfuse-observed NTM/Codex RIE run"),
            ], max_length=32),
        ),
        migrations.AddField(
            model_name="judgmentunit", name="case",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="judgment_unit", to="review.researchcase",
            ),
        ),
        migrations.AddField(
            model_name="populationadmission", name="artifact_seal",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="population_admission", to="review.artifactseal",
            ),
        ),
        migrations.AddField(
            model_name="populationadmission", name="enrollment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="population_admissions", to="review.analystenrollment",
            ),
        ),
        migrations.AddField(
            model_name="judgmentunit", name="population_admission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="judgment_units", to="review.populationadmission",
            ),
        ),
        migrations.AddField(
            model_name="queueassignment", name="population_admission",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="assignments", to="review.populationadmission",
            ),
        ),
        migrations.AddField(
            model_name="researchcase", name="population_admission",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="cases", to="review.populationadmission",
            ),
        ),
        migrations.AddConstraint(
            model_name="researchcase",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("artifact_seal__isnull", True),
                        ("population_admission__isnull", True),
                        ("subject_mode", "legacy_fixture_import"),
                    ),
                    models.Q(
                        ("artifact_seal__isnull", False),
                        ("population_admission__isnull", False),
                        ("subject_mode__in", (
                            "contract_fixture", "native_observed_run",
                            "langfuse_observed_run",
                        )),
                    ),
                    _connector="OR",
                ),
                name="research_case_admission_mode",
            ),
        ),
        migrations.AddConstraint(
            model_name="populationadmission",
            constraint=models.UniqueConstraint(
                fields=("enrollment", "idempotency_key"),
                name="one_admission_idempotency_key_per_enrollment",
            ),
        ),
        migrations.AddConstraint(
            model_name="judgmentunit",
            constraint=models.UniqueConstraint(
                fields=("population_admission", "unit_id"),
                name="one_judgment_unit_per_admission",
            ),
        ),
        migrations.RunSQL(
            "CREATE TRIGGER review_populationadmission_append_only "
            "BEFORE UPDATE OR DELETE ON review_populationadmission "
            "FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation(); "
            "CREATE TRIGGER review_judgmentunit_append_only "
            "BEFORE UPDATE OR DELETE ON review_judgmentunit "
            "FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation();",
            "DROP TRIGGER IF EXISTS review_judgmentunit_append_only ON review_judgmentunit; "
            "DROP TRIGGER IF EXISTS review_populationadmission_append_only ON review_populationadmission;",
        ),
    ]
