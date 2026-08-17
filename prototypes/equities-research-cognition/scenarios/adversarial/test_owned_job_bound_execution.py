from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import uuid

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError, connection, transaction
from django.test import Client, TestCase
from django.urls import reverse

from product.campaign.models import (
    Artifact,
    ArtifactVersion,
    Proposal,
    ProposalDisposition,
    ResearchCampaign,
    RuntimeEvent,
    RunSpecVersion,
    WorkOrder,
    canonical_bytes,
    canonical_digest,
)
from product.campaign.services import (
    CampaignRejected,
    _approved_order,
    _dispatch_path,
    _validate_runtime_contract,
    canonical_bound_work_packet,
    create_campaign,
    create_owned_job,
    record_proposal,
    stop_campaign,
)
from harness.ntm.adapter import ExecutionResult
from scenarios.adversarial._tue2_runtime_support import tracked_send_response


def mark_worker_complete(
    order: WorkOrder, *, materialize_inputs: bool = True
) -> None:
    if materialize_inputs:
        _dispatch_path(order)
    send_id = uuid.uuid4()
    send_payload = {
        "id": str(send_id),
        "campaign": str(order.campaign_id),
        "work_order": str(order.pk),
        "kind": RuntimeEvent.Kind.SEND,
        "generation": 1,
        "request": {"argv": ["mechanical-test-only-send", "--panes=2"]},
        "response": tracked_send_response(order),
        "succeeded": True,
    }
    RuntimeEvent.objects.create(
        id=send_id,
        campaign=order.campaign,
        work_order=order,
        kind=RuntimeEvent.Kind.SEND,
        request=send_payload["request"],
        response=send_payload["response"],
        succeeded=True,
        digest=canonical_digest(send_payload),
    )
    status_id = uuid.uuid4()
    status_payload = {
        "id": str(status_id),
        "campaign": str(order.campaign_id),
        "work_order": str(order.pk),
        "kind": RuntimeEvent.Kind.STATUS,
        "generation": 1,
        "request": {"argv": ["mechanical-test-only-completion", "--panes=2"]},
        "response": {
            "success": True,
            "session": order.campaign.ntm_session,
            "condition": "complete",
            "agents": [
                {
                    "pane": "%opaque-provider-pane",
                    "state": "WAITING",
                    "agent_type": "codex",
                }
            ],
        },
        "succeeded": True,
    }
    RuntimeEvent.objects.create(
        id=status_id,
        campaign=order.campaign,
        work_order=order,
        kind=RuntimeEvent.Kind.STATUS,
        request=status_payload["request"],
        response=status_payload["response"],
        succeeded=True,
        digest=canonical_digest(status_payload),
    )


def write_bound_outputs(
    order: WorkOrder,
    *,
    acknowledgement_inputs: list[dict[str, str]] | None = None,
    outcome_kind: str = "candidate",
    conflicting_disposition: bool = False,
) -> None:
    output = Path(order.packet["output_contract"]["output_root"])
    output.mkdir(parents=True, exist_ok=True)
    acknowledgement = canonical_bytes(
        {
            "schema_version": "bound-run-acknowledgement/v1",
            "campaign_id": str(order.campaign_id),
            "run_spec_id": str(order.run_spec_id),
            "run_spec_sha256": order.run_spec.digest,
            "work_order_id": str(order.pk),
            "inputs": (
                order.packet["job_inputs"]
                if acknowledgement_inputs is None
                else acknowledgement_inputs
            ),
        }
    )
    outcome = canonical_bytes(
        {
            "schema_version": "bound-run-outcome/v1",
            "kind": outcome_kind,
            "authority": "provisional_only",
            "summary": (
                "Propose 1,200 for consolidated GAAP revenue from the earnings release."
                if outcome_kind == "candidate"
                else "The supplied bytes cannot be interpreted by the available tools."
            ),
            "candidate": (
                {
                    "operation": "propose_value",
                    "target": "FY2025 consolidated GAAP revenue",
                    "value": 1200,
                    "unit": "USDm",
                    "source_basis": "earnings_release_nonfiling",
                }
                if outcome_kind == "candidate"
                else None
            ),
            "refusal": (
                (
                    "A candidate and refusal cannot coexist."
                    if conflicting_disposition
                    else None
                )
                if outcome_kind == "candidate"
                else "No installed tool can inspect the native artifact safely."
            ),
        }
    )
    payloads = {
        "outcome.json": outcome,
        "run-acknowledgement.json": acknowledgement,
    }
    for name, content in payloads.items():
        (output / name).write_bytes(content)
    rows = [
        {
            "relative_path": name,
            "byte_length": len(content),
            "sha256": sha256(content).hexdigest(),
        }
        for name, content in sorted(payloads.items())
    ]
    (output / "artifact-attestation.json").write_bytes(
        canonical_bytes(
            {
                "schema_version": "work-order-artifact-attestation/v1",
                "campaign_id": str(order.campaign_id),
                "work_order_id": str(order.pk),
                "logical_role_id": str(order.logical_role_id),
                "artifacts": rows,
                "authority": "worker_candidate_attestation",
            }
        )
    )


