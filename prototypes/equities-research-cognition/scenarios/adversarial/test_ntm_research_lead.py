from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_workspace import ResearchWorkspace, ValidationError
from research_workspace.branch_workspace import attempt_paths
from research_workspace.research_lead import ResearchLead
from research_workspace.util import atomic_write, canonical_json

from .test_ntm_persistent_research_branch import FakeNtmControl


class PersistentResearchLeadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = ResearchWorkspace.initialise(self.root / "workspace")
        self.controller = FakeNtmControl()
        self.codex_binary = self.root / "fake-codex"
        self.codex_binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.codex_binary.chmod(0o700)
        self.mandate = self.workspace.create_mandate(
            title="Research lead test",
            decision_use="Internal post-results research",
            actor="analyst",
            policy={"authorised_actors": ["analyst"]},
        )
        self.method = self.workspace.register_method(
            name="research-lead-and-evidence-work",
            version="v1",
            purpose="Plan and perform purpose-bound research",
            output_kinds=["research_plan", "typed_claims"],
            required_actions=["plan_research", "support_claim"],
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
            title="Micron results",
            original_request=(
                "Work out what the results change about HBM, check the model where "
                "relevant, and produce the work worth keeping."
            ),
            evidence_cutoff="2025-10-04T00:00:00+00:00",
            intended_use="Internal post-results research",
            prior_perspective_id=self.perspective.id,
        )
        self.commission = self.workspace.confirm_commission(
            episode_id=self.episode.id,
            actor="analyst",
            purpose="Determine what the results change about the prior HBM view",
            subject_ids=[],
            method_ids=[self.method.id],
            output_kinds=["research_plan", "typed_claims"],
            unresolved_questions=["Which evidence and artifact work can change the answer?"],
            limits={"authority": "provisional_only"},
        )
        self.professional_object = self.workspace.create_professional_object(
            mandate_id=self.mandate.id,
            kind="historical_model_input",
            label="FY2025 consolidated GAAP revenue",
            attributes={"metric": "revenue", "period": "FY2025"},
            binding={"named_range": "FY25_REVENUE_USDM"},
            authority="human_confirmed",
            actor="analyst",
        )
        self.lead = ResearchLead(self.workspace)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _acknowledge(self, launch) -> None:
        branch = self.workspace.store.get_object(launch.branch_id)
        binding = self.workspace.store.get_object(launch.binding_id)
        instruction = self.workspace.store.get_object(launch.instruction_id)
        paths = attempt_paths(
            self.workspace.store,
            launch.branch_id,
            launch.binding_id,
        )
        atomic_write(
            paths.outbox / f"acknowledgement-{instruction.id}.json",
            canonical_json(
                {
                    "schema": "research-branch-acknowledgement/v1",
                    "branch_id": branch.id,
                    "binding_id": binding.id,
                    "instruction_id": instruction.id,
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
        self.workspace.collect_branch_acknowledgement(
            branch_id=branch.id,
            binding_id=binding.id,
            instruction_id=instruction.id,
        )

    def _produce_plan_artifact(self) -> str:
        launch = self.lead.start(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            professional_object_ids=[self.professional_object.id],
            controller=self.controller,
            codex_binary=self.codex_binary.resolve(),
            model="gpt-5.6-codex",
            actor="analyst",
            session="micron-research-lead",
        )
        self._acknowledge(launch)
        paths = attempt_paths(
            self.workspace.store,
            launch.branch_id,
            launch.binding_id,
        )
        atomic_write(
            paths.checkpoints / "0001.json",
            canonical_json(
                {
                    "schema": "research-branch-checkpoint/v1",
                    "branch_id": launch.branch_id,
                    "binding_id": launch.binding_id,
                    "sequence": 1,
                    "predecessor_id": None,
                    "candidate_claims": [],
                    "rivals": [],
                    "source_request_ids": [],
                    "artifact_proposals": [{"kind": "research_plan"}],
                    "unresolved_questions": [],
                    "next_action": None,
                    "disposition": "complete",
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        checkpoint = self.workspace.collect_branch_checkpoint(
            branch_id=launch.branch_id,
            binding_id=launch.binding_id,
            relative_path="0001.json",
        )
        plan = {
            "schema": "research-plan/v1",
            "summary": "Discover the filed source, then test the supported historical claim.",
            "proposals": [
                {
                    "proposal_id": "discover-filing",
                    "title": "Discover the filed annual source",
                    "question": "Find the source that can support the historical revenue object.",
                    "branch_kind": "research",
                    "context_kind": "discovery",
                    "method_id": self.method.id,
                    "professional_object_ids": [self.professional_object.id],
                    "evidence_needs": [
                        {"source_class": "annual_filing", "purpose": "historical revenue"}
                    ],
                    "input_object_ids": [],
                    "expected_outputs": ["source_requests", "leads"],
                    "authority_ceiling": "discovery_only",
                    "depends_on": [],
                    "stop_conditions": ["A source request identifies the filed annual report."],
                    "rationale": "The current evidence cannot support the model route.",
                },
                {
                    "proposal_id": "support-revenue",
                    "title": "Test the annual revenue claim",
                    "question": "Determine the annual revenue claim licensed by the filed source.",
                    "branch_kind": "research",
                    "context_kind": "support",
                    "method_id": self.method.id,
                    "professional_object_ids": [self.professional_object.id],
                    "evidence_needs": [],
                    "input_object_ids": [],
                    "expected_outputs": ["typed_claims"],
                    "authority_ceiling": "provisional_only",
                    "depends_on": ["discover-filing"],
                    "stop_conditions": ["The admitted evidence supports or refuses the claim."],
                    "rationale": "The evidential route must be tested separately from discovery.",
                },
            ],
            "unresolved_questions": ["The annual filing has not yet been captured."],
        }
        atomic_write(
            paths.artifacts / "research-plan.json",
            canonical_json(plan).encode("utf-8"),
        )
        self.workspace.observe_branch_completion(
            branch_id=launch.branch_id,
            binding_id=launch.binding_id,
            controller=self.controller,
        )
        atomic_write(
            paths.outbox / "result.json",
            canonical_json(
                {
                    "schema": "research-branch-result/v1",
                    "branch_id": launch.branch_id,
                    "binding_id": launch.binding_id,
                    "checkpoint_id": checkpoint.id,
                    "summary": plan["summary"],
                    "claims": [],
                    "artifacts": [
                        {
                            "path": "artifacts/research-plan.json",
                            "kind": "research_plan",
                            "title": "Micron research plan",
                            "media_type": "application/json",
                        }
                    ],
                    "memory_proposals": [],
                    "unresolved_questions": plan["unresolved_questions"],
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        outcome = self.workspace.collect_branch_result(
            branch_id=launch.branch_id,
            binding_id=launch.binding_id,
        )
        self.assertEqual(1, len(outcome.artifact_ids))
        return outcome.artifact_ids[0]

    def test_lead_plan_is_validated_and_specific_proposals_are_materialised(self) -> None:
        plan_artifact_id = self._produce_plan_artifact()
        plan = self.lead.validate_plan(plan_artifact_id)
        self.assertEqual(
            ["discover-filing", "support-revenue"],
            [proposal["proposal_id"] for proposal in plan["proposals"]],
        )
        seed_path = self.root / "seed.txt"
        seed_path.write_text("A preliminary result points to the annual filing.", encoding="utf-8")
        seed_source = self.workspace.capture_source(
            mandate_id=self.mandate.id,
            path=seed_path,
            source_class="earnings_release",
            rights={"retain": True, "model_access": True},
            metadata={},
        )
        discovery_context = self.workspace.build_discovery_context(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            purpose="Discover the filed annual source",
            professional_object_ids=[self.professional_object.id],
            source_ids=[seed_source.id],
            allow_codex_search=True,
        )
        discovery = self.lead.materialise_proposal(
            artifact_id=plan_artifact_id,
            proposal_id="discover-filing",
            context_ids=[discovery_context.id],
            actor="analyst",
        )
        discovery_branch = self.workspace.store.get_object(discovery.branch_id)
        self.assertEqual("discovery", self.workspace._branch_context_kind(discovery.branch_id))
        self.assertEqual("lead", self.workspace.store.get_object(
            discovery_branch.payload["parent_branch_id"]
        ).payload["branch_kind"])

        filing_path = self.root / "filing.txt"
        filing_path.write_text("FY2025 revenue was 37,378 USDm.", encoding="utf-8")
        filing_source = self.workspace.capture_source(
            mandate_id=self.mandate.id,
            path=filing_path,
            source_class="annual_filing",
            rights={"retain": True, "model_access": True},
            metadata={},
        )
        assertion = self.workspace.create_assertion(
            source_id=filing_source.id,
            locator="revenue",
            content="FY2025 revenue was 37,378 USDm",
            attributes={"value": "37378"},
            proposed_by="host",
        )
        self.workspace.decide_evidence_use(
            episode_id=self.episode.id,
            assertion_id=assertion.id,
            professional_object_id=self.professional_object.id,
            intended_use=self.episode.payload["intended_use"],
            permitted_actions=["support_claim"],
            decision="admit",
            rationale="The filing is admitted for the historical object.",
            actor="analyst",
        )
        support_context = self.workspace.build_context(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            purpose="Test the annual revenue claim",
            assertion_ids=[assertion.id],
            professional_object_ids=[self.professional_object.id],
            required_action="support_claim",
        )
        support = self.lead.materialise_proposal(
            artifact_id=plan_artifact_id,
            proposal_id="support-revenue",
            context_ids=[support_context.id],
            actor="analyst",
        )
        self.assertEqual("support", self.workspace._branch_context_kind(support.branch_id))
        decisions = [
            self.workspace.store.get_object(relation.object_id)
            for relation in self.workspace.store.relations_from(
                plan_artifact_id,
                "targeted_by",
            )
        ]
        self.assertEqual(2, len(decisions))

    def test_cyclic_model_plan_is_rejected(self) -> None:
        artifact_id = self._produce_plan_artifact()
        artifact = self.workspace.store.get_object(artifact_id)
        blob = self.workspace.store.get_blob(artifact.payload["blob_digest"])
        plan = canonical_json(
            {
                "schema": "research-plan/v1",
                "summary": "Cyclic plan",
                "proposals": [
                    {
                        "proposal_id": "a",
                        "title": "A",
                        "question": "A?",
                        "branch_kind": "research",
                        "context_kind": "support",
                        "method_id": self.method.id,
                        "professional_object_ids": [self.professional_object.id],
                        "evidence_needs": [],
                        "input_object_ids": [],
                        "expected_outputs": ["typed_claims"],
                        "authority_ceiling": "provisional_only",
                        "depends_on": ["b"],
                        "stop_conditions": [],
                        "rationale": "A",
                    },
                    {
                        "proposal_id": "b",
                        "title": "B",
                        "question": "B?",
                        "branch_kind": "research",
                        "context_kind": "support",
                        "method_id": self.method.id,
                        "professional_object_ids": [self.professional_object.id],
                        "evidence_needs": [],
                        "input_object_ids": [],
                        "expected_outputs": ["typed_claims"],
                        "authority_ceiling": "provisional_only",
                        "depends_on": ["a"],
                        "stop_conditions": [],
                        "rationale": "B",
                    },
                ],
                "unresolved_questions": [],
            }
        ).encode("utf-8")
        cyclic_blob = self.workspace.store.put_blob(plan, media_type="application/json")
        cyclic_artifact = self.workspace.store.put_object(
            "artifact",
            {
                **artifact.payload,
                "blob_digest": cyclic_blob.digest,
                "filename": "cyclic-research-plan.json",
            },
        )
        with self.assertRaises(ValidationError):
            self.lead.validate_plan(cyclic_artifact.id)


if __name__ == "__main__":
    unittest.main()
