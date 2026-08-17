from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("review", "0012_launchpad_langfuse_cutover")]
    operations = [
        migrations.AddField(
            model_name="lineagerecord", name="producer",
            field=models.TextField(blank=True, default="", editable=False),
        ),
        migrations.AddField(
            model_name="lineagerecord", name="relations",
            field=models.JSONField(default=list, editable=False),
        ),
    ]
