from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError, connection, transaction
from django.test import TestCase, override_settings

from product.campaign import services as campaign_services
from product.campaign.model_change.services import NETWORK_POLICY, PROTOCOL_VERSION

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
