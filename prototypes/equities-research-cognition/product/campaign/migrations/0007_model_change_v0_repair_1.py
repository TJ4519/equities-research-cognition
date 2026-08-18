from __future__ import annotations

import django.db.models.deletion
import uuid

from django.conf import settings
from django.db import migrations, models


def install_repair_guards(apps, schema_editor) -> None:
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT candidate.candidate_from_pass_id
            FROM campaign_artifactversion candidate
            WHERE candidate.role = 'candidate'
              AND candidate.candidate_from_pass_id IS NOT NULL
            GROUP BY candidate.candidate_from_pass_id
            HAVING count(*) > 1
            LIMIT 1
            """
        )
        if cursor.fetchone() is not None:
            raise RuntimeError(
                "refusing model-change repair migration with duplicate candidate authority"
            )
        cursor.execute(
            """
            SELECT amendment.blocked_decision_id
            FROM campaign_amendment amendment
            WHERE amendment.action = 'USE_FILED_ANNUAL_REPORT'
              AND amendment.blocked_decision_id IS NOT NULL
            GROUP BY amendment.blocked_decision_id
            HAVING count(*) > 1
            LIMIT 1
            """
        )
        if cursor.fetchone() is not None:
            raise RuntimeError(
                "refusing model-change repair migration with repeated filed-report repair"
            )
        cursor.execute(
            """
            SELECT candidate.id
            FROM campaign_artifactversion candidate
            LEFT JOIN campaign_admissibilitydecision decision
              ON decision.id = candidate.candidate_from_pass_id
            LEFT JOIN campaign_modelchangeproposal proposal
              ON proposal.id = decision.proposal_id
            LEFT JOIN campaign_modelchangeepisode episode
              ON episode.id = proposal.episode_id
            LEFT JOIN campaign_sourcedocumentversion document_version
              ON document_version.id = (
                SELECT assertion.document_version_id
                FROM campaign_sourceassertion assertion
                WHERE assertion.id = proposal.source_assertion_id
              )
            LEFT JOIN campaign_calculationreceipt receipt
              ON receipt.candidate_id = candidate.id
            WHERE candidate.role = 'candidate'
              AND (
                decision.id IS NULL
                OR decision.validator_version <> 'model-change-admissibility/v0'
                OR decision.outcome <> 'PASS'
                OR decision.reason_code <> 'PASS_EXACT_CLOSURE'
                OR decision.closure_digest <> proposal.closure_digest
                OR episode.id IS NULL
                OR candidate.parent_id <> proposal.starting_artifact_id
                OR candidate.campaign_id <> episode.campaign_id
                OR encode(sha256(candidate.content), 'hex') <> candidate.digest
                OR NOT (
                  (proposal.operation->>'target_ref' = 'FY25_REVENUE_USDM'
                   AND document_version.document_class = 'FILED_ANNUAL_REPORT_10K')
                  OR
                  (proposal.operation->>'target_ref' = 'FY2025_PRELIMINARY_EARNINGS_FLASH_REVENUE'
                   AND document_version.document_class = 'EARNINGS_RELEASE_8K')
                )
                OR receipt.id IS NULL
                OR receipt.pass_decision_id <> decision.id
                OR receipt.episode_id <> episode.id
                OR receipt.manifest_id <> proposal.manifest_id
                OR receipt.input_digest <> (
                  SELECT parent.digest
                  FROM campaign_artifactversion parent
                  WHERE parent.id = candidate.parent_id
                )
                OR receipt.output_digest <> candidate.digest
                OR receipt.closure_digest <> proposal.closure_digest
                OR receipt.formula_errors <> '[]'::jsonb
                OR EXISTS (
                  SELECT 1
                  FROM campaign_invalidationevent invalidation
                  WHERE (
                    invalidation.descendant_type = 'PROPOSAL'
                    AND invalidation.descendant_id = proposal.id
                  ) OR (
                    invalidation.descendant_type = 'DECISION'
                    AND invalidation.descendant_id = decision.id
                  ) OR (
                    invalidation.descendant_type = 'CANDIDATE'
                    AND invalidation.descendant_id = candidate.id
                  )
                )
              )
            LIMIT 1
            """
        )
        if cursor.fetchone() is not None:
            raise RuntimeError(
                "refusing model-change repair migration with forged or orphaned candidate authority"
            )
        cursor.execute(
            """
            SELECT receipt.id
            FROM campaign_calculationreceipt receipt
            JOIN campaign_artifactversion candidate ON candidate.id = receipt.candidate_id
            WHERE candidate.role <> 'candidate'
            LIMIT 1
            """
        )
        if cursor.fetchone() is not None:
            raise RuntimeError(
                "refusing model-change repair migration with orphaned calculation evidence"
            )

        cursor.execute(
            """
            DROP TRIGGER IF EXISTS model_change_candidate_guard
              ON campaign_artifactversion;

            CREATE OR REPLACE FUNCTION campaign_model_change_expected_admission_v1(
              requested_proposal_id uuid
            ) RETURNS TABLE(
              validator_version text,
              outcome text,
              reason_code text,
              closure_digest text
            ) LANGUAGE plpgsql STABLE AS $$
            DECLARE
              facts record;
              expected_closure text;
              expected_repair_key text;
            BEGIN
              SELECT
                proposal.*,
                episode.input_revision AS current_input_revision,
                episode.starting_artifact_id AS episode_starting_artifact_id,
                episode.campaign_id AS episode_campaign_id,
                object_version.episode_id AS object_episode_id,
                object_version.manifest_id AS object_manifest_id,
                manifest.episode_id AS manifest_episode_id,
                manifest.artifact_id AS manifest_artifact_id,
                manifest.target_ref AS manifest_target_ref,
                manifest.allowed_operation AS manifest_allowed_operation,
                manifest.target_unit AS manifest_target_unit,
                assertion.document_version_id AS assertion_document_id,
                assertion.value AS assertion_value,
                assertion.unit AS assertion_unit,
                document_version.episode_id AS document_episode_id,
                document_version.document_class AS document_class,
                work_order.protocol AS work_order_protocol,
                work_order.campaign_id AS work_order_campaign_id,
                work_order.packet AS work_order_packet,
                repair.id AS repair_id,
                repair.actor_id AS repair_actor_id,
                repair.blocked_decision_id AS repair_blocked_decision_id,
                repair.action AS repair_action,
                repair.repair_key AS repair_key,
                repair.adapter_profile AS repair_adapter_profile,
                repair.idempotency_key AS repair_idempotency_key,
                parent_decision.proposal_id AS blocked_proposal_id,
                parent_proposal.closure_digest AS blocked_closure_digest
              INTO facts
              FROM campaign_modelchangeproposal proposal
              JOIN campaign_modelchangeepisode episode
                ON episode.id = proposal.episode_id
              JOIN campaign_conceptualobjectversion object_version
                ON object_version.id = proposal.conceptual_object_id
              JOIN campaign_artifactmanifestversion manifest
                ON manifest.id = proposal.manifest_id
              JOIN campaign_sourceassertion assertion
                ON assertion.id = proposal.source_assertion_id
              JOIN campaign_sourcedocumentversion document_version
                ON document_version.id = assertion.document_version_id
              LEFT JOIN campaign_workorder work_order
                ON work_order.id = proposal.work_order_id
              LEFT JOIN campaign_amendment repair
                ON repair.replacement_proposal_id = proposal.id
               AND repair.action = 'USE_FILED_ANNUAL_REPORT'
              LEFT JOIN campaign_admissibilitydecision parent_decision
                ON parent_decision.id = repair.blocked_decision_id
              LEFT JOIN campaign_modelchangeproposal parent_proposal
                ON parent_proposal.id = parent_decision.proposal_id
              WHERE proposal.id = requested_proposal_id;

              IF NOT FOUND THEN
                RETURN QUERY SELECT
                  'model-change-admissibility/v1'::text,
                  'BLOCK'::text,
                  'BLOCK_UNKNOWN_HOST_IDENTITY'::text,
                  NULL::text;
                RETURN;
              END IF;

              IF facts.proposer_kind = 'MODEL' THEN
                expected_closure := facts.work_order_packet->>'closure_digest';
                IF facts.work_order_id IS NULL
                   OR facts.work_order_protocol <> 'model_change_v0'
                   OR facts.work_order_campaign_id <> facts.episode_campaign_id
                   OR facts.work_order_packet->'episode'->>'id' <> facts.episode_id::text
                   OR facts.work_order_packet->'conceptual_object'->>'id'
                      <> facts.conceptual_object_id::text
                   OR facts.work_order_packet->'manifest'->>'id' <> facts.manifest_id::text
                   OR facts.work_order_packet->'starting_artifact'->>'id'
                      <> facts.starting_artifact_id::text THEN
                  expected_closure := NULL;
                END IF;
              ELSIF facts.proposer_kind = 'HOST_DERIVED' THEN
                expected_repair_key := encode(
                  sha256(
                    convert_to(
                      'repair-v1|'
                      || coalesce(facts.repair_blocked_decision_id::text, '') || '|'
                      || facts.source_assertion_id::text || '|'
                      || coalesce(facts.repair_actor_id::text, '') || '|'
                      || coalesce(facts.repair_action, '') || '|'
                      || coalesce(facts.blocked_closure_digest, '') || '|'
                      || coalesce(facts.repair_adapter_profile, '') || '|'
                      || coalesce(facts.repair_idempotency_key, ''),
                      'UTF8'
                    )
                  ),
                  'hex'
                );
                IF facts.parent_id IS NULL
                   OR facts.blocked_proposal_id <> facts.parent_id
                   OR facts.repair_id IS NULL
                   OR facts.repair_key IS NULL
                   OR facts.repair_key <> expected_repair_key THEN
                  expected_closure := NULL;
                ELSE
                  expected_closure := facts.repair_key;
                END IF;
              ELSE
                expected_closure := NULL;
              END IF;

              IF expected_closure IS NULL
                 OR facts.closure_digest <> expected_closure
                 OR facts.input_revision <> facts.current_input_revision
                 OR facts.starting_artifact_id <> facts.episode_starting_artifact_id
                 OR facts.object_episode_id <> facts.episode_id
                 OR facts.object_manifest_id <> facts.manifest_id
                 OR facts.manifest_episode_id <> facts.episode_id
                 OR facts.manifest_artifact_id <> facts.starting_artifact_id
                 OR facts.document_episode_id <> facts.episode_id
                 OR EXISTS (
                   SELECT 1
                   FROM campaign_invalidationevent invalidation
                   WHERE (
                     invalidation.descendant_type = 'PROPOSAL'
                     AND invalidation.descendant_id = facts.id
                   ) OR (
                     invalidation.descendant_type = 'OBJECT'
                     AND invalidation.descendant_id = facts.conceptual_object_id
                   )
                 ) THEN
                RETURN QUERY SELECT
                  'model-change-admissibility/v1'::text,
                  'BLOCK'::text,
                  'BLOCK_STALE_CLOSURE'::text,
                  coalesce(expected_closure, facts.closure_digest)::text;
                RETURN;
              END IF;

              IF facts.operation <> jsonb_build_object(
                   'kind', facts.manifest_allowed_operation,
                   'target_ref', facts.manifest_target_ref,
                   'value', facts.assertion_value::text,
                   'unit', facts.assertion_unit
                 )
                 OR facts.manifest_allowed_operation <> 'set_numeric_value'
                 OR facts.manifest_target_unit <> facts.assertion_unit THEN
                RETURN QUERY SELECT
                  'model-change-admissibility/v1'::text,
                  'BLOCK'::text,
                  'BLOCK_INVALID_OPERATION'::text,
                  expected_closure::text;
                RETURN;
              END IF;

              IF facts.manifest_target_ref = 'FY25_REVENUE_USDM'
                 AND facts.document_class = 'EARNINGS_RELEASE_8K' THEN
                RETURN QUERY SELECT
                  'model-change-admissibility/v1'::text,
                  'BLOCK'::text,
                  'BLOCK_WRONG_DOCUMENT_CLASS'::text,
                  expected_closure::text;
              ELSIF (
                  facts.manifest_target_ref = 'FY25_REVENUE_USDM'
                  AND facts.document_class = 'FILED_ANNUAL_REPORT_10K'
                ) OR (
                  facts.manifest_target_ref = 'FY2025_PRELIMINARY_EARNINGS_FLASH_REVENUE'
                  AND facts.document_class = 'EARNINGS_RELEASE_8K'
                ) THEN
                RETURN QUERY SELECT
                  'model-change-admissibility/v1'::text,
                  'PASS'::text,
                  'PASS_EXACT_CLOSURE'::text,
                  expected_closure::text;
              ELSE
                RETURN QUERY SELECT
                  'model-change-admissibility/v1'::text,
                  'UNSUPPORTED'::text,
                  'UNSUPPORTED_TARGET_SOURCE_PAIR'::text,
                  expected_closure::text;
              END IF;
            END;
            $$;

            CREATE OR REPLACE FUNCTION campaign_model_change_decision_guard_v1()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE expected record;
            BEGIN
              SELECT * INTO expected
              FROM campaign_model_change_expected_admission_v1(NEW.proposal_id);
              IF expected.validator_version IS NULL
                 OR NEW.validator_version <> expected.validator_version
                 OR NEW.outcome <> expected.outcome
                 OR NEW.reason_code <> expected.reason_code
                 OR NEW.closure_digest <> expected.closure_digest THEN
                RAISE EXCEPTION 'admissibility decision differs from canonical database result';
              END IF;
              RETURN NEW;
            END;
            $$;

            CREATE TRIGGER model_change_decision_guard_v1
            BEFORE INSERT ON campaign_admissibilitydecision
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_decision_guard_v1();

            CREATE OR REPLACE FUNCTION campaign_model_change_candidate_guard()
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
                JOIN campaign_artifactmanifestversion manifest
                  ON manifest.id = proposal.manifest_id
                WHERE decision.id = NEW.candidate_from_pass_id
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
                FROM campaign_model_change_expected_admission_v1(
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
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_candidate_guard();

            CREATE OR REPLACE FUNCTION campaign_model_change_receipt_guard_v1()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE expected record;
            BEGIN
              SELECT * INTO expected
              FROM campaign_model_change_expected_admission_v1(
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

            CREATE TRIGGER model_change_receipt_guard_v1
            BEFORE INSERT ON campaign_calculationreceipt
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_receipt_guard_v1();

            CREATE OR REPLACE FUNCTION campaign_model_change_candidate_complete_v1()
            RETURNS trigger LANGUAGE plpgsql AS $$
            DECLARE receipt_count integer;
            DECLARE exact_count integer;
            BEGIN
              IF NEW.role <> 'candidate' THEN
                RETURN NEW;
              END IF;
              SELECT
                count(*),
                count(*) FILTER (
                  WHERE receipt.pass_decision_id = NEW.candidate_from_pass_id
                    AND receipt.episode_id = proposal.episode_id
                    AND receipt.manifest_id = proposal.manifest_id
                    AND receipt.input_digest = parent.digest
                    AND receipt.output_digest = NEW.digest
                    AND receipt.closure_digest = proposal.closure_digest
                    AND receipt.formula_errors = '[]'::jsonb
                )
                INTO receipt_count, exact_count
              FROM campaign_calculationreceipt receipt
              JOIN campaign_admissibilitydecision decision
                ON decision.id = NEW.candidate_from_pass_id
              JOIN campaign_modelchangeproposal proposal
                ON proposal.id = decision.proposal_id
              JOIN campaign_artifactversion parent ON parent.id = NEW.parent_id
              WHERE receipt.candidate_id = NEW.id;
              IF receipt_count <> 1 OR exact_count <> 1 THEN
                RAISE EXCEPTION 'candidate requires one exact calculation receipt at commit';
              END IF;
              RETURN NEW;
            END;
            $$;

            CREATE CONSTRAINT TRIGGER model_change_candidate_complete_v1
            AFTER INSERT ON campaign_artifactversion
            DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW
            WHEN (NEW.role = 'candidate')
            EXECUTE FUNCTION campaign_model_change_candidate_complete_v1();

            CREATE OR REPLACE FUNCTION campaign_model_change_outcome_guard_v1()
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
                FROM campaign_model_change_expected_admission_v1(
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

            CREATE TRIGGER model_change_outcome_guard_v1
            BEFORE INSERT ON campaign_modelchangeoutcome
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_outcome_guard_v1();

            CREATE TRIGGER model_change_outcome_append_only
            BEFORE UPDATE OR DELETE ON campaign_modelchangeoutcome
            FOR EACH ROW EXECUTE FUNCTION campaign_model_change_append_only();
            """
        )


def remove_repair_guards(apps, schema_editor) -> None:
    with schema_editor.connection.cursor() as cursor:
        for table in (
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
            "campaign_modelchangeoutcome",
        ):
            cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
            if cursor.fetchone() is not None:
                raise RuntimeError(
                    "refusing destructive model-change repair reverse while canonical facts exist"
                )
        if schema_editor.connection.vendor != "postgresql":
            return
        cursor.execute(
            """
            DROP TRIGGER IF EXISTS model_change_outcome_append_only
              ON campaign_modelchangeoutcome;
            DROP TRIGGER IF EXISTS model_change_outcome_guard_v1
              ON campaign_modelchangeoutcome;
            DROP FUNCTION IF EXISTS campaign_model_change_outcome_guard_v1();
            DROP TRIGGER IF EXISTS model_change_candidate_complete_v1
              ON campaign_artifactversion;
            DROP FUNCTION IF EXISTS campaign_model_change_candidate_complete_v1();
            DROP TRIGGER IF EXISTS model_change_receipt_guard_v1
              ON campaign_calculationreceipt;
            DROP FUNCTION IF EXISTS campaign_model_change_receipt_guard_v1();
            DROP TRIGGER IF EXISTS model_change_decision_guard_v1
              ON campaign_admissibilitydecision;
            DROP FUNCTION IF EXISTS campaign_model_change_decision_guard_v1();
            DROP TRIGGER IF EXISTS model_change_candidate_guard
              ON campaign_artifactversion;
            DROP FUNCTION IF EXISTS campaign_model_change_candidate_guard();
            DROP FUNCTION IF EXISTS campaign_model_change_expected_admission_v1(uuid);

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
                  AND manifest.artifact_id = NEW.parent_id;
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
            """
        )


class Migration(migrations.Migration):
    dependencies = [
        ("campaign", "0006_model_change_v0_guards"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="amendment",
            name="adapter_profile",
            field=models.CharField(blank=True, default="", max_length=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="amendment",
            name="idempotency_key",
            field=models.CharField(blank=True, default="", max_length=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="amendment",
            name="repair_key",
            field=models.CharField(
                blank=True, editable=False, max_length=64, null=True, unique=True
            ),
        ),
        migrations.CreateModel(
            name="ModelChangeOutcome",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "stage",
                    models.CharField(
                        choices=[
                            ("RUNTIME_FAILURE", "Runtime failure"),
                            ("WORKER_REFUSAL", "Worker refusal"),
                            ("CALCULATION_FAILURE", "Calculation failure"),
                        ],
                        max_length=32,
                    ),
                ),
                ("reason_code", models.CharField(max_length=80)),
                ("public_message", models.TextField()),
                (
                    "next_action",
                    models.CharField(
                        choices=[
                            ("RETRY_WORK", "Retry this work"),
                            ("RETRY_CANDIDATE", "Retry creating the candidate"),
                            ("NONE", "No next action"),
                        ],
                        max_length=24,
                    ),
                ),
                ("closure_digest", models.CharField(max_length=64)),
                ("attempt_key", models.CharField(max_length=64)),
                ("protocol_version", models.CharField(max_length=80)),
                ("technical_details", models.JSONField(default=dict, editable=False)),
                ("digest", models.CharField(editable=False, max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "blocked_decision",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="model_change_outcomes",
                        to="campaign.admissibilitydecision",
                    ),
                ),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="model_change_outcomes",
                        to="campaign.modelchangeepisode",
                    ),
                ),
                (
                    "work_order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="model_change_outcomes",
                        to="campaign.workorder",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("stage", "attempt_key"),
                        name="model_change_outcome_attempt_once",
                    )
                ]
            },
        ),
        migrations.RunPython(install_repair_guards, remove_repair_guards),
        migrations.AddConstraint(
            model_name="artifactversion",
            constraint=models.UniqueConstraint(
                condition=models.Q(candidate_from_pass__isnull=False),
                fields=("candidate_from_pass",),
                name="model_change_one_candidate_per_pass",
            ),
        ),
        migrations.AddConstraint(
            model_name="amendment",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    action="USE_FILED_ANNUAL_REPORT",
                    blocked_decision__isnull=False,
                ),
                fields=("blocked_decision",),
                name="model_change_one_filed_repair_per_block",
            ),
        ),
    ]
