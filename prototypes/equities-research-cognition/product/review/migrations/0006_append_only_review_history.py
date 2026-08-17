from django.db import migrations


FORWARD = """
CREATE FUNCTION flywheel_reject_history_mutation() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'review history is append-only' USING ERRCODE = '55000';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER research_case_append_only
BEFORE UPDATE OR DELETE ON review_researchcase
FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation();

CREATE TRIGGER lineage_record_append_only
BEFORE UPDATE OR DELETE ON review_lineagerecord
FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation();

CREATE TRIGGER first_pass_append_only
BEFORE UPDATE OR DELETE ON review_firstpass
FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation();

CREATE TRIGGER exposure_event_append_only
BEFORE UPDATE OR DELETE ON review_exposureevent
FOR EACH ROW EXECUTE FUNCTION flywheel_reject_history_mutation();
"""

REVERSE = """
DROP TRIGGER IF EXISTS exposure_event_append_only ON review_exposureevent;
DROP TRIGGER IF EXISTS first_pass_append_only ON review_firstpass;
DROP TRIGGER IF EXISTS lineage_record_append_only ON review_lineagerecord;
DROP TRIGGER IF EXISTS research_case_append_only ON review_researchcase;
DROP FUNCTION IF EXISTS flywheel_reject_history_mutation();
"""


class Migration(migrations.Migration):
    dependencies = [("review", "0005_exposureevent_lineage_snapshot_and_more")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
