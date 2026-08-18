from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shlex
from unittest.mock import patch

from django.conf import settings
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


def launcher_argv(path: Path) -> list[str]:
    command = path.read_text().splitlines()[-1]
    return shlex.split(command.removeprefix("exec "))


def launcher_trust_paths(path: Path) -> list[Path]:
    argv = launcher_argv(path)
    values = [argv[index + 1] for index, item in enumerate(argv) if item == "-c"]
    prefix = "projects."
    suffix = '.trust_level="trusted"'
    return [
        Path(json.loads(value[len(prefix) : -len(suffix)]))
        for value in values
        if value.startswith(prefix) and value.endswith(suffix)
    ]


class ModelChangeRuntimeTests(CaseAFixtureMixin, TestCase):
    def test_closed_protocol_launcher_trusts_the_exact_output_root_used_by_cd(self) -> None:
        order = self.compile_order()
        output_root = campaign_services._prepare_output_root(order)

        launcher, config = campaign_services._control_files(order)
        argv = launcher_argv(launcher)

        self.assertEqual(str(output_root), argv[argv.index("--cd") + 1])
        self.assertEqual(
            [campaign_services.PROTOTYPE_ROOT.parents[1], output_root],
            launcher_trust_paths(launcher),
        )
        forbidden = {
            Path("/"),
            Path.home(),
            campaign_services.PROTOTYPE_ROOT.parents[2],
            Path(order.campaign.artifact_root),
            Path(order.campaign.artifact_root).parent,
            output_root.parent,
            output_root.parent / "unrelated-sibling",
        }
        self.assertTrue(forbidden.isdisjoint(launcher_trust_paths(launcher)))
        self.assertEqual(str(settings.CAMPAIGN_CODEX_BINARY), argv[0])
        self.assertEqual(
            ["--sandbox", "workspace-write", "--ask-for-approval", "never"],
            argv[1:5],
        )
        self.assertNotIn("--search", argv)
        self.assertIn(
            f'default_codex = "{settings.CAMPAIGN_CODEX_MODEL}"'.encode(),
            config.read_bytes(),
        )

    def test_closed_protocol_launcher_refuses_a_non_owner_only_output_root(self) -> None:
        order = self.compile_order()
        output_root = campaign_services._prepare_output_root(order)
        output_root.chmod(0o750)

        with self.assertRaisesRegex(
            campaign_services.CampaignRejected, "owner-only"
        ):
            campaign_services._control_files(order)

    def test_closed_protocol_launcher_rechecks_that_output_root_is_not_a_symlink(self) -> None:
        order = self.compile_order()
        output_root = campaign_services._output_root(order)
        output_root.parent.mkdir(parents=True)
        target = output_root.parent / "foreign-target"
        target.mkdir(mode=0o700)
        output_root.symlink_to(target, target_is_directory=True)

        with self.assertRaisesRegex(
            campaign_services.CampaignRejected, "symlink"
        ):
            campaign_services._control_files(order)

    def test_closed_protocol_launcher_refuses_an_unresolved_output_root(self) -> None:
        order = self.compile_order()
        campaign_root = Path(order.campaign.artifact_root)
        (campaign_root.parent / "unused-segment").mkdir()
        unresolved_campaign_root = (
            campaign_root.parent / "unused-segment" / ".." / campaign_root.name
        )
        order.campaign.artifact_root = str(unresolved_campaign_root)
        order.packet = deepcopy(order.packet)
        order.packet["output_contract"] = campaign_services._output_contract(
            order.campaign, order.pk, order.protocol
        )
        campaign_services._prepare_output_root(order)

        with self.assertRaisesRegex(
            campaign_services.CampaignRejected, "canonical"
        ):
            campaign_services._control_files(order)

    def test_closed_protocol_launcher_refuses_a_missing_output_root(self) -> None:
        order = self.compile_order()

        with self.assertRaisesRegex(
            campaign_services.CampaignRejected, "unavailable at launch"
        ):
            campaign_services._control_files(order)

    def test_closed_protocol_launcher_refuses_a_cross_campaign_output_contract(self) -> None:
        order = self.compile_order()
        order.packet = deepcopy(order.packet)
        order.packet["output_contract"] = deepcopy(
            order.packet["output_contract"]
        )
        order.packet["output_contract"]["output_root"] = str(
            Path(self.temporary.name)
            / "foreign-campaign"
            / "work"
            / str(order.pk)
            / "out"
        )

        with self.assertRaisesRegex(
            campaign_services.CampaignRejected, "custody contract changed"
        ):
            campaign_services._control_files(order)

    def test_each_work_order_trusts_only_its_own_output_root(self) -> None:
        first = self.compile_order()
        first_root = campaign_services._prepare_output_root(first)
        first_launcher, _ = campaign_services._control_files(first)
        OutcomeService.record_runtime_failure(first, "FORCED_TEST_RETRY")
        resumed = ProjectionService.resume(
            self.owner, self.episode.job_id, self.episode.pk
        )
        successor = WorkCompiler.compile(
            self.episode,
            self.object,
            resumed["object_authorities"],
            self.manifest,
            self.assertions,
            PROTOCOL_VERSION,
        )
        successor_root = campaign_services._prepare_output_root(successor)
        successor_launcher, _ = campaign_services._control_files(successor)

        repository_root = campaign_services.PROTOTYPE_ROOT.parents[1]
        self.assertNotEqual(first_root, successor_root)
        self.assertNotEqual(first_launcher.name, successor_launcher.name)
        self.assertNotEqual(first_launcher.read_bytes(), successor_launcher.read_bytes())
        self.assertEqual(
            [repository_root, first_root], launcher_trust_paths(first_launcher)
        )
        self.assertEqual(
            [repository_root, successor_root],
            launcher_trust_paths(successor_launcher),
        )
        self.assertNotIn(first_root, launcher_trust_paths(successor_launcher))

    def test_exact_output_root_trust_survives_shell_and_toml_quoting(self) -> None:
        order = self.compile_order()
        old_campaign_root = Path(order.campaign.artifact_root)
        special_parent = (
            old_campaign_root.parent
            / "campaign root 'single' \"double\" [v0] $literal"
        )
        special_parent.mkdir()
        special_campaign_root = special_parent / old_campaign_root.name
        old_campaign_root.rename(special_campaign_root)
        order.campaign.artifact_root = str(special_campaign_root.resolve())
        order.packet = deepcopy(order.packet)
        order.packet["output_contract"] = campaign_services._output_contract(
            order.campaign, order.pk, order.protocol
        )
        output_root = campaign_services._prepare_output_root(order)

        launcher, _ = campaign_services._control_files(order)
        argv = launcher_argv(launcher)

        self.assertEqual(str(output_root), argv[argv.index("--cd") + 1])
        self.assertEqual(output_root, launcher_trust_paths(launcher)[-1])

    def test_launcher_generation_does_not_modify_persistent_codex_config(self) -> None:
        order = self.compile_order()
        campaign_services._prepare_output_root(order)
        fixture_root = Path(self.temporary.name) / "persistent-config-fixture"
        fake_repository = fixture_root / "repository"
        fake_package = fake_repository / "prototypes" / "equities-research-cognition"
        fake_workbenches = fake_package / "workbenches"
        fake_home = fixture_root / "home"
        user_config = fake_home / ".codex" / "config.toml"
        project_config = fake_repository / ".codex" / "config.toml"
        for path, content in (
            (user_config, b"user-config-must-not-change\n"),
            (project_config, b"project-config-must-not-change\n"),
        ):
            path.parent.mkdir(parents=True)
            path.write_bytes(content)
        before = {
            path: (path.stat().st_mtime_ns, sha256(path.read_bytes()).hexdigest())
            for path in (user_config, project_config)
        }
        for _, _, directory, _ in campaign_services.ACTIVE_WORKBENCHES:
            source = campaign_services.WORKBENCH_ROOT / directory / "protocol.md"
            target = fake_workbenches / directory / "protocol.md"
            target.parent.mkdir(parents=True)
            target.write_bytes(source.read_bytes())

        with (
            patch.object(campaign_services, "PROTOTYPE_ROOT", fake_package),
            patch.object(campaign_services, "WORKBENCH_ROOT", fake_workbenches),
            patch.object(Path, "home", return_value=fake_home),
        ):
            launcher, _ = campaign_services._control_files(order)

        self.assertEqual(fake_repository, launcher_trust_paths(launcher)[0])
        self.assertEqual(
            before,
            {
                path: (path.stat().st_mtime_ns, sha256(path.read_bytes()).hexdigest())
                for path in (user_config, project_config)
            },
        )

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
        trace_args = ["-c", 'trace.\"packet012\"=\"unchanged\"']
        with patch.object(
            campaign_services,
            "build_codex_trace_arguments",
            return_value=trace_args,
        ):
            launcher, _ = campaign_services._control_files(order)
        argv = launcher_argv(launcher)
        self.assertIn("--search", argv)
        self.assertEqual([], launcher_trust_paths(launcher))
        self.assertEqual(str(settings.CAMPAIGN_CODEX_BINARY), argv[0])
        self.assertEqual(
            ["--sandbox", "workspace-write", "--ask-for-approval", "never"],
            argv[1:5],
        )
        expected = (
            "#!/bin/sh\nset -eu\n"
            "exec "
            + shlex.quote(str(Path(settings.CAMPAIGN_CODEX_BINARY)))
            + " --sandbox workspace-write --ask-for-approval never --search "
            + "--cd "
            + shlex.quote(str(campaign_services._output_root(order)))
            + "  "
            + " ".join(shlex.quote(item) for item in trace_args)
            + ' -m "$1"\n'
        ).encode()
        self.assertEqual(expected, launcher.read_bytes())

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
