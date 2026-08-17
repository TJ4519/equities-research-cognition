from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("review", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="researchcase",
            name="source_url",
            field=models.URLField(default="https://www.sec.gov/"),
            preserve_default=False,
        ),
    ]
