from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_workspace.branch_supervisor import BranchSupervisor
from research_workspace.branch_workspace import attempt_paths
from research_workspace.util import atomic_write, canonical_json

from .test_ntm_branch_policy import BranchPolicyFixture


class BranchSupervisorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.fixture = BranchPolicyFixture(Path(self.temporary.name))
        self.supervisor = BranchSupervisor(
            self.fixture.workspace,
            self.fixture.controller,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_ack(self, branch_id: str, binding_id: str, instruction_id: str) -> None:
        branch = self.fixture.workspace.store.get_object(branch_id)
        binding = self.fixture.workspace.store.get_object(binding_id)
        instruction = self.fixture.workspace.store.get_object(instruction_id)
        paths = attempt_paths(
            self.fixture.workspace.store,
            branch_id,
            binding_id,
        )
        atomic_write(
            paths.outbox / f"acknowledgement-{instruction_id}.json",
            canonical_json(
                {
                    "schema": "research-branch-acknowledgement/v1",
                    "branch_id": branch_id,
                    "binding_id": binding_id,
                    "instruction_id": instruction_id,
                    "instruction_digest": instruction.payload["message_digest"],
                    "context_ids": instruction.payload["context_ids"],
                    "authority_ceiling": branch.payload["authority_ceiling"],
                    "worker": {
                        "provider": "codex",
                        "model": binding.payload["model"],
                        "role": binding.payload["role_name"],
                    },
                    "protocol_version": "ntm-codex-research-branch/v1",
                }
            ).encode("utf-8"),
        )

    def test_supervisor_returns_checkpoint_identity_and_collects_result(self) -> None:
        launch = self.fixture.launch(session="supervised-completion")
        self._write_ack(
            self.fixture.branch.id,
            launch.binding_id,
            launch.instruction_id,
        )
        first = self.supervisor.step(self.fixture.branch.id)
        self.assertEqual("acknowledgement_collected", first.action)

        context_id = self.fixture.workspace._branch_context_ids(self.fixture.branch.id)[0]
        context = self.fixture.workspace.store.get_object(context_id)
        assertion_id = context.payload["included_assertion_ids"][0]
        object_id = context.payload["professional_object_ids"][0]
        claim = {
            "claim_id": "supervised-claim",
            "text": "The admitted evidence supports the professional object.",
            "support_relations": [
                {
                    "assertion_id": assertion_id,
                    "professional_object_id": object_id,
                }
            ],
            "contradiction_relations": [],
            "uncertainty": [],
            "scope": {"use": "internal research"},
        }
        paths = attempt_paths(
            self.fixture.workspace.store,
            self.fixture.branch.id,
            launch.binding_id,
        )
        atomic_write(
            paths.checkpoints / "0001.json",
            canonical_json(
                {
                    "schema": "research-branch-checkpoint/v1",
                    "branch_id": self.fixture.branch.id,
                    "binding_id": launch.binding_id,
                    "sequence": 1,
                    "predecessor_id": None,
                    "candidate_claims": [claim],
                    "rivals": [],
                    "source_request_ids": [],
                    "artifact_proposals": [],
                    "unresolved_questions": [],
                    "next_action": None,
                    "disposition": "complete",
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        checkpoint_report = self.supervisor.step(self.fixture.branch.id)
        self.assertEqual("checkpoint_collected", checkpoint_report.action)
        self.assertIsNotNone(checkpoint_report.object_id)
        self.assertIsNotNone(checkpoint_report.instruction_id)

        self._write_ack(
            self.fixture.branch.id,
            launch.binding_id,
            checkpoint_report.instruction_id,
        )
        receipt_ack = self.supervisor.step(self.fixture.branch.id)
        self.assertEqual("acknowledgement_collected", receipt_ack.action)

        atomic_write(
            paths.outbox / "result.json",
            canonical_json(
                {
                    "schema": "research-branch-result/v1",
                    "branch_id": self.fixture.branch.id,
                    "binding_id": launch.binding_id,
                    "checkpoint_id": checkpoint_report.object_id,
                    "summary": "The admitted evidence supports the object.",
                    "claims": [claim],
                    "artifacts": [],
                    "memory_proposals": [],
                    "unresolved_questions": [],
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        completed = self.supervisor.step(self.fixture.branch.id)
        self.assertEqual("result_collected", completed.action)
        self.assertEqual(
            "completed",
            self.fixture.workspace.branch_state(self.fixture.branch.id)["state"],
        )

    def test_supervisor_returns_host_source_request_identity_to_codex(self) -> None:
        launch = self.fixture.launch(session="supervised-source-request")
        self._write_ack(
            self.fixture.branch.id,
            launch.binding_id,
            launch.instruction_id,
        )
        self.supervisor.step(self.fixture.branch.id)
        context_id = self.fixture.workspace._branch_context_ids(self.fixture.branch.id)[0]
        context = self.fixture.workspace.store.get_object(context_id)
        object_id = context.payload["professional_object_ids"][0]
        paths = attempt_paths(
            self.fixture.workspace.store,
            self.fixture.branch.id,
            launch.binding_id,
        )
        atomic_write(
            paths.source_requests / "need-more-evidence.json",
            canonical_json(
                {
                    "schema": "research-source-request/v1",
                    "branch_id": self.fixture.branch.id,
                    "binding_id": launch.binding_id,
                    "external_request_id": "need-more-evidence",
                    "request_kind": "url",
                    "locator": "https://example.invalid/source",
                    "source_class": "public_source",
                    "purpose": "Test another source",
                    "rationale": "The branch needs another discriminator.",
                    "professional_object_ids": [object_id],
                    "rights_needed": {"internal_use": True},
                }
            ).encode("utf-8"),
        )
        report = self.supervisor.step(self.fixture.branch.id)
        self.assertEqual("source_request_collected", report.action)
        self.assertIsNotNone(report.object_id)
        self.assertIsNotNone(report.instruction_id)
        receipt = self.fixture.workspace.store.get_object(report.instruction_id)
        self.assertIn(report.object_id, receipt.payload["instruction_text"])

        self._write_ack(
            self.fixture.branch.id,
            launch.binding_id,
            report.instruction_id,
        )
        self.assertEqual(
            "acknowledgement_collected",
            self.supervisor.step(self.fixture.branch.id).action,
        )
        atomic_write(
            paths.checkpoints / "0001.json",
            canonical_json(
                {
                    "schema": "research-branch-checkpoint/v1",
                    "branch_id": self.fixture.branch.id,
                    "binding_id": launch.binding_id,
                    "sequence": 1,
                    "predecessor_id": None,
                    "candidate_claims": [],
                    "rivals": [],
                    "source_request_ids": [report.object_id],
                    "artifact_proposals": [],
                    "unresolved_questions": ["Waiting for the host to capture the source."],
                    "next_action": "Wait for an admitted context delta.",
                    "disposition": "continue",
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        checkpoint_report = self.supervisor.step(self.fixture.branch.id)
        self.assertEqual("checkpoint_collected", checkpoint_report.action)
        checkpoint_receipt = self.fixture.workspace.store.get_object(
            checkpoint_report.instruction_id
        )
        self.assertIn(
            checkpoint_report.object_id,
            checkpoint_receipt.payload["instruction_text"],
        )


if __name__ == "__main__":
    unittest.main()
