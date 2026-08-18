from __future__ import annotations

from django.db import migrations


def install_source_custody(apps, schema_editor) -> None:
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT CASE
              WHEN episode.id IS NULL OR job.id IS NULL
                OR episode_campaign.id IS NULL OR source_artifact.id IS NULL
                OR source_campaign.id IS NULL
                THEN 'missing source-custody relation'
              WHEN source_artifact.role <> 'source'
                THEN 'non-source artifact'
              WHEN source_artifact.campaign_id <> episode.campaign_id
                THEN 'cross-campaign source artifact'
              WHEN episode_campaign.director_id <> job.owner_id
                OR source_campaign.director_id <> job.owner_id
                THEN 'cross-owner source artifact'
              ELSE NULL
            END AS defect
            FROM campaign_sourcedocumentversion document_version
            LEFT JOIN campaign_modelchangeepisode episode
              ON episode.id = document_version.episode_id
            LEFT JOIN campaign_researchjob job ON job.id = episode.job_id
            LEFT JOIN campaign_researchcampaign episode_campaign
              ON episode_campaign.id = episode.campaign_id
            LEFT JOIN campaign_artifactversion source_artifact
              ON source_artifact.id = document_version.artifact_id
            LEFT JOIN campaign_researchcampaign source_campaign
              ON source_campaign.id = source_artifact.campaign_id
            WHERE episode.id IS NULL
               OR job.id IS NULL
               OR episode_campaign.id IS NULL
               OR source_artifact.id IS NULL
               OR source_campaign.id IS NULL
               OR source_artifact.role <> 'source'
               OR source_artifact.campaign_id <> episode.campaign_id
               OR episode_campaign.director_id <> job.owner_id
               OR source_campaign.director_id <> job.owner_id
            LIMIT 1
            """
        )
        defect = cursor.fetchone()
        if defect is not None:
            raise RuntimeError(
                f"refusing source-custody migration with {defect[0]}"
            )
        cursor.execute(
            """
            SELECT assertion.id
            FROM campaign_sourceassertion assertion
            LEFT JOIN campaign_sourcedocumentversion document_version
              ON document_version.id = assertion.document_version_id
            LEFT JOIN campaign_modelchangeepisode episode
              ON episode.id = document_version.episode_id
            LEFT JOIN campaign_researchjob job ON job.id = episode.job_id
            LEFT JOIN campaign_researchcampaign episode_campaign
              ON episode_campaign.id = episode.campaign_id
            LEFT JOIN campaign_artifactversion source_artifact
              ON source_artifact.id = document_version.artifact_id
            LEFT JOIN campaign_researchcampaign source_campaign
              ON source_campaign.id = source_artifact.campaign_id
            WHERE document_version.id IS NULL
               OR episode.id IS NULL
               OR job.id IS NULL
               OR episode_campaign.id IS NULL
               OR source_artifact.id IS NULL
               OR source_campaign.id IS NULL
               OR source_artifact.role <> 'source'
               OR source_artifact.campaign_id <> episode.campaign_id
               OR episode_campaign.director_id <> job.owner_id
               OR source_campaign.director_id <> job.owner_id
            LIMIT 1
            """
        )
        if cursor.fetchone() is not None:
            raise RuntimeError(
                "refusing source-custody migration with invalid source assertion"
            )
        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION campaign_model_change_source_custody_v2(
              requested_document_id uuid
            ) RETURNS TABLE(
              valid boolean,
              reason_code text,
              episode_id uuid,
              campaign_id uuid,
              owner_id integer,
              artifact_id uuid
            ) LANGUAGE plpgsql STABLE AS $$
            DECLARE facts record;
            BEGIN
              SELECT
                document_version.episode_id,
                episode.campaign_id,
                job.owner_id,
                document_version.artifact_id,
                source_artifact.role AS artifact_role,
                source_artifact.campaign_id AS artifact_campaign_id,
                episode_campaign.director_id AS episode_director_id,
                source_campaign.director_id AS source_director_id
              INTO facts
              FROM campaign_sourcedocumentversion document_version
              JOIN campaign_modelchangeepisode episode
                ON episode.id = document_version.episode_id
              JOIN campaign_researchjob job ON job.id = episode.job_id
              JOIN campaign_researchcampaign episode_campaign
                ON episode_campaign.id = episode.campaign_id
              JOIN campaign_artifactversion source_artifact
                ON source_artifact.id = document_version.artifact_id
              JOIN campaign_researchcampaign source_campaign
                ON source_campaign.id = source_artifact.campaign_id
              WHERE document_version.id = requested_document_id;

              IF NOT FOUND THEN
                RETURN QUERY SELECT false, 'BLOCK_SOURCE_CUSTODY'::text,
                  NULL::uuid, NULL::uuid, NULL::integer, NULL::uuid;
                RETURN;
              END IF;
              RETURN QUERY SELECT
                facts.artifact_role = 'source'
                  AND facts.artifact_campaign_id = facts.campaign_id
                  AND facts.episode_director_id = facts.owner_id
                  AND facts.source_director_id = facts.owner_id,
                CASE WHEN facts.artifact_role = 'source'
                       AND facts.artifact_campaign_id = facts.campaign_id
                       AND facts.episode_director_id = facts.owner_id
                       AND facts.source_director_id = facts.owner_id
                     THEN 'SOURCE_CUSTODY_EXACT'::text
                     ELSE 'BLOCK_SOURCE_CUSTODY'::text END,
                facts.episode_id,
                facts.campaign_id,
                facts.owner_id,
                facts.artifact_id;
            END;
            $$;

            CREATE OR REPLACE FUNCTION campaign_model_change_source_document_guard_v2()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE valid_link integer;
            BEGIN
              SELECT count(*) INTO valid_link
              FROM campaign_modelchangeepisode episode
              JOIN campaign_researchjob job ON job.id = episode.job_id
              JOIN campaign_researchcampaign episode_campaign
                ON episode_campaign.id = episode.campaign_id
              JOIN campaign_artifactversion source_artifact
                ON source_artifact.id = NEW.artifact_id
              JOIN campaign_researchcampaign source_campaign
                ON source_campaign.id = source_artifact.campaign_id
              WHERE episode.id = NEW.episode_id
                AND source_artifact.role = 'source'
                AND source_artifact.campaign_id = episode.campaign_id
                AND episode_campaign.director_id = job.owner_id
                AND source_campaign.director_id = job.owner_id;
              IF valid_link <> 1 THEN
                RAISE EXCEPTION 'source document crosses exact source custody';
              END IF;
              RETURN NEW;
            END;
            $$;

            CREATE TRIGGER model_change_source_document_guard_v2
            BEFORE INSERT ON campaign_sourcedocumentversion
            FOR EACH ROW
            EXECUTE FUNCTION campaign_model_change_source_document_guard_v2();

            CREATE OR REPLACE FUNCTION campaign_model_change_source_assertion_guard_v2()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE custody record;
            BEGIN
              SELECT * INTO custody
              FROM campaign_model_change_source_custody_v2(NEW.document_version_id);
              IF custody.valid IS DISTINCT FROM true THEN
                RAISE EXCEPTION 'source assertion crosses exact source custody';
              END IF;
              RETURN NEW;
            END;
            $$;

            CREATE TRIGGER model_change_source_assertion_guard_v2
            BEFORE INSERT ON campaign_sourceassertion
            FOR EACH ROW
            EXECUTE FUNCTION campaign_model_change_source_assertion_guard_v2();

            CREATE OR REPLACE FUNCTION campaign_model_change_expected_admission_v2(
              requested_proposal_id uuid
            ) RETURNS TABLE(
              validator_version text,
              outcome text,
              reason_code text,
              closure_digest text
            ) LANGUAGE plpgsql STABLE AS $$
            DECLARE expected record;
            DECLARE custody record;
            DECLARE requested_document_id uuid;
            BEGIN
              SELECT assertion.document_version_id INTO requested_document_id
              FROM campaign_modelchangeproposal proposal
              JOIN campaign_sourceassertion assertion
                ON assertion.id = proposal.source_assertion_id
              WHERE proposal.id = requested_proposal_id;
              SELECT * INTO expected
              FROM campaign_model_change_expected_admission_v1(requested_proposal_id);
              SELECT * INTO custody
              FROM campaign_model_change_source_custody_v2(requested_document_id);
              IF custody.valid IS DISTINCT FROM true THEN
                RETURN QUERY SELECT
                  'model-change-admissibility/v2'::text,
                  'BLOCK'::text,
                  'BLOCK_SOURCE_CUSTODY'::text,
                  expected.closure_digest::text;
                RETURN;
              END IF;
              RETURN QUERY SELECT
                'model-change-admissibility/v2'::text,
                expected.outcome::text,
                expected.reason_code::text,
                expected.closure_digest::text;
            END;
            $$;

            DROP TRIGGER IF EXISTS model_change_decision_guard_v1
              ON campaign_admissibilitydecision;
            CREATE OR REPLACE FUNCTION campaign_model_change_decision_guard_v2()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE expected record;
            BEGIN
              SELECT * INTO expected
              FROM campaign_model_change_expected_admission_v2(NEW.proposal_id);
              IF expected.validator_version IS NULL
                 OR NEW.validator_version <> expected.validator_version
                 OR NEW.outcome <> expected.outcome
                 OR NEW.reason_code <> expected.reason_code
                 OR NEW.closure_digest IS DISTINCT FROM expected.closure_digest THEN
                RAISE EXCEPTION 'admissibility decision differs from canonical database result';
              END IF;
              RETURN NEW;
            END;
            $$;
            CREATE TRIGGER model_change_decision_guard_v2
            BEFORE INSERT ON campaign_admissibilitydecision
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_decision_guard_v2();

            DROP TRIGGER IF EXISTS model_change_candidate_guard
              ON campaign_artifactversion;
            CREATE OR REPLACE FUNCTION campaign_model_change_candidate_guard_v2()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE expected record;
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
                JOIN campaign_artifactversion source_artifact
                  ON source_artifact.id = document_version.artifact_id
                JOIN campaign_researchcampaign source_campaign
                  ON source_campaign.id = source_artifact.campaign_id
                JOIN campaign_artifactmanifestversion manifest
                  ON manifest.id = proposal.manifest_id
                WHERE decision.id = NEW.candidate_from_pass_id
                  AND proposal.input_revision = episode.input_revision
                  AND proposal.starting_artifact_id = NEW.parent_id
                  AND episode.starting_artifact_id = NEW.parent_id
                  AND parent.campaign_id = NEW.campaign_id
                  AND episode.campaign_id = NEW.campaign_id
                  AND campaign.director_id = job.owner_id
                  AND source_artifact.role = 'source'
                  AND source_artifact.campaign_id = episode.campaign_id
                  AND source_artifact.campaign_id = NEW.campaign_id
                  AND source_campaign.director_id = job.owner_id
                  AND object_version.episode_id = episode.id
                  AND document_version.episode_id = episode.id
                  AND manifest.episode_id = episode.id
                  AND manifest.artifact_id = NEW.parent_id
                  AND encode(sha256(NEW.content), 'hex') = NEW.digest
                  AND NOT EXISTS (
                    SELECT 1 FROM campaign_invalidationevent invalidation
                    WHERE (
                      invalidation.descendant_type = 'PROPOSAL'
                      AND invalidation.descendant_id = proposal.id
                    ) OR (
                      invalidation.descendant_type = 'DECISION'
                      AND invalidation.descendant_id = decision.id
                    )
                  );
                IF valid_link <> 1 THEN
                  RAISE EXCEPTION 'candidate pass authority is not current and exact';
                END IF;
                SELECT * INTO expected
                FROM campaign_model_change_expected_admission_v2(
                  (SELECT proposal_id FROM campaign_admissibilitydecision
                   WHERE id = NEW.candidate_from_pass_id)
                );
                IF expected.outcome <> 'PASS'
                   OR NOT EXISTS (
                     SELECT 1
                     FROM campaign_admissibilitydecision decision
                     WHERE decision.id = NEW.candidate_from_pass_id
                       AND decision.validator_version = expected.validator_version
                       AND decision.outcome = expected.outcome
                       AND decision.reason_code = expected.reason_code
                       AND decision.closure_digest = expected.closure_digest
                   ) THEN
                  RAISE EXCEPTION 'candidate authority is not a canonical database pass';
                END IF;
              ELSIF NEW.parent_id IS NOT NULL OR NEW.candidate_from_pass_id IS NOT NULL THEN
                RAISE EXCEPTION 'non-candidate artifact cannot carry candidate authority';
              END IF;
              RETURN NEW;
            END;
            $$;
            CREATE TRIGGER model_change_candidate_guard
            BEFORE INSERT ON campaign_artifactversion
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_candidate_guard_v2();

            DROP TRIGGER IF EXISTS model_change_receipt_guard_v1
              ON campaign_calculationreceipt;
            CREATE OR REPLACE FUNCTION campaign_model_change_receipt_guard_v2()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE expected record;
            BEGIN
              SELECT * INTO expected
              FROM campaign_model_change_expected_admission_v2(
                (SELECT decision.proposal_id
                 FROM campaign_admissibilitydecision decision
                 WHERE decision.id = NEW.pass_decision_id)
              );
              IF expected.outcome <> 'PASS'
                 OR NEW.formula_errors <> '[]'::jsonb
                 OR NOT EXISTS (
                   SELECT 1
                   FROM campaign_artifactversion candidate
                   JOIN campaign_artifactversion parent
                     ON parent.id = candidate.parent_id
                   JOIN campaign_admissibilitydecision decision
                     ON decision.id = candidate.candidate_from_pass_id
                   JOIN campaign_modelchangeproposal proposal
                     ON proposal.id = decision.proposal_id
                   JOIN campaign_modelchangeepisode episode
                     ON episode.id = proposal.episode_id
                   WHERE candidate.id = NEW.candidate_id
                     AND candidate.role = 'candidate'
                     AND candidate.candidate_from_pass_id = NEW.pass_decision_id
                     AND NEW.episode_id = episode.id
                     AND NEW.manifest_id = proposal.manifest_id
                     AND NEW.input_digest = parent.digest
                     AND NEW.output_digest = candidate.digest
                     AND NEW.closure_digest = expected.closure_digest
                     AND decision.validator_version = expected.validator_version
                     AND decision.outcome = expected.outcome
                     AND decision.reason_code = expected.reason_code
                     AND decision.closure_digest = expected.closure_digest
                 ) THEN
                RAISE EXCEPTION 'calculation receipt differs from exact candidate authority';
              END IF;
              RETURN NEW;
            END;
            $$;
            CREATE TRIGGER model_change_receipt_guard_v2
            BEFORE INSERT ON campaign_calculationreceipt
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_receipt_guard_v2();

            DROP TRIGGER IF EXISTS model_change_outcome_guard_v1
              ON campaign_modelchangeoutcome;
            CREATE OR REPLACE FUNCTION campaign_model_change_outcome_guard_v2()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE valid_custody integer;
            DECLARE expected record;
            DECLARE expected_attempt text;
            BEGIN
              IF NEW.public_message IS NULL
                 OR btrim(NEW.public_message) = ''
                 OR jsonb_typeof(NEW.technical_details) <> 'object'
                 OR length(NEW.closure_digest) <> 64
                 OR length(NEW.attempt_key) <> 64 THEN
                RAISE EXCEPTION 'model-change outcome lacks exact bounded evidence';
              END IF;
              IF NEW.stage IN ('RUNTIME_FAILURE', 'WORKER_REFUSAL') THEN
                SELECT count(*) INTO valid_custody
                FROM campaign_workorder work_order
                JOIN campaign_modelchangeepisode episode
                  ON episode.campaign_id = work_order.campaign_id
                WHERE work_order.id = NEW.work_order_id
                  AND episode.id = NEW.episode_id
                  AND NEW.blocked_decision_id IS NULL
                  AND work_order.protocol = 'model_change_v0'
                  AND work_order.packet->'episode'->>'id' = NEW.episode_id::text
                  AND work_order.packet->>'closure_digest' = NEW.closure_digest
                  AND work_order.packet->>'protocol_version' = NEW.protocol_version
                  AND NEW.next_action = 'RETRY_WORK';
                expected_attempt := encode(
                  sha256(
                    convert_to(
                      '{"stage":"'
                      || CASE WHEN NEW.stage = 'RUNTIME_FAILURE'
                              THEN 'runtime' ELSE 'refusal' END
                      || '","work_order":"' || NEW.work_order_id::text || '"}',
                      'UTF8'
                    )
                  ),
                  'hex'
                );
                IF valid_custody <> 1 OR NEW.attempt_key <> expected_attempt THEN
                  RAISE EXCEPTION 'runtime outcome crosses exact work custody';
                END IF;
              ELSIF NEW.stage = 'CALCULATION_FAILURE' THEN
                SELECT * INTO expected
                FROM campaign_model_change_expected_admission_v2(
                  (SELECT proposal_id
                   FROM campaign_admissibilitydecision
                   WHERE id = NEW.blocked_decision_id)
                );
                SELECT count(*) INTO valid_custody
                FROM campaign_admissibilitydecision decision
                JOIN campaign_modelchangeproposal proposal
                  ON proposal.id = decision.proposal_id
                WHERE decision.id = NEW.blocked_decision_id
                  AND proposal.episode_id = NEW.episode_id
                  AND NEW.work_order_id IS NULL
                  AND decision.outcome = 'BLOCK'
                  AND decision.reason_code = 'BLOCK_WRONG_DOCUMENT_CLASS'
                  AND expected.validator_version = decision.validator_version
                  AND expected.outcome = decision.outcome
                  AND expected.reason_code = decision.reason_code
                  AND expected.closure_digest = decision.closure_digest
                  AND NEW.closure_digest = decision.closure_digest
                  AND NEW.protocol_version = proposal.protocol_version
                  AND NEW.next_action = 'RETRY_CANDIDATE';
                IF valid_custody <> 1 THEN
                  RAISE EXCEPTION 'calculation outcome crosses exact blocked custody';
                END IF;
              ELSE
                RAISE EXCEPTION 'unsupported model-change outcome stage';
              END IF;
              RETURN NEW;
            END;
            $$;
            CREATE TRIGGER model_change_outcome_guard_v2
            BEFORE INSERT ON campaign_modelchangeoutcome
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_outcome_guard_v2();
            """
        )


