from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from harness.ntm.adapter import NtmAdapter
from research_workspace import (
    AuthorityError,
    NtmResearchController,
    ResearchWorkspace,
    RuntimeFailure,
)
from research_workspace.branch_workspace import attempt_paths
from research_workspace.util import atomic_write, canonical_json

from .test_ntm_persistent_research_branch import FakeNtmControl


class BranchPolicyFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.workspace = ResearchWorkspace.initialise(root / "workspace")
        self.controller = FakeNtmControl()
        self.config = root / "ntm-config.json"
        self.config.write_text("{}", encoding="utf-8")
        mandate = self.workspace.create_mandate(
            title="Persistent branch policy",
            decision_use="Internal research",
            actor="analyst",
            policy={"authorised_actors": ["analyst"]},
        )
        method = self.workspace.register_method(
            name="evidence comparison",
            version="v1",
            purpose="Test one admitted claim",
            output_kinds=["cited_note"],
            required_actions=["support_claim"],
            runtime={"kind": "ntm-persistent-codex"},
            limits={"provisional_only": True},
        )
        perspective = self.workspace.create_perspective(
            mandate_id=mandate.id,
            label="Starting view",
            item_ids=[],
        )
        episode = self.workspace.create_episode(
            mandate_id=mandate.id,
            title="Policy episode",
            original_request="Test the persistent branch authority.",
            evidence_cutoff="2025-10-04T00:00:00+00:00",
            intended_use="Internal research",
            prior_perspective_id=perspective.id,
        )
        commission = self.workspace.confirm_commission(
            episode_id=episode.id,
            actor="analyst",
            purpose="Test the persistent branch authority",
            subject_ids=[],
            method_ids=[method.id],
            output_kinds=["cited_note"],
            unresolved_questions=[],
            limits={"authority": "provisional_only"},
        )
        professional_object = self.workspace.create_professional_object(
            mandate_id=mandate.id,
            kind="research_claim",
            label="One admitted fact",
            attributes={},
            binding={},
            authority="human_confirmed",
            actor="analyst",
        )
        source_path = root / "source.txt"
        source_path.write_text("The admitted fact is true.", encoding="utf-8")
        source = self.workspace.capture_source(
            mandate_id=mandate.id,
            path=source_path,
            source_class="public_source",
            rights={"retain": True, "internal_use": True},
            metadata={},
        )
        assertion = self.workspace.create_assertion(
            source_id=source.id,
            locator="line 1",
            content="The admitted fact is true.",
            attributes={},
            proposed_by="fixture",
        )
        self.workspace.decide_evidence_use(
            episode_id=episode.id,
            assertion_id=assertion.id,
            professional_object_id=professional_object.id,
            intended_use=episode.payload["intended_use"],
            permitted_actions=["support_claim"],
            decision="admit",
            rationale="The source is permitted for this object and use.",
            actor="analyst",
        )
        context = self.workspace.build_context(
            episode_id=episode.id,
            commission_id=commission.id,
            method_id=method.id,
            purpose="Support one claim",
            assertion_ids=[assertion.id],
            professional_object_ids=[professional_object.id],
            required_action="support_claim",
        )
        self.branch = self.workspace.create_research_branch(
            episode_id=episode.id,
            commission_id=commission.id,
            method_id=method.id,
            branch_kind="research",
            title="Persistent policy branch",
            question="What does the admitted evidence support?",
            context_ids=[context.id],
            expected_outputs=["typed_claims"],
            authority_ceiling="provisional_only",
            created_by="analyst",
        )

    def launch(self, *, session: str, resume_checkpoint_id: str | None = None):
        return self.workspace.launch_research_branch(
            branch_id=self.branch.id,
            controller=self.controller,
            config=self.config,
            model="gpt-5.6-codex",
            role_name="research_worker",
            actor="analyst",
            session=session,
            resume_checkpoint_id=resume_checkpoint_id,
        )

    def acknowledgement_payload(
        self,
        launch,
        *,
        model: str = "gpt-5.6-codex",
        role: str = "research_worker",
    ) -> dict:
        binding = self.workspace.store.get_object(launch.binding_id)
        instruction = self.workspace.store.get_object(launch.instruction_id)
        return {
            "schema": "research-branch-acknowledgement/v1",
            "branch_id": self.branch.id,
            "binding_id": binding.id,
            "instruction_id": instruction.id,
            "instruction_digest": instruction.payload["message_digest"],
            "context_ids": instruction.payload["context_ids"],
            "authority_ceiling": self.branch.payload["authority_ceiling"],
            "worker": {
                "provider": "codex",
                "model": model,
                "role": role,
            },
            "protocol_version": "ntm-codex-research-branch/v1",
        }

    def acknowledge(self, launch) -> None:
        paths = attempt_paths(
            self.workspace.store,
            self.branch.id,
            launch.binding_id,
        )
        atomic_write(
            paths.outbox / f"acknowledgement-{launch.instruction_id}.json",
            canonical_json(self.acknowledgement_payload(launch)).encode("utf-8"),
        )
        self.workspace.collect_branch_acknowledgement(
            branch_id=self.branch.id,
            binding_id=launch.binding_id,
            instruction_id=launch.instruction_id,
        )

    def checkpoint(self, launch, *, sequence: int, predecessor_id: str | None):
        paths = attempt_paths(
            self.workspace.store,
            self.branch.id,
            launch.binding_id,
        )
        filename = f"{sequence:04d}.json"
        atomic_write(
            paths.checkpoints / filename,
            canonical_json(
                {
                    "schema": "research-branch-checkpoint/v1",
                    "branch_id": self.branch.id,
                    "binding_id": launch.binding_id,
                    "sequence": sequence,
                    "predecessor_id": predecessor_id,
                    "candidate_claims": [],
                    "rivals": [],
                    "source_request_ids": [],
                    "artifact_proposals": [],
                    "unresolved_questions": ["The branch remains open."],
                    "next_action": "Continue in a persistent session.",
                    "disposition": "continue",
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        return self.workspace.collect_branch_checkpoint(
            branch_id=self.branch.id,
            binding_id=launch.binding_id,
            relative_path=filename,
        )


class PersistentBranchPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.fixture = BranchPolicyFixture(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_wrong_codex_model_acknowledgement_is_rejected_before_custody(self) -> None:
        launch = self.fixture.launch(session="wrong-model")
        paths = attempt_paths(
            self.fixture.workspace.store,
            self.fixture.branch.id,
            launch.binding_id,
        )
        atomic_write(
            paths.outbox / f"acknowledgement-{launch.instruction_id}.json",
            canonical_json(
                self.fixture.acknowledgement_payload(
                    launch,
                    model="different-codex-model",
                )
            ).encode("utf-8"),
        )
        with self.assertRaises(RuntimeFailure):
            self.fixture.workspace.collect_branch_acknowledgement(
                branch_id=self.fixture.branch.id,
                binding_id=launch.binding_id,
                instruction_id=launch.instruction_id,
            )
        self.assertEqual(
            [],
            self.fixture.workspace.store.list_objects("branch_ack"),
        )

    def test_superseded_ntm_session_cannot_advance_branch(self) -> None:
        first = self.fixture.launch(session="first-session")
        self.fixture.acknowledge(first)
        checkpoint = self.fixture.checkpoint(
            first,
            sequence=1,
            predecessor_id=None,
        )
        second = self.fixture.launch(
            session="second-session",
            resume_checkpoint_id=checkpoint.id,
        )
        with self.assertRaises(AuthorityError):
            self.fixture.workspace.observe_branch_status(
                branch_id=self.fixture.branch.id,
                binding_id=first.binding_id,
                controller=self.fixture.controller,
                config=self.fixture.config,
            )
        self.assertEqual(
            second.binding_id,
            self.fixture.workspace.branch_state(self.fixture.branch.id)[
                "latest_binding_id"
            ],
        )


class NtmResearchControllerTests(unittest.TestCase):
    def test_controller_uses_existing_allowlisted_persistent_ntm_commands(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / "fake-ntm"
            binary.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "print(json.dumps({'argv': sys.argv[1:]}))\n",
                encoding="utf-8",
            )
            binary.chmod(0o700)
            config = root / "config.json"
            config.write_text("{}", encoding="utf-8")
            working = root / "working"
            working.mkdir()
            message = root / "message.json"
            message.write_text("{}", encoding="utf-8")
            controller = NtmResearchController(NtmAdapter(binary.resolve()))
            receipts = [
                controller.spawn(
                    session="persistent-research",
                    working_directory=working,
                    role_name="research_worker",
                    config=config,
                ),
                controller.send(
                    session="persistent-research",
                    pane=1,
                    message=message,
                    config=config,
                ),
                controller.status(
                    session="persistent-research",
                    config=config,
                ),
                controller.completion(
                    session="persistent-research",
                    pane=1,
                    config=config,
                ),
                controller.stop(
                    session="persistent-research",
                    config=config,
                ),
            ]
            self.assertTrue(all(item.succeeded for item in receipts))
            arguments = [argument for item in receipts for argument in item.argv]
            self.assertIn("--robot-spawn=persistent-research", arguments)
            self.assertIn("--robot-send=persistent-research", arguments)
            self.assertIn("--robot-wait=persistent-research", arguments)
            self.assertNotIn("exec", arguments)
            self.assertNotIn("codex", arguments)


if __name__ == "__main__":
    unittest.main()
