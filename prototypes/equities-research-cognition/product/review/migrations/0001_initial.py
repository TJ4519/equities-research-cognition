from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="AnalystEnrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope_code", models.CharField(max_length=64)),
                ("qualification_basis", models.TextField()),
                ("attested_by", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("enrolled_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="ResearchCase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("external_id", models.CharField(max_length=255, unique=True)),
                ("subject_mode", models.CharField(choices=[("legacy_fixture_import", "Legacy fixture — engineering only"), ("otel_native_run", "OTel-native run")], max_length=32)),
                ("question", models.TextField()),
                ("source_identity", models.TextField()),
                ("source_locator", models.TextField()),
                ("exact_passage", models.TextField()),
                ("necessary_context", models.TextField()),
                ("rubric", models.JSONField()),
                ("packet_digest", models.CharField(editable=False, max_length=64)),
                ("rubric_digest", models.CharField(editable=False, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="QueueAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("assigned_at", models.DateTimeField(auto_now_add=True)),
                ("case", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="review.researchcase")),
                ("enrollment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="review.analystenrollment")),
            ],
        ),
        migrations.AddConstraint(
            model_name="queueassignment",
            constraint=models.UniqueConstraint(fields=("enrollment", "case"), name="one_case_per_enrollment"),
        ),
    ]
