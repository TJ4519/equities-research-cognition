from django.db import migrations


TABLES = (
    "review_reviewcompletion",
    "review_consequencedecision",
    "review_currentcorrection",
    "review_rubricevalstate",
    "review_futureproposal",
)


class Migration(migrations.Migration):
    dependencies = [("review", "0008_reviewcompletion_futureproposal_currentcorrection_and_more")]
    operations = [
        migrations.RunSQL(
            "\n".join(
                f"CREATE TRIGGER {table}_append_only BEFORE UPDATE OR DELETE ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation();"
                for table in TABLES
            ),
            "\n".join(f"DROP TRIGGER IF EXISTS {table}_append_only ON {table};" for table in TABLES),
        )
    ]
