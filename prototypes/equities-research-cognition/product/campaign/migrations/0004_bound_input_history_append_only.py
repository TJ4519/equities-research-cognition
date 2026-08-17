from django.db import migrations


FORWARD = """
CREATE OR REPLACE FUNCTION campaign_reject_bound_history_mutation()
RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'bound job history is append-only' USING ERRCODE = '55000';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER campaign_artifactversion_append_only
BEFORE UPDATE OR DELETE ON campaign_artifactversion
FOR EACH ROW EXECUTE FUNCTION campaign_reject_bound_history_mutation();

CREATE TRIGGER campaign_runspecversion_append_only
BEFORE UPDATE OR DELETE ON campaign_runspecversion
FOR EACH ROW EXECUTE FUNCTION campaign_reject_bound_history_mutation();

CREATE OR REPLACE FUNCTION campaign_reject_bound_workorder_mutation()
RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.run_spec_id IS NOT NULL THEN
      RAISE EXCEPTION 'bound job history is append-only' USING ERRCODE = '55000';
    END IF;
    RETURN OLD;
  END IF;
  IF OLD.run_spec_id IS NOT NULL OR NEW.run_spec_id IS NOT NULL THEN
    RAISE EXCEPTION 'bound job history is append-only' USING ERRCODE = '55000';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER campaign_workorder_append_only
BEFORE UPDATE OR DELETE ON campaign_workorder
FOR EACH ROW EXECUTE FUNCTION campaign_reject_bound_workorder_mutation();
"""

REVERSE = """
DROP TRIGGER IF EXISTS campaign_workorder_append_only
ON campaign_workorder;
DROP TRIGGER IF EXISTS campaign_runspecversion_append_only
ON campaign_runspecversion;
DROP TRIGGER IF EXISTS campaign_artifactversion_append_only
ON campaign_artifactversion;
DROP FUNCTION IF EXISTS campaign_reject_bound_workorder_mutation();
DROP FUNCTION IF EXISTS campaign_reject_bound_history_mutation();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("campaign", "0003_artifactversion_runspecversion_workorder_run_spec"),
    ]

    operations = [migrations.RunSQL(FORWARD, REVERSE)]
