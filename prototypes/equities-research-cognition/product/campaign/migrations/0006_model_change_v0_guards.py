from django.db import migrations


FACT_TABLES = (
    "campaign_researchjob",
    "campaign_modelchangeepisode",
    "campaign_artifactmanifestversion",
    "campaign_conceptualobjectversion",
    "campaign_objectdisposition",
    "campaign_sourcedocumentversion",
    "campaign_sourceassertion",
    "campaign_modelchangeproposal",
    "campaign_admissibilitydecision",
    "campaign_calculationreceipt",
    "campaign_amendment",
    "campaign_invalidationevent",
    "campaign_artifactdisposition",
    "campaign_correctionrecord",
)


def install_guards(apps, schema_editor) -> None:
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION campaign_model_change_append_only()
            RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
              RAISE EXCEPTION 'model-change canonical facts are append-only';
            END;
            $$;
            """
        )
        for table in FACT_TABLES:
            cursor.execute(
                f"""
                CREATE TRIGGER model_change_append_only
                BEFORE UPDATE OR DELETE ON {table}
                FOR EACH ROW EXECUTE FUNCTION campaign_model_change_append_only();
                """
            )
        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION campaign_model_change_candidate_guard()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE valid_link integer;
            BEGIN
              IF NEW.role = 'candidate' THEN
                IF NEW.parent_id IS NULL OR NEW.candidate_from_pass_id IS NULL THEN
                  RAISE EXCEPTION 'candidate requires exact parent and pass authority';
                END IF;
                SELECT count(*) INTO valid_link
                FROM campaign_admissibilitydecision decision
                JOIN campaign_modelchangeproposal proposal
                  ON proposal.id = decision.proposal_id
                JOIN campaign_modelchangeepisode episode
                  ON episode.id = proposal.episode_id
                JOIN campaign_researchjob job ON job.id = episode.job_id
                JOIN campaign_researchcampaign campaign
                  ON campaign.id = episode.campaign_id
                JOIN campaign_artifactversion parent
                  ON parent.id = proposal.starting_artifact_id
                JOIN campaign_conceptualobjectversion object_version
                  ON object_version.id = proposal.conceptual_object_id
                JOIN campaign_sourceassertion assertion
                  ON assertion.id = proposal.source_assertion_id
                JOIN campaign_sourcedocumentversion document_version
                  ON document_version.id = assertion.document_version_id
                JOIN campaign_artifactmanifestversion manifest
                  ON manifest.id = proposal.manifest_id
                WHERE decision.id = NEW.candidate_from_pass_id
                  AND decision.outcome = 'PASS'
                  AND decision.closure_digest = proposal.closure_digest
                  AND proposal.input_revision = episode.input_revision
                  AND proposal.starting_artifact_id = NEW.parent_id
                  AND episode.starting_artifact_id = NEW.parent_id
                  AND parent.campaign_id = NEW.campaign_id
                  AND episode.campaign_id = NEW.campaign_id
                  AND campaign.director_id = job.owner_id
                  AND object_version.episode_id = episode.id
                  AND document_version.episode_id = episode.id
                  AND manifest.episode_id = episode.id
                  AND manifest.artifact_id = NEW.parent_id
                  AND NOT EXISTS (
                    SELECT 1 FROM campaign_invalidationevent invalidation
                    JOIN campaign_amendment amendment
                      ON amendment.id = invalidation.amendment_id
                    WHERE amendment.episode_id = episode.id
                      AND (
                        (invalidation.descendant_type = 'PROPOSAL'
                         AND invalidation.descendant_id = proposal.id)
                        OR
                        (invalidation.descendant_type = 'DECISION'
                         AND invalidation.descendant_id = decision.id)
                      )
                  );
                IF valid_link <> 1 THEN
                  RAISE EXCEPTION 'candidate pass authority is not current and exact';
                END IF;
              ELSIF NEW.parent_id IS NOT NULL OR NEW.candidate_from_pass_id IS NOT NULL THEN
                RAISE EXCEPTION 'non-candidate artifact cannot carry candidate authority';
              END IF;
              RETURN NEW;
            END;
            $$;

            CREATE TRIGGER model_change_candidate_guard
            BEFORE INSERT ON campaign_artifactversion
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_candidate_guard();

            CREATE OR REPLACE FUNCTION campaign_model_change_workorder_guard()
            RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
              IF OLD.protocol = 'model_change_v0'
                 OR (TG_OP = 'UPDATE' AND NEW.protocol = 'model_change_v0') THEN
                RAISE EXCEPTION 'model-change work authority is append-only';
              END IF;
              IF TG_OP = 'DELETE' THEN
                RETURN OLD;
              END IF;
              RETURN NEW;
            END;
            $$;

            CREATE TRIGGER model_change_workorder_append_only
            BEFORE UPDATE OR DELETE ON campaign_workorder
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_workorder_guard();
            """
        )


def remove_guards(apps, schema_editor) -> None:
    with schema_editor.connection.cursor() as cursor:
        populated = []
        for table in FACT_TABLES:
            cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
            if cursor.fetchone() is not None:
                populated.append(table)
        if populated:
            raise RuntimeError(
                "refusing destructive model-change reverse while canonical facts exist"
            )
        if schema_editor.connection.vendor == "postgresql":
            cursor.execute(
                "DROP TRIGGER IF EXISTS model_change_workorder_append_only ON campaign_workorder"
            )
            cursor.execute(
                "DROP FUNCTION IF EXISTS campaign_model_change_workorder_guard()"
            )
            cursor.execute(
                "DROP TRIGGER IF EXISTS model_change_candidate_guard ON campaign_artifactversion"
            )
            cursor.execute(
                "DROP FUNCTION IF EXISTS campaign_model_change_candidate_guard()"
            )
            for table in FACT_TABLES:
                cursor.execute(
                    f"DROP TRIGGER IF EXISTS model_change_append_only ON {table}"
                )
            cursor.execute(
                "DROP FUNCTION IF EXISTS campaign_model_change_append_only()"
            )


class Migration(migrations.Migration):
    dependencies = [("campaign", "0005_model_change_v0")]

    operations = [migrations.RunPython(install_guards, remove_guards)]
