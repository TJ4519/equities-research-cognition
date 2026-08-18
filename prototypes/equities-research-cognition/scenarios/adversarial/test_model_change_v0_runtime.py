from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError, connection, transaction
from django.test import TestCase, override_settings

from product.campaign import services as campaign_services
from product.campaign.model_change.services import (
    MODEL_OUTPUT,
    NETWORK_POLICY,
    OutcomeService,
    PROTOCOL_VERSION,
    ModelChangeRejected,
    ProjectionService,
    ProposalParser,
    RunService,
    WorkCompiler,
    _collect_model_change_artifacts,
)
from product.campaign.models import Artifact, ModelChangeOutcome

from scenarios.adversarial.test_model_change_v0_services import CaseAFixtureMixin


class ModelChangeRuntimeTests(CaseAFixtureMixin, TestCase):
    def test_closed_protocol_launcher_omits_search_and_materializes_exact_inputs(self) -> None:
        order = self.compile_order()
        campaign_services._prepare_output_root(order)
        launcher, _ = campaign_services._control_files(order)
        self.assertNotIn(b"--search", launcher.read_bytes())
        self.assertIn(b"trust_level", launcher.read_bytes())
        dispatch = campaign_services._dispatch_path(order)
        self.assertEqual(order.packet, json.loads(dispatch.read_bytes()))
        input_root = Path(order.campaign.artifact_root) / "dispatches" / f"{order.pk}.inputs"
        self.assertEqual(
            {Path(row["materialized_path"]).name for row in order.packet["job_input_files"]},
            {item.name for item in input_root.iterdir()},
        )
        campaign_services._verify_materialized_bound_inputs(order)

    @override_settings(LANGFUSE_TARGET_BASE_URL="https://cloud.langfuse.com")
    def test_existing_protocol_launcher_keeps_search(self) -> None:
        workbook = bytes(self.episode.starting_artifact.content)
        campaign = campaign_services.create_owned_job(
            director=self.owner,
            title="Existing bounded job",
            issuer_or_security="Synthetic issuer",
            equities_decision_use="Synthetic review",
            evidence_cutoff="2025-10-03",
            question="Produce a bounded result",
            run_instruction="Use only the supplied exact inputs.",
            starting_artifact=SimpleUploadedFile(
                "starting.xlsx",
                workbook,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            sources=[SimpleUploadedFile("source.txt", b"captured", content_type="text/plain")],
        )
        order = campaign.work_orders.get()
        campaign_services._prepare_output_root(order)
        launcher, _ = campaign_services._control_files(order)
        self.assertIn(b"--search", launcher.read_bytes())

    def test_exact_acknowledgement_and_output_are_accepted_only_with_attestation(self) -> None:
        order = self.compile_order()
        proposal = self.worker_value(order)
        outputs = {
            "model-change-output.json": json.dumps(
                proposal, sort_keys=True, separators=(",", ":")
            ).encode(),
            "run-acknowledgement.json": json.dumps(
                {
                    "schema": "model-change-run-acknowledgement/v0",
                    "episode_id": order.packet["episode"]["id"],
                    "episode_digest": order.packet["episode"]["sha256"],
                    "work_order_id": str(order.pk),
                    "closure_digest": order.packet["closure_digest"],
                    "inputs": order.packet["job_inputs"],
                    "network_policy": NETWORK_POLICY,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode(),
        }
        attestation = {
            "schema_version": "work-order-artifact-attestation/v1",
            "campaign_id": str(order.campaign_id),
            "work_order_id": str(order.pk),
            "logical_role_id": str(order.logical_role_id),
            "artifacts": [
                {
                    "relative_path": name,
                    "byte_length": len(content),
                    "sha256": sha256(content).hexdigest(),
                }
                for name, content in sorted(outputs.items())
            ],
            "authority": "worker_candidate_attestation",
        }
        observed = campaign_services._validate_artifact_attestation(
            order,
            json.dumps(attestation).encode(),
            outputs,
        )
        self.assertEqual("worker_candidate_attestation", observed["authority"])
        outputs["extra.txt"] = b"not permitted"
        with self.assertRaisesRegex(
            campaign_services.CampaignRejected, "attestation"
        ):
            campaign_services._validate_artifact_attestation(
                order, json.dumps(attestation).encode(), outputs
            )

    def test_packet_rederivation_refuses_stale_protocol_file(self) -> None:
        order = self.compile_order()
        self.assertEqual(PROTOCOL_VERSION, order.packet["protocol_version"])
        changed = dict(order.packet)
        changed["closure_digest"] = "0" * 64
        order.packet = changed
        with self.assertRaisesRegex(
            campaign_services.CampaignRejected, "model change"
        ):
            campaign_services._validate_runtime_contract(order)

    def test_direct_sql_cannot_rewrite_model_change_work_authority(self) -> None:
        order = self.compile_order()
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE campaign_workorder SET packet = %s WHERE id = %s",
                    ["{}", order.pk],
                )
        order.refresh_from_db()
        self.assertEqual("model_change_v0", order.packet["protocol"])

    def test_runtime_failure_survives_restart_and_successor_preserves_attempt(self) -> None:
        order = self.compile_order()
        with patch(
            "product.campaign.model_change.services.campaign_services.launch_role",
            side_effect=ValueError("forced pinned control failure"),
        ):
            outcome, decision = RunService.run(self.owner, order)
        self.assertIsNone(decision)
        self.assertEqual(ModelChangeOutcome.Stage.RUNTIME_FAILURE, outcome.stage)
        self.assertEqual(ModelChangeOutcome.NextAction.RETRY_WORK, outcome.next_action)
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        self.assertEqual(outcome.pk, resumed["technical_outcome"].pk)
        self.assertEqual("RETRY_WORK", resumed["next_action"])
        successor = WorkCompiler.compile(
            self.episode,
            self.object,
            resumed["object_authorities"],
            self.manifest,
            self.assertions,
            PROTOCOL_VERSION,
        )
        self.assertNotEqual(order.pk, successor.pk)
        self.assertTrue(ModelChangeOutcome.objects.filter(pk=outcome.pk).exists())

    @override_settings(
        MODEL_CHANGE_RUNTIME_READY_SECONDS=0,
        MODEL_CHANGE_RUNTIME_POLL_LIMIT=1,
    )
    def test_readiness_and_collection_failures_each_persist_for_restart(self) -> None:
        readiness_order = self.compile_order()
        with (
            patch("product.campaign.model_change.services.campaign_services.launch_role"),
            patch("product.campaign.model_change.services.campaign_services.refresh_status"),
            patch(
                "product.campaign.model_change.services.campaign_services._target_index",
                side_effect=campaign_services.CampaignRejected("forced not ready"),
            ),
            patch("product.campaign.model_change.services.time.sleep"),
        ):
            readiness, decision = RunService.run(self.owner, readiness_order)
        self.assertIsNone(decision)
        self.assertEqual(ModelChangeOutcome.Stage.RUNTIME_FAILURE, readiness.stage)
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        self.assertEqual(readiness.pk, resumed["technical_outcome"].pk)

        collection_order = WorkCompiler.compile(
            self.episode,
            self.object,
            resumed["object_authorities"],
            self.manifest,
            self.assertions,
            PROTOCOL_VERSION,
        )
        output_root = Path(self.temporary.name) / "collection-failure-output"
        output_root.mkdir()
        for name in (
            MODEL_OUTPUT,
            "run-acknowledgement.json",
            collection_order.packet["output_contract"]["attestation_path"],
        ):
            (output_root / name).write_bytes(b"sealed")
        with (
            patch("product.campaign.model_change.services.campaign_services.launch_role"),
            patch("product.campaign.model_change.services.campaign_services.refresh_status"),
            patch(
                "product.campaign.model_change.services.campaign_services._target_index",
                return_value=0,
            ),
            patch("product.campaign.model_change.services.campaign_services.send_dispatch"),
            patch(
                "product.campaign.model_change.services.campaign_services._completion_observed",
                return_value=True,
            ),
            patch(
                "product.campaign.model_change.services.campaign_services._output_root",
                return_value=output_root,
            ),
            patch(
                "product.campaign.model_change.services._collect_model_change_artifacts",
                side_effect=campaign_services.CampaignRejected("forced collection failure"),
            ),
        ):
            collection, decision = RunService.run(self.owner, collection_order)
        self.assertIsNone(decision)
        self.assertEqual(ModelChangeOutcome.Stage.RUNTIME_FAILURE, collection.stage)
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        self.assertEqual(collection.pk, resumed["technical_outcome"].pk)
        self.assertEqual("RETRY_WORK", resumed["next_action"])
        self.assertEqual(0, self.episode.model_change_proposals.count())

    def test_successor_collection_ignores_failed_predecessor_output_root(self) -> None:
        failed_order = self.compile_order()
        campaign_services._prepare_output_root(failed_order)
        failure = OutcomeService.record_runtime_failure(
            failed_order, "FORCED_PREDECESSOR_FAILURE"
        )
        restarted = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        successor = WorkCompiler.compile(
            self.episode,
            self.object,
            restarted["object_authorities"],
            self.manifest,
            self.assertions,
            PROTOCOL_VERSION,
        )
        sealed = Path(self.temporary.name) / "targeted-successor-sealed"
        sealed.mkdir()
        files = {
            MODEL_OUTPUT: b"{}",
            "run-acknowledgement.json": b"{}",
            successor.packet["output_contract"]["attestation_path"]: b"{}",
        }
        with (
            patch(
                "product.campaign.model_change.services.campaign_services._completion_observed",
                return_value=True,
            ),
            patch(
                "product.campaign.model_change.services.campaign_services._verify_materialized_bound_inputs"
            ),
            patch(
                "product.campaign.model_change.services.campaign_services._seal_output_root",
                return_value=sealed,
            ),
            patch(
                "product.campaign.model_change.services.campaign_services._output_files",
                return_value=files,
            ),
            patch(
                "product.campaign.model_change.services.campaign_services._validate_artifact_attestation"
            ),
            patch(
                "product.campaign.model_change.services.campaign_services.collect_artifacts",
                side_effect=AssertionError("campaign-wide collection must not run"),
            ),
        ):
            self.assertEqual(3, _collect_model_change_artifacts(successor, self.owner))
        self.assertEqual(failure.pk, failed_order.model_change_outcomes.get().pk)
        self.assertEqual(0, failed_order.artifacts.count())
        self.assertEqual(3, successor.artifacts.count())

    @override_settings(
        MODEL_CHANGE_RUNTIME_READY_SECONDS=0,
        MODEL_CHANGE_RUNTIME_POLL_LIMIT=1,
    )
    def test_worker_refusal_survives_restart_and_stale_output_cannot_displace_it(self) -> None:
        order = self.compile_order()
        refusal = {
            "schema": "model-change-refusal/v0",
            "episode_id": str(self.episode.pk),
            "reason": "The captured evidence does not support a bounded proposal.",
        }
        refusal_bytes = json.dumps(refusal, sort_keys=True).encode()
        Artifact.objects.create(
            campaign=order.campaign,
            work_order=order,
            kind="candidate",
            relative_path=MODEL_OUTPUT,
            version=1,
            media_type="application/json",
            content=refusal_bytes,
            digest=sha256(refusal_bytes).hexdigest(),
        )
        output_root = Path(self.temporary.name) / "refusal-output"
        output_root.mkdir()
        for name in (
            MODEL_OUTPUT,
            "run-acknowledgement.json",
            order.packet["output_contract"]["attestation_path"],
        ):
            (output_root / name).write_bytes(b"sealed")
        with (
            patch(
                "product.campaign.model_change.services.campaign_services.launch_role"
            ),
            patch(
                "product.campaign.model_change.services.campaign_services.refresh_status"
            ),
            patch(
                "product.campaign.model_change.services.campaign_services._target_index",
                return_value=0,
            ),
            patch(
                "product.campaign.model_change.services.campaign_services.send_dispatch"
            ),
            patch(
                "product.campaign.model_change.services.campaign_services._completion_observed",
                return_value=True,
            ),
            patch(
                "product.campaign.model_change.services.campaign_services._output_root",
                return_value=output_root,
            ),
            patch(
                "product.campaign.model_change.services._collect_model_change_artifacts"
            ),
        ):
            outcome, decision = RunService.run(self.owner, order)
        self.assertIsNone(decision)
        self.assertEqual(ModelChangeOutcome.Stage.WORKER_REFUSAL, outcome.stage)
        self.assertEqual(refusal["reason"], outcome.technical_details["reason"])
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        self.assertEqual(outcome.pk, resumed["technical_outcome"].pk)
        self.assertEqual("RETRY_WORK", resumed["next_action"])
        with self.assertRaisesRegex(ModelChangeRejected, "completed attempt"):
            ProposalParser.parse(self.worker_value(order), order.packet)
