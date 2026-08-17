from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("review", "0002_researchcase_source_url")]
    operations = [
        migrations.RemoveField(model_name="researchcase", name="necessary_context"),
        migrations.AddField(model_name="researchcase", name="context_items", field=models.JSONField(default=list), preserve_default=False),
        migrations.AddField(model_name="researchcase", name="custody_tree_digest", field=models.CharField(default="", max_length=64), preserve_default=False),
        migrations.AddField(model_name="researchcase", name="source_artifact_digest", field=models.CharField(default="", max_length=64), preserve_default=False),
        migrations.AddField(model_name="researchcase", name="evidence_artifact_digest", field=models.CharField(default="", max_length=64), preserve_default=False),
        migrations.AddField(model_name="researchcase", name="projection_version", field=models.CharField(default="", max_length=64), preserve_default=False),
    ]
