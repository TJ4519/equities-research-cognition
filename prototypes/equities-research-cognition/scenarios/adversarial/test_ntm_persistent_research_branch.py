from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_workspace import AuthorityError, ResearchWorkspace, RuntimeFailure
from research_workspace.branch_workspace import attempt_paths
from research_workspace.ntm_research import NtmReceipt
from research_workspace.util import atomic_write, canonical_json


class FakeNtmControl:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def _receipt(self, action: str, argv: list[str], response: object) -> NtmReceipt:
        self.calls.append({"action": action, "argv": argv, "response": response})
        return NtmReceipt(
            action=action,
            argv=tuple(argv),
            exit_code=0,
            timed_out=False,
            stdout=canonical_json(response).encode("utf-8"),
            stderr=b"",
            response=response,
        )

    def spawn(self, *, session, working_directory, role_name, config, environment=None):
        return self._receipt(
            "spawn",
            ["ntm", "spawn", session, str(working_directory), role_name, str(config)],
            {"session": session, "pane": 1, "condition": "ready"},
        )

    def send(self, *, session, pane, message, config, environment=None):
        return self._receipt(
            "send",
            ["ntm", "send", session, str(pane), str(message), str(config)],
            {"session": session, "pane": pane, "tracked": True},
        )

    def status(self, *, session, config, environment=None):
        return self._receipt(
            "status",
            ["ntm", "status", session, str(config)],
            {"session": session, "condition": "active"},
        )

    def completion(self, *, session, pane, config, environment=None):
        return self._receipt(
            "completion",
            ["ntm", "wait", session, str(pane), str(config)],
            {"session": session, "pane": pane, "condition": "complete"},
        )

    def stop(self, *, session, config, environment=None):
        return self._receipt(
            "stop",
            ["ntm", "stop", session, str(config)],
            {"session": session, "condition": "stopped"},
        )


class PersistentResearchBranchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = ResearchWorkspace.initialise(self.root / "workspace")
        self.controller = FakeNtmControl()
        self.config = self.root / "ntm-config.json"
        self.config.write_text("{}", encoding="utf-8")

        self.mandate = self.workspace.create_mandate(
            title="Micron historical replay",
            decision_use="Internal post-results research",
            actor="analyst",
            policy={"authorised_actors": ["analyst"]},
        )
        self.method = self.workspace.register_method(
            name="purpose-bound-evidence-comparison",
            version="v1",
            purpose="Compare new evidence with exact prior work",
            output_kinds=["cited_note"],
            required_actions=["support_claim"],
            runtime={"kind": "ntm-persistent-codex"},
            limits={"provisional_only": True},
        )
        self.perspective = self.workspace.create_perspective(
            mandate_id=self.mandate.id,
            label="Pre-results view",
            item_ids=[],
        )
        self.episode = self.workspace.create_episode(
            mandate_id=self.mandate.id,
            title="Micron FY2025 results",
            original_request=(
                "Work out what the results change, compare management language, "
                "and check the historical revenue route."
            ),
            evidence_cutoff="2025-10-04T00:00:00+00:00",
            intended_use="Internal post-results research",
            prior_perspective_id=self.perspective.id,
        )
        self.commission = self.workspace.confirm_commission(
            episode_id=self.episode.id,
            actor="analyst",
            purpose="Determine supported changes to the prior Micron view",
            subject_ids=[],
            method_ids=[self.method.id],
            output_kinds=["cited_note"],
            unresolved_questions=["Which evidential route may support annual revenue?"],
            limits={"authority": "provisional_only"},
        )
        self.revenue_object = self.workspace.create_professional_object(
            mandate_id=self.mandate.id,
            kind="historical_model_input",
            label="FY2025 consolidated GAAP revenue",
            attributes={"unit": "USD millions", "period": "FY2025"},
            binding={"named_range": "FY25_REVENUE_USDM"},
            authority="human_confirmed",
            actor="analyst",
        )
        self.narrative_object = self.workspace.create_professional_object(
            mandate_id=self.mandate.id,
            kind="management_statement",
            label="Management's FY2025 revenue narrative",
            attributes={"period": "FY2025"},
            binding={},
            authority="human_confirmed",
            actor="analyst",
        )
        earnings_path = self.root / "earnings-release.txt"
        earnings_path.write_text("FY2025 revenue was 37,378.", encoding="utf-8")
        self.earnings_source = self.workspace.capture_source(
            mandate_id=self.mandate.id,
            path=earnings_path,
            source_class="earnings_release",
            rights={"retain": True, "internal_use": True},
            metadata={"issuer": "Micron"},
            published_at="2025-09-23T00:00:00+00:00",
        )
        self.earnings_assertion = self.workspace.create_assertion(
            source_id=self.earnings_source.id,
            locator="revenue statement",
            content="FY2025 revenue was 37,378 USDm",
            attributes={"value": "37378", "unit": "USD millions"},
            proposed_by="host-fixture",
        )
        self.workspace.decide_evidence_use(
            episode_id=self.episode.id,
            assertion_id=self.earnings_assertion.id,
            professional_object_id=self.narrative_object.id,
            intended_use=self.episode.payload["intended_use"],
            permitted_actions=["support_claim"],
            decision="admit",
            rationale="The release is admissible for management-language comparison.",
            actor="analyst",
        )
        self.workspace.decide_evidence_use(
            episode_id=self.episode.id,
            assertion_id=self.earnings_assertion.id,
            professional_object_id=self.revenue_object.id,
            intended_use=self.episode.payload["intended_use"],
            permitted_actions=[],
            decision="reject",
            rationale="The historical line requires the filed annual report once available.",
            actor="analyst",
        )
        self.context = self.workspace.build_context(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            purpose="Compare management language while protecting the model route",
            assertion_ids=[self.earnings_assertion.id],
            professional_object_ids=[self.narrative_object.id, self.revenue_object.id],
            required_action="support_claim",
            allowed_tools=["source_request"],
        )
        self.branch = self.workspace.create_research_branch(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            branch_kind="research",
            title="Micron evidence comparison",
            question="Which claims are supported, and which model route remains blocked?",
            context_ids=[self.context.id],
            expected_outputs=["typed_claims", "cited_note"],
            authority_ceiling="provisional_only",
            created_by="analyst",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _launch(self, *, resume_checkpoint_id: str | None = None, session: str = "micron-research"):
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

    def _acknowledge(self, launch, instruction_id: str | None = None):
        binding = self.workspace.store.get_object(launch.binding_id)
        instruction = self.workspace.store.get_object(
            instruction_id or launch.instruction_id
        )
        paths = attempt_paths(self.workspace.store, self.branch.id, binding.id)
        payload = {
            "schema": "research-branch-acknowledgement/v1",
            "branch_id": self.branch.id,
            "binding_id": binding.id,
            "instruction_id": instruction.id,
            "instruction_digest": instruction.payload["message_digest"],
            "context_ids": instruction.payload["context_ids"],
            "authority_ceiling": self.branch.payload["authority_ceiling"],
            "worker": {
                "provider": "codex",
                "model": binding.payload["model"],
                "role": binding.payload["role_name"],
            },
            "protocol_version": "ntm-codex-research-branch/v1",
        }
        atomic_write(
            paths.outbox / f"acknowledgement-{instruction.id}.json",
            canonical_json(payload).encode("utf-8"),
        )
        return self.workspace.collect_branch_acknowledgement(
            branch_id=self.branch.id,
            binding_id=binding.id,
            instruction_id=instruction.id,
        )

    def _write_checkpoint(self, binding_id: str, filename: str, payload: dict):
        paths = attempt_paths(self.workspace.store, self.branch.id, binding_id)
        atomic_write(
            paths.checkpoints / filename,
            canonical_json(payload).encode("utf-8"),
        )
        return self.workspace.collect_branch_checkpoint(
            branch_id=self.branch.id,
            binding_id=binding_id,
            relative_path=filename,
        )

    def test_persistent_branch_adds_host_admitted_context_and_collects_result(self) -> None:
        launch = self._launch()
        self._acknowledge(launch)
        binding_id = launch.binding_id
        paths = attempt_paths(self.workspace.store, self.branch.id, binding_id)

        source_request_payload = {
            "schema": "research-source-request/v1",
            "branch_id": self.branch.id,
            "binding_id": binding_id,
            "external_request_id": "need-annual-filing",
            "request_kind": "url",
            "locator": "Micron FY2025 annual filing",
            "source_class": "annual_filing",
            "purpose": "Support the historical revenue object",
            "rationale": "The earnings release is not admitted for this model use.",
            "professional_object_ids": [self.revenue_object.id],
            "rights_needed": {"internal_use": True},
        }
        atomic_write(
            paths.source_requests / "need-annual-filing.json",
            canonical_json(source_request_payload).encode("utf-8"),
        )
        source_request = self.workspace.collect_branch_source_request(
            branch_id=self.branch.id,
            binding_id=binding_id,
            relative_path="need-annual-filing.json",
        )
        checkpoint_one = self._write_checkpoint(
            binding_id,
            "0001.json",
            {
                "schema": "research-branch-checkpoint/v1",
                "branch_id": self.branch.id,
                "binding_id": binding_id,
                "sequence": 1,
                "predecessor_id": None,
                "candidate_claims": [
                    {
                        "claim_id": "management-revenue",
                        "text": "Management reported FY2025 revenue of 37,378 USDm.",
                        "support_relations": [
                            {
                                "assertion_id": self.earnings_assertion.id,
                                "professional_object_id": self.narrative_object.id,
                            }
                        ],
                        "contradiction_relations": [],
                        "uncertainty": [],
                        "scope": {"use": "management-language comparison"},
                    }
                ],
                "rivals": [],
                "source_request_ids": [source_request.id],
                "artifact_proposals": [],
                "unresolved_questions": ["Annual filing support remains missing."],
                "next_action": "Wait for host-captured annual filing evidence.",
                "disposition": "continue",
                "refusal": None,
            },
        )

        filing_path = self.root / "annual-filing.txt"
        filing_path.write_text("FY2025 revenue was 37,378.", encoding="utf-8")
        filing_source = self.workspace.capture_source(
            mandate_id=self.mandate.id,
            path=filing_path,
            source_class="annual_filing",
            rights={"retain": True, "internal_use": True},
            metadata={"issuer": "Micron"},
            published_at="2025-10-03T00:00:00+00:00",
        )
        filing_assertion = self.workspace.create_assertion(
            source_id=filing_source.id,
            locator="consolidated statements of operations",
            content="FY2025 revenue was 37,378 USDm",
            attributes={"value": "37378", "unit": "USD millions"},
            proposed_by="host-fixture",
        )
        self.workspace.decide_evidence_use(
            episode_id=self.episode.id,
            assertion_id=filing_assertion.id,
            professional_object_id=self.revenue_object.id,
            intended_use=self.episode.payload["intended_use"],
            permitted_actions=["support_claim"],
            decision="admit",
            rationale="The annual filing is admitted for the historical model line.",
            actor="analyst",
        )
        delta_context = self.workspace.build_context(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            purpose="Add annual filing support for the historical revenue object",
            assertion_ids=[filing_assertion.id],
            professional_object_ids=[self.revenue_object.id],
            required_action="support_claim",
            allowed_tools=[],
        )
        delta_instruction = self.workspace.attach_branch_context_delta(
            branch_id=self.branch.id,
            binding_id=binding_id,
            context_id=delta_context.id,
            controller=self.controller,
            config=self.config,
            actor="analyst",
            satisfies_source_request_ids=[source_request.id],
        )
        self._acknowledge(launch, delta_instruction.id)

        checkpoint_two = self._write_checkpoint(
            binding_id,
            "0002.json",
            {
                "schema": "research-branch-checkpoint/v1",
                "branch_id": self.branch.id,
                "binding_id": binding_id,
                "sequence": 2,
                "predecessor_id": checkpoint_one.id,
                "candidate_claims": [
                    {
                        "claim_id": "historical-revenue",
                        "text": "FY2025 consolidated GAAP revenue was 37,378 USDm.",
                        "support_relations": [
                            {
                                "assertion_id": filing_assertion.id,
                                "professional_object_id": self.revenue_object.id,
                            }
                        ],
                        "contradiction_relations": [],
                        "uncertainty": [],
                        "scope": {"use": "historical model support"},
                    }
                ],
                "rivals": [],
                "source_request_ids": [source_request.id],
                "artifact_proposals": [{"kind": "cited_note"}],
                "unresolved_questions": [],
                "next_action": None,
                "disposition": "complete",
                "refusal": None,
            },
        )
        self.workspace.observe_branch_completion(
            branch_id=self.branch.id,
            binding_id=binding_id,
            controller=self.controller,
            config=self.config,
        )
        note = paths.artifacts / "micron-note.md"
        atomic_write(
            note,
            (
                "# Micron results\n\n"
                "FY2025 consolidated GAAP revenue was 37,378 USDm "
                f"[{filing_assertion.id}].\n"
            ).encode("utf-8"),
        )
        result_payload = {
            "schema": "research-branch-result/v1",
            "branch_id": self.branch.id,
            "binding_id": binding_id,
            "checkpoint_id": checkpoint_two.id,
            "summary": "The same number is retained through the admitted annual-filing route.",
            "claims": checkpoint_two.payload["candidate_claims"],
            "artifacts": [
                {
                    "path": "artifacts/micron-note.md",
                    "kind": "cited_note",
                    "title": "Micron results note",
                    "media_type": "text/markdown",
                }
            ],
            "memory_proposals": [
                {
                    "content": "Use the filed annual report for this historical revenue object once available.",
                    "scope": {"professional_object_id": self.revenue_object.id},
                    "reason": "Preserve the confirmed source method without making it universal.",
                }
            ],
            "unresolved_questions": [],
            "refusal": None,
        }
        atomic_write(
            paths.outbox / "result.json",
            canonical_json(result_payload).encode("utf-8"),
        )
        outcome = self.workspace.collect_branch_result(
            branch_id=self.branch.id,
            binding_id=binding_id,
        )
        result = self.workspace.store.get_object(outcome.result_id)
        run = self.workspace.store.get_object(outcome.run_id)
        self.assertEqual("ntm-persistent-codex/v1", run.payload["adapter"])
        self.assertEqual(checkpoint_two.id, result.payload["checkpoint_id"])
        self.assertEqual("completed", self.workspace.branch_state(self.branch.id)["state"])
        self.assertNotEqual(self.earnings_assertion.id, filing_assertion.id)
        self.assertTrue(any(call["action"] == "spawn" for call in self.controller.calls))
        self.assertGreaterEqual(
            sum(call["action"] == "send" for call in self.controller.calls),
            2,
        )

    def test_ntm_completion_alone_cannot_complete_research(self) -> None:
        launch = self._launch(session="completion-is-not-authority")
        self.workspace.observe_branch_completion(
            branch_id=self.branch.id,
            binding_id=launch.binding_id,
            controller=self.controller,
            config=self.config,
        )
        with self.assertRaises(RuntimeFailure):
            self.workspace.collect_branch_result(
                branch_id=self.branch.id,
                binding_id=launch.binding_id,
            )

    def test_unacknowledged_context_delta_cannot_enter_checkpoint(self) -> None:
        launch = self._launch(session="unacknowledged-delta")
        self._acknowledge(launch)
        filing_path = self.root / "unacknowledged-filing.txt"
        filing_path.write_text("FY2025 revenue was 37,378.", encoding="utf-8")
        source = self.workspace.capture_source(
            mandate_id=self.mandate.id,
            path=filing_path,
            source_class="annual_filing",
            rights={"retain": True},
            metadata={},
        )
        assertion = self.workspace.create_assertion(
            source_id=source.id,
            locator="revenue",
            content="FY2025 revenue was 37,378 USDm",
            attributes={"value": "37378"},
            proposed_by="host-fixture",
        )
        self.workspace.decide_evidence_use(
            episode_id=self.episode.id,
            assertion_id=assertion.id,
            professional_object_id=self.revenue_object.id,
            intended_use=self.episode.payload["intended_use"],
            permitted_actions=["support_claim"],
            decision="admit",
            rationale="Admitted after capture.",
            actor="analyst",
        )
        context = self.workspace.build_context(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            purpose="Unacknowledged context delta",
            assertion_ids=[assertion.id],
            professional_object_ids=[self.revenue_object.id],
            required_action="support_claim",
        )
        self.workspace.attach_branch_context_delta(
            branch_id=self.branch.id,
            binding_id=launch.binding_id,
            context_id=context.id,
            controller=self.controller,
            config=self.config,
            actor="analyst",
        )
        paths = attempt_paths(self.workspace.store, self.branch.id, launch.binding_id)
        atomic_write(
            paths.checkpoints / "0001.json",
            canonical_json(
                {
                    "schema": "research-branch-checkpoint/v1",
                    "branch_id": self.branch.id,
                    "binding_id": launch.binding_id,
                    "sequence": 1,
                    "predecessor_id": None,
                    "candidate_claims": [
                        {
                            "claim_id": "unacknowledged",
                            "text": "The annual filing supports revenue.",
                            "support_relations": [
                                {
                                    "assertion_id": assertion.id,
                                    "professional_object_id": self.revenue_object.id,
                                }
                            ],
                            "contradiction_relations": [],
                            "uncertainty": [],
                            "scope": {},
                        }
                    ],
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
        with self.assertRaises(RuntimeFailure):
            self.workspace.collect_branch_checkpoint(
                branch_id=self.branch.id,
                binding_id=launch.binding_id,
                relative_path="0001.json",
            )

    def test_resume_uses_new_persistent_session_and_exact_checkpoint(self) -> None:
        launch = self._launch(session="first-persistent-session")
        self._acknowledge(launch)
        checkpoint = self._write_checkpoint(
            launch.binding_id,
            "0001.json",
            {
                "schema": "research-branch-checkpoint/v1",
                "branch_id": self.branch.id,
                "binding_id": launch.binding_id,
                "sequence": 1,
                "predecessor_id": None,
                "candidate_claims": [],
                "rivals": [],
                "source_request_ids": [],
                "artifact_proposals": [],
                "unresolved_questions": ["Research remains open."],
                "next_action": "Resume in a fresh persistent session.",
                "disposition": "continue",
                "refusal": None,
            },
        )
        resumed = self._launch(
            resume_checkpoint_id=checkpoint.id,
            session="second-persistent-session",
        )
        binding = self.workspace.store.get_object(resumed.binding_id)
        instruction = self.workspace.store.get_object(resumed.instruction_id)
        self.assertEqual(launch.binding_id, binding.payload["predecessor_binding_id"])
        self.assertEqual(checkpoint.id, binding.payload["resume_checkpoint_id"])
        self.assertEqual("resume", instruction.payload["instruction_kind"])

    def test_direct_conformance_runner_refuses_codex(self) -> None:
        with self.assertRaises(AuthorityError):
            self.workspace.run_context(
                context_id=self.context.id,
                argv=["/usr/local/bin/codex", "exec", "research"],
            )


if __name__ == "__main__":
    unittest.main()