class OwnedJobBoundExecutionTests(TestCase):
    """MECHANICAL_REGRESSION_ONLY for the owned job and exact run boundary."""

    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        settings = self.settings(CAMPAIGN_ROOT=self.temp.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.director = get_user_model().objects.create_user(
            "director", password="local-password"
        )
        self.client.force_login(self.director)

    def create_job(self) -> tuple[ResearchCampaign, bytes, tuple[bytes, bytes]]:
        workbook_bytes = b"opaque-native-workbook-bytes\x00v1"
        filing_bytes = b"FY2025 consolidated GAAP revenue: 1,200; source class: filing"
        release_bytes = b"FY2025 consolidated GAAP revenue: 1,200; source class: earnings release"
        response = self.client.post(
            reverse("campaigns"),
            {
                "title": "Post-earnings model revision",
                "issuer_or_security": "Example Industrials",
                "equities_decision_use": (
                    "Update the owned model without silently adopting any proposal."
                ),
                "evidence_cutoff": "2026-08-13",
                "commissioned_question": (
                    "Which stated values should become a provisional model-change proposal?"
                ),
                "run_instruction": (
                    "Read the exact supplied files and return either one typed provisional "
                    "change proposal or a bounded refusal."
                ),
                "starting_artifact": SimpleUploadedFile(
                    "owned-model.xlsx",
                    workbook_bytes,
                    content_type=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                ),
                "sources": [
                    SimpleUploadedFile(
                        "annual-filing.txt", filing_bytes, content_type="text/plain"
                    ),
                    SimpleUploadedFile(
                        "earnings-release.txt", release_bytes, content_type="text/plain"
                    ),
                ],
            },
        )
        self.assertEqual(302, response.status_code, response.content)
        return (
            ResearchCampaign.objects.get(director=self.director),
            workbook_bytes,
            (filing_bytes, release_bytes),
        )

    def test_authenticated_upload_creates_one_bound_job_retrievable_after_restart(
        self,
    ) -> None:
        campaign, workbook_bytes, source_bytes = self.create_job()
        ArtifactVersion = apps.get_model("campaign", "ArtifactVersion")
        RunSpecVersion = apps.get_model("campaign", "RunSpecVersion")
        inputs = list(ArtifactVersion.objects.filter(campaign=campaign).order_by("role"))
        self.assertEqual(3, len(inputs))
        self.assertEqual(
            {
                sha256(workbook_bytes).hexdigest(),
                *(sha256(item).hexdigest() for item in source_bytes),
            },
            {item.digest for item in inputs},
        )
        self.assertEqual(
            {workbook_bytes, *source_bytes}, {bytes(item.content) for item in inputs}
        )
        spec = RunSpecVersion.objects.get(campaign=campaign)
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")
        self.assertEqual(spec.pk, order.run_spec_id)
        self.assertEqual(str(spec.pk), order.packet["run_spec"]["id"])
        self.assertEqual(spec.digest, order.packet["run_spec"]["sha256"])
        self.assertEqual(
            [
                {"id": str(item.pk), "sha256": item.digest}
                for item in sorted(inputs, key=lambda item: str(item.pk))
            ],
            order.packet["job_inputs"],
        )

        restarted = Client()
        restarted.force_login(self.director)
        page = restarted.get(reverse("campaign", args=[campaign.pk]))
        self.assertEqual(200, page.status_code)
        self.assertContains(page, "owned-model.xlsx")
        self.assertContains(page, "annual-filing.txt")
        self.assertContains(page, "earnings-release.txt")
        self.assertContains(page, str(spec.pk))
        self.assertContains(page, spec.digest)
        self.assertContains(page, "Provisional result only")
        starting = ArtifactVersion.objects.get(
            campaign=campaign, role=ArtifactVersion.Role.STARTING_ARTIFACT
        )
        download = restarted.get(
            reverse("campaign_input_artifact", args=[campaign.pk, starting.pk])
        )
        self.assertEqual(workbook_bytes, download.content)
        self.assertEqual(starting.digest, download["X-Content-SHA256"])
        outsider = get_user_model().objects.create_user("outsider")
        outside = Client()
        outside.force_login(outsider)
        self.assertEqual(
            404,
            outside.get(
                reverse("campaign_input_artifact", args=[campaign.pk, starting.pk])
            ).status_code,
        )

    def test_synthetic_wrong_source_candidate_survives_as_provisional_only(
        self,
    ) -> None:
        campaign, _, _ = self.create_job()
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")
        mark_worker_complete(order)
        write_bound_outputs(order)

        response = self.client.post(reverse("campaign_collect", args=[campaign.pk]))

        self.assertEqual(302, response.status_code, response.content)
        self.assertEqual(3, Artifact.objects.filter(work_order=order).count())
        outcome = json.loads(
            bytes(Artifact.objects.get(work_order=order, relative_path="outcome.json").content)
        )
        self.assertEqual("candidate", outcome["kind"])
        self.assertEqual("provisional_only", outcome["authority"])
        self.assertEqual(
            "FY2025 consolidated GAAP revenue", outcome["candidate"]["target"]
        )
        self.assertEqual(
            "earnings_release_nonfiling", outcome["candidate"]["source_basis"]
        )
        self.assertFalse(hasattr(order, "state_transition"))

        restarted = Client()
        restarted.force_login(self.director)
        page = restarted.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(page, "The worker acknowledged this exact job")
        self.assertContains(
            page,
            "Propose 1,200 for consolidated GAAP revenue from the earnings release.",
        )
        self.assertContains(page, "No workbook parsing")
        result = Artifact.objects.get(work_order=order, relative_path="outcome.json")
        download = restarted.get(
            reverse("campaign_artifact", args=[campaign.pk, result.pk])
        )
        self.assertEqual(bytes(result.content), download.content)
        self.assertEqual(result.digest, download["X-Content-SHA256"])

    def test_missing_exact_inputs_creates_nothing(self) -> None:
        response = self.client.post(
            reverse("campaigns"),
            {
                "title": "Incomplete job",
                "issuer_or_security": "Example Industrials",
                "equities_decision_use": "Update the owned model.",
                "evidence_cutoff": "2026-08-13",
                "commissioned_question": "Which value should change?",
                "run_instruction": "Return a provisional proposal or refusal.",
            },
        )

        self.assertEqual(409, response.status_code)
        self.assertEqual(0, ResearchCampaign.objects.count())
        self.assertEqual(0, ArtifactVersion.objects.count())
        self.assertEqual(0, RunSpecVersion.objects.count())
        self.assertEqual(0, WorkOrder.objects.count())
        self.assertEqual([], list(Path(self.temp.name).iterdir()))

    def test_job_input_population_is_bounded_and_atomic(self) -> None:
        with self.settings(
            CAMPAIGN_JOB_MAX_SOURCES=1,
            CAMPAIGN_JOB_MAX_INPUT_BYTES=8,
        ):
            too_many = self.client.post(
                reverse("campaigns"),
                {
                    "title": "Too many sources",
                    "issuer_or_security": "Example Industrials",
                    "equities_decision_use": "Update the owned model.",
                    "evidence_cutoff": "2026-08-13",
                    "commissioned_question": "Which value should change?",
                    "run_instruction": "Return a provisional proposal or refusal.",
                    "starting_artifact": SimpleUploadedFile("model.xlsx", b"model"),
                    "sources": [
                        SimpleUploadedFile("one.txt", b"one"),
                        SimpleUploadedFile("two.txt", b"two"),
                    ],
                },
            )
            self.assertEqual(409, too_many.status_code)
            self.assertContains(too_many, "job has too many sources", status_code=409)
            self.assertEqual(0, ResearchCampaign.objects.count())

            too_large = self.client.post(
                reverse("campaigns"),
                {
                    "title": "Too many bytes",
                    "issuer_or_security": "Example Industrials",
                    "equities_decision_use": "Update the owned model.",
                    "evidence_cutoff": "2026-08-13",
                    "commissioned_question": "Which value should change?",
                    "run_instruction": "Return a provisional proposal or refusal.",
                    "starting_artifact": SimpleUploadedFile("model.xlsx", b"model"),
                    "sources": [SimpleUploadedFile("one.txt", b"source")],
                },
            )
            self.assertEqual(409, too_large.status_code)
            self.assertContains(
                too_large,
                "job inputs exceed the aggregate custody limit",
                status_code=409,
            )
        self.assertEqual(0, ResearchCampaign.objects.count())
        self.assertEqual(0, ArtifactVersion.objects.count())
        self.assertEqual(0, RunSpecVersion.objects.count())
        self.assertEqual(0, WorkOrder.objects.count())
        self.assertEqual([], list(Path(self.temp.name).iterdir()))

    def test_oversize_upload_is_read_only_to_the_limit_and_creates_nothing(
        self,
    ) -> None:
        class HostileUpload:
            name = "oversize.xlsx"
            content_type = "application/octet-stream"
            size = None
            read_limit: int | None = None

            def read(self, limit: int) -> bytes:
                self.read_limit = limit
                return b"x" * limit

        hostile = HostileUpload()
        with self.settings(
            CAMPAIGN_ARTIFACT_MAX_BYTES=8,
            CAMPAIGN_JOB_MAX_INPUT_BYTES=32,
            CAMPAIGN_JOB_MAX_SOURCES=1,
        ):
            with self.assertRaisesMessage(
                CampaignRejected, "starting artifact exceeds the custody limit"
            ):
                create_owned_job(
                    director=self.director,
                    title="Oversize job",
                    issuer_or_security="Example Industrials",
                    equities_decision_use="Update the owned model.",
                    evidence_cutoff="2026-08-13",
                    question="Which value should change?",
                    run_instruction="Return a provisional proposal or refusal.",
                    starting_artifact=hostile,
                    sources=[SimpleUploadedFile("source.txt", b"source")],
                )
        self.assertEqual(9, hostile.read_limit)
        self.assertEqual(0, ResearchCampaign.objects.count())
        self.assertEqual(0, ArtifactVersion.objects.count())
        self.assertEqual([], list(Path(self.temp.name).iterdir()))

    def test_wrong_semantic_acknowledgement_cannot_be_attached_post_hoc(self) -> None:
        campaign, _, _ = self.create_job()
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")
        mark_worker_complete(order)
        write_bound_outputs(
            order,
            acknowledgement_inputs=[
                {"id": str(uuid.uuid4()), "sha256": "0" * 64}
            ],
        )

        response = self.client.post(reverse("campaign_collect", args=[campaign.pk]))

        self.assertEqual(409, response.status_code)
        self.assertContains(response, "did not acknowledge the exact bound run", status_code=409)
        self.assertEqual(0, Artifact.objects.filter(work_order=order).count())

    def test_conflicting_candidate_and_refusal_are_not_admitted(self) -> None:
        campaign, _, _ = self.create_job()
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")
        mark_worker_complete(order)
        write_bound_outputs(order, conflicting_disposition=True)

        response = self.client.post(reverse("campaign_collect", args=[campaign.pk]))

        self.assertEqual(409, response.status_code)
        self.assertContains(
            response,
            "bound work outcome contains conflicting dispositions",
            status_code=409,
        )
        self.assertEqual(0, Artifact.objects.filter(work_order=order).count())

    def test_changed_materialized_input_blocks_outcome_admission(self) -> None:
        campaign, _, _ = self.create_job()
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")
        _dispatch_path(order)
        materialized = Path(order.packet["job_input_files"][0]["materialized_path"])
        materialized.chmod(0o600)
        materialized.write_bytes(b"different bytes under the original path")
        mark_worker_complete(order, materialize_inputs=False)
        write_bound_outputs(order)

        response = self.client.post(reverse("campaign_collect", args=[campaign.pk]))

        self.assertEqual(409, response.status_code)
        self.assertContains(
            response,
            "materialized bound job input changed",
            status_code=409,
        )
        self.assertEqual(0, Artifact.objects.filter(work_order=order).count())
        self.assertTrue(Path(order.packet["output_contract"]["output_root"]).is_dir())

    def test_oversize_worker_output_is_rejected_before_unbounded_read(self) -> None:
        campaign, _, _ = self.create_job()
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")
        mark_worker_complete(order)
        write_bound_outputs(order)
        output = Path(order.packet["output_contract"]["output_root"])
        (output / "outcome.json").write_bytes(b"x" * 4097)

        with self.settings(CAMPAIGN_ARTIFACT_MAX_BYTES=4096):
            response = self.client.post(
                reverse("campaign_collect", args=[campaign.pk])
            )

        self.assertEqual(409, response.status_code)
        self.assertContains(response, "artifact exceeds the custody limit", status_code=409)
        self.assertEqual(0, Artifact.objects.filter(work_order=order).count())

    def test_run_spec_cannot_bind_another_campaign_owners_input(self) -> None:
        campaign, _, _ = self.create_job()
        foreign_input = ArtifactVersion.objects.filter(campaign=campaign).first()
        other_director = get_user_model().objects.create_user("other-director")
        other_campaign = create_campaign(
            director=other_director,
            title="Another owned job",
            issuer_or_security="Different issuer",
            equities_decision_use="A separate professional use.",
            evidence_cutoff="2026-08-13",
            question="What belongs to this separate job?",
        )
        manifest = [
            {
                "id": str(foreign_input.pk),
                "role": foreign_input.role,
                "filename": foreign_input.filename,
                "media_type": foreign_input.media_type,
                "sha256": foreign_input.digest,
            }
        ]
        outcome_contract = {
            "schema_version": "bound-run-outcome/v1",
            "allowed_kinds": ["candidate", "refusal"],
            "authority": "provisional_only",
        }
        with self.assertRaisesMessage(
            ValidationError,
            "run specification input custody does not match",
        ):
            RunSpecVersion.objects.create(
                id=uuid.uuid4(),
                campaign=other_campaign,
                objective="Cross the ownership boundary.",
                instruction="This must fail.",
                input_manifest=manifest,
                outcome_contract=outcome_contract,
                digest="0" * 64,
            )
        self.assertEqual(1, RunSpecVersion.objects.count())

    def test_run_spec_and_bound_order_reject_post_hoc_mutation(self) -> None:
        campaign, _, _ = self.create_job()
        spec = RunSpecVersion.objects.get(campaign=campaign)
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")

        spec.instruction = "A different instruction"
        with self.assertRaises(ValidationError):
            spec.save()
        with self.assertRaises(ValidationError):
            RunSpecVersion.objects.filter(pk=spec.pk).update(instruction="changed")
        order.run_spec = None
        with self.assertRaises(ValidationError):
            order.save()
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE campaign_runspecversion SET instruction = %s WHERE id = %s",
                    ["raw SQL mutation", spec.pk],
                )
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE campaign_workorder SET run_spec_id = NULL WHERE id = %s",
                    [order.pk],
                )

    def test_work_order_model_requires_bound_protocol_and_run_spec_together(self) -> None:
        campaign, _, _ = self.create_job()
        spec = RunSpecVersion.objects.get(campaign=campaign)
        base_packet = WorkOrder.objects.get(campaign=campaign).packet

        def approved_proposal(protocol: str) -> Proposal:
            proposal = record_proposal(
                campaign=campaign,
                author=Proposal.Author.DIRECTOR,
                author_user=self.director,
                protocol=protocol,
                title=f"Direct {protocol} construction",
                task="This must fail at the model boundary.",
                contract={"workbenches": [], "reasoning_operators": []},
            )
            ProposalDisposition.objects.create(
                proposal=proposal,
                kind=ProposalDisposition.Kind.APPROVED,
                actor=self.director,
            )
            return proposal

        bound = approved_proposal("bound_work")
        with self.assertRaisesMessage(
            ValidationError,
            "bound-work protocol and run specification must be present together",
        ):
            WorkOrder.objects.create(
                id=uuid.uuid4(),
                campaign=campaign,
                proposal=bound,
                run_spec=None,
                logical_role_id=uuid.uuid4(),
                protocol="bound_work",
                proposal_digest=bound.digest,
                input_artifact_ids=[],
                packet={},
                digest="0" * 64,
            )

        reused_planner = approved_proposal("planner")
        reused_packet = json.loads(json.dumps(base_packet))
        reused_id = uuid.uuid4()
        reused_role = uuid.uuid4()
        reused_packet.update(
            {
                "work_order_id": str(reused_id),
                "logical_role_id": str(reused_role),
                "proposal_id": str(reused_planner.pk),
                "proposal_digest": reused_planner.digest,
                "task": reused_planner.task,
                "contract": reused_planner.contract,
            }
        )
        with self.assertRaisesMessage(
            ValidationError,
            "work-order packet does not derive from its exact approved proposal",
        ):
            WorkOrder.objects.create(
                id=reused_id,
                campaign=campaign,
                proposal=reused_planner,
                run_spec=spec,
                logical_role_id=reused_role,
                protocol="bound_work",
                proposal_digest=reused_planner.digest,
                input_artifact_ids=[],
                packet=reused_packet,
                digest="0" * 64,
            )

        expected_contract = {
            "workbenches": [],
            "reasoning_operators": [],
            "run_spec": {"id": str(spec.pk), "sha256": spec.digest},
            "authority": "provisional_only",
        }
        exact_proposal = record_proposal(
            campaign=campaign,
            author=Proposal.Author.DIRECTOR,
            author_user=self.director,
            protocol="bound_work",
            title="Forge a changed run instruction",
            task=spec.instruction,
            contract=expected_contract,
        )
        ProposalDisposition.objects.create(
            proposal=exact_proposal,
            kind=ProposalDisposition.Kind.APPROVED,
            actor=self.director,
        )
        extra_id = uuid.uuid4()
        extra_role = uuid.uuid4()
        extra_packet = canonical_bound_work_packet(
            campaign=campaign,
            proposal=exact_proposal,
            run_spec=spec,
            order_id=extra_id,
            logical_role_id=extra_role,
        )
        extra_identity = {
            "id": str(extra_id),
            "campaign": str(campaign.pk),
            "proposal": str(exact_proposal.pk),
            "logical_role_id": str(extra_role),
            "protocol": "bound_work",
            "proposal_digest": exact_proposal.digest,
            "input_artifact_ids": [999],
            "state_basis": WorkOrder.StateBasis.COMMISSION,
            "input_state": None,
            "packet": extra_packet,
            "run_spec": str(spec.pk),
            "run_spec_sha256": spec.digest,
        }
        with self.assertRaisesMessage(
            ValidationError,
            "bound work may use only its exact run-spec input custody",
        ):
            WorkOrder.objects.create(
                id=extra_id,
                campaign=campaign,
                proposal=exact_proposal,
                run_spec=spec,
                logical_role_id=extra_role,
                protocol="bound_work",
                proposal_digest=exact_proposal.digest,
                input_artifact_ids=[999],
                packet=extra_packet,
                digest=canonical_digest(extra_identity),
            )
        extra_order = WorkOrder(
            id=extra_id,
            campaign=campaign,
            proposal=exact_proposal,
            run_spec=spec,
            logical_role_id=extra_role,
            protocol="bound_work",
            proposal_digest=exact_proposal.digest,
            input_artifact_ids=[999],
            packet=extra_packet,
            digest=canonical_digest(extra_identity),
        )
        with self.assertRaisesMessage(
            CampaignRejected,
            "bound work no longer matches its exact run specification",
        ):
            _validate_runtime_contract(extra_order)

        forged_id = uuid.uuid4()
        forged_role = uuid.uuid4()
        forged_packet = canonical_bound_work_packet(
            campaign=campaign,
            proposal=exact_proposal,
            run_spec=spec,
            order_id=forged_id,
            logical_role_id=forged_role,
        )
        forged_packet["run_instruction"] = (
            "A different instruction with a recomputed digest."
        )
        forged_identity = {
            "id": str(forged_id),
            "campaign": str(campaign.pk),
            "proposal": str(exact_proposal.pk),
            "logical_role_id": str(forged_role),
            "protocol": "bound_work",
            "proposal_digest": exact_proposal.digest,
            "input_artifact_ids": [],
            "state_basis": WorkOrder.StateBasis.COMMISSION,
            "input_state": None,
            "packet": forged_packet,
            "run_spec": str(spec.pk),
            "run_spec_sha256": spec.digest,
        }
        with self.assertRaisesMessage(
            ValidationError,
            "work order packet does not match its canonical bound specification",
        ):
            WorkOrder.objects.create(
                id=forged_id,
                campaign=campaign,
                proposal=exact_proposal,
                run_spec=spec,
                logical_role_id=forged_role,
                protocol="bound_work",
                proposal_digest=exact_proposal.digest,
                input_artifact_ids=[],
                packet=forged_packet,
                digest=canonical_digest(forged_identity),
            )

        for field, value in (
            ("decision_use", "FORGED DECISION USE"),
            ("schema_version", "forged-work-order/v999"),
            ("research_case_id", str(uuid.uuid4())),
        ):
            hostile_id = uuid.uuid4()
            hostile_role = uuid.uuid4()
            hostile_packet = canonical_bound_work_packet(
                campaign=campaign,
                proposal=exact_proposal,
                run_spec=spec,
                order_id=hostile_id,
                logical_role_id=hostile_role,
            )
            hostile_packet[field] = value
            hostile_identity = {
                "id": str(hostile_id),
                "campaign": str(campaign.pk),
                "proposal": str(exact_proposal.pk),
                "logical_role_id": str(hostile_role),
                "protocol": "bound_work",
                "proposal_digest": exact_proposal.digest,
                "input_artifact_ids": [],
                "state_basis": WorkOrder.StateBasis.COMMISSION,
                "input_state": None,
                "packet": hostile_packet,
                "run_spec": str(spec.pk),
                "run_spec_sha256": spec.digest,
            }
            with self.subTest(field=field), self.assertRaisesMessage(
                ValidationError,
                "work order packet does not match its canonical bound specification",
            ):
                WorkOrder.objects.create(
                    id=hostile_id,
                    campaign=campaign,
                    proposal=exact_proposal,
                    run_spec=spec,
                    logical_role_id=hostile_role,
                    protocol="bound_work",
                    proposal_digest=exact_proposal.digest,
                    input_artifact_ids=[],
                    packet=hostile_packet,
                    digest=canonical_digest(hostile_identity),
                )
            hostile_order = WorkOrder(
                id=hostile_id,
                campaign=campaign,
                proposal=exact_proposal,
                run_spec=spec,
                logical_role_id=hostile_role,
                protocol="bound_work",
                proposal_digest=exact_proposal.digest,
                input_artifact_ids=[],
                packet=hostile_packet,
                digest=canonical_digest(hostile_identity),
            )
            with self.subTest(field=f"runtime:{field}"), self.assertRaisesMessage(
                CampaignRejected,
                "bound work no longer matches its exact run specification",
            ):
                _validate_runtime_contract(hostile_order)

        planner = approved_proposal("planner")
        with self.assertRaisesMessage(
            ValidationError,
            "bound-work protocol and run specification must be present together",
        ):
            WorkOrder.objects.create(
                id=uuid.uuid4(),
                campaign=campaign,
                proposal=planner,
                run_spec=spec,
                logical_role_id=uuid.uuid4(),
                protocol="planner",
                proposal_digest=planner.digest,
                input_artifact_ids=[],
                packet=base_packet,
                digest="0" * 64,
            )

    def test_bound_job_cannot_enter_the_legacy_planner_path(self) -> None:
        campaign, _, _ = self.create_job()

        response = self.client.post(
            reverse("campaign_approve_planner_programme", args=[campaign.pk])
        )

        self.assertEqual(409, response.status_code)
        self.assertContains(
            response,
            "campaign already has an authorized first step",
            status_code=409,
        )
        self.assertEqual(1, WorkOrder.objects.filter(campaign=campaign).count())
        self.assertFalse(
            WorkOrder.objects.filter(campaign=campaign, protocol="planner").exists()
        )

    def test_bound_work_cannot_use_a_legacy_unbound_packet(self) -> None:
        campaign = create_campaign(
            director=self.director,
            title="Historical research campaign",
            issuer_or_security="Example Industrials",
            equities_decision_use="Investigate the earnings change.",
            evidence_cutoff="2026-08-13",
            question="What changed?",
        )
        proposal = record_proposal(
            campaign=campaign,
            author="director",
            author_user=self.director,
            protocol="bound_work",
            title="Attempt an unbound job",
            task="Return a proposal.",
            contract={
                "workbenches": [],
                "reasoning_operators": [],
                "authority": "provisional_only",
            },
        )

        with self.assertRaisesMessage(
            CampaignRejected, "bound work lacks its exact run specification"
        ):
            _approved_order(proposal, user=self.director)
        self.assertEqual(0, WorkOrder.objects.filter(campaign=campaign).count())

    def test_bounded_refusal_uses_the_same_custody_path(self) -> None:
        campaign, _, _ = self.create_job()
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")
        mark_worker_complete(order)
        write_bound_outputs(order, outcome_kind="refusal")

        response = self.client.post(reverse("campaign_collect", args=[campaign.pk]))

        self.assertEqual(302, response.status_code, response.content)
        restarted = Client()
        restarted.force_login(self.director)
        page = restarted.get(reverse("campaign", args=[campaign.pk]))
        self.assertContains(page, "Bounded refusal")
        self.assertContains(page, "No installed tool can inspect the native artifact safely.")

    def test_collected_job_can_stop_without_reopening_output_custody(self) -> None:
        class ControlledStop:
            def stop_command(self, session, config):
                return ["controlled-stop"]

            def execute(self, argv, *, environment):
                return ExecutionResult(
                    0,
                    b"",
                    b"",
                    {
                        "killed": True,
                        "session": campaign.ntm_session,
                        "generated_at": "2026-08-14T22:03:00Z",
                    },
                )

        campaign, _, _ = self.create_job()
        order = WorkOrder.objects.get(campaign=campaign, protocol="bound_work")
        mark_worker_complete(order)
        write_bound_outputs(order)
        self.assertEqual(
            302,
            self.client.post(reverse("campaign_collect", args=[campaign.pk])).status_code,
        )

        with self.settings(
            CAMPAIGN_CODEX_BINARY="/usr/bin/true",
            LANGFUSE_TARGET_BASE_URL="https://cloud.langfuse.com",
        ):
            event = stop_campaign(campaign, self.director, control=ControlledStop())

        self.assertTrue(event.succeeded)
        self.assertFalse(
            Path(order.packet["output_contract"]["output_root"]).exists()
        )