def remove_source_custody(apps, schema_editor) -> None:
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM campaign_admissibilitydecision
            WHERE validator_version = 'model-change-admissibility/v2'
            LIMIT 1
            """
        )
        if cursor.fetchone() is not None:
            raise RuntimeError(
                "refusing source-custody reverse while V2 authority exists"
            )
        cursor.execute(
            """
            DROP TRIGGER IF EXISTS model_change_outcome_guard_v2
              ON campaign_modelchangeoutcome;
            DROP FUNCTION IF EXISTS campaign_model_change_outcome_guard_v2();
            CREATE TRIGGER model_change_outcome_guard_v1
            BEFORE INSERT ON campaign_modelchangeoutcome
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_outcome_guard_v1();

            DROP TRIGGER IF EXISTS model_change_receipt_guard_v2
              ON campaign_calculationreceipt;
            DROP FUNCTION IF EXISTS campaign_model_change_receipt_guard_v2();
            CREATE TRIGGER model_change_receipt_guard_v1
            BEFORE INSERT ON campaign_calculationreceipt
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_receipt_guard_v1();

            DROP TRIGGER IF EXISTS model_change_candidate_guard
              ON campaign_artifactversion;
            DROP FUNCTION IF EXISTS campaign_model_change_candidate_guard_v2();
            CREATE TRIGGER model_change_candidate_guard
            BEFORE INSERT ON campaign_artifactversion
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_candidate_guard();

            DROP TRIGGER IF EXISTS model_change_decision_guard_v2
              ON campaign_admissibilitydecision;
            DROP FUNCTION IF EXISTS campaign_model_change_decision_guard_v2();
            CREATE TRIGGER model_change_decision_guard_v1
            BEFORE INSERT ON campaign_admissibilitydecision
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_decision_guard_v1();

            DROP TRIGGER IF EXISTS model_change_source_assertion_guard_v2
              ON campaign_sourceassertion;
            DROP FUNCTION IF EXISTS campaign_model_change_source_assertion_guard_v2();
            DROP TRIGGER IF EXISTS model_change_source_document_guard_v2
              ON campaign_sourcedocumentversion;
            DROP FUNCTION IF EXISTS campaign_model_change_source_document_guard_v2();
            DROP FUNCTION IF EXISTS campaign_model_change_expected_admission_v2(uuid);
            DROP FUNCTION IF EXISTS campaign_model_change_source_custody_v2(uuid);
            """
        )


class Migration(migrations.Migration):
    dependencies = [("campaign", "0007_model_change_v0_repair_1")]

    operations = [
        migrations.RunPython(install_source_custody, remove_source_custody)
    ]
