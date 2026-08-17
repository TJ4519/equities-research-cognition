from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("review", "0006_append_only_review_history")]
    operations = [migrations.RunSQL(
        """
        CREATE TRIGGER queue_assignment_append_only
        BEFORE UPDATE OR DELETE ON review_queueassignment
        FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation();
        """,
        "DROP TRIGGER IF EXISTS queue_assignment_append_only ON review_queueassignment;",
    )]
