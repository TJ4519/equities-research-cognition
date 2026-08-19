from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_workspace import AuthorityError, ResearchWorkspace, RuntimeFailure
from research_workspace.branch_workspace import attempt_paths
from research_workspace.util import atomic_write, canonical_json, read_regular_file

from .test_ntm_persistent_research_branch import FakeNtmControl


class DiscoverySupportChallengeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = ResearchWorkspace.initialise(self.root / "workspace")
        self.controller = FakeNtmControl()
        self.codex_binary = self.root / "fake-codex"
        self.codex_binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.codex_binary.chmod(0o700)
        self.mandate = self.workspace.create_mandate(
            title="Micron NTM research episode",
            decision_use="Internal post-results research",
            actor="analyst",
            policy={"authorised_actors": ["analyst"]},
        )
        self.method = self.workspace.register_method(
            name="persistent-evidence-research",
            version="v1",
            purpose="Discover evidence, support claims, and challenge the result",
            output_kinds=["typed_claims"],
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
                "Work out what the results change about the HBM view and identify "
                "evidence that can support the historical revenue update."
            ),
            evidence_cutoff="2025-10-04T00:00:00+00:00",
            intended_use="Internal post-results research",
            prior_perspective_id=self.perspective.id,
        )
        self.commission = self.workspace.confirm_commission(
            episode_id=self.episode.id,
            actor="analyst",
            purpose="Discover and test evidence that can change the prior view",
            subject_ids=[],
            method_ids=[self.method.id],
            output_kinds=["typed_claims"],
            unresolved_questions=["Which source can support annual revenue?"],
            limits={"authority": "provisional_only"},
        )
        self.revenue_object = self.workspace.create_professional_object(
            mandate_id=self.mandate.id,
            kind="historical_model_input",
            label="FY2025 consolidated GAAP revenue",
            attributes={"metric": "revenue", "period": "FY2025"},
            binding={"named_range": "FY25_REVENUE_USDM"},
            authority="human_confirmed",
            actor="analyst",
        )
        self.seed_path = self.root / "earnings-release.txt"
        self.seed_path.write_text(
            "Micron reported FY2025 revenue of 37,378 USDm in its earnings release.",
            encoding="utf-8",
        )
        self.seed_source = self.workspace.capture_source(
            mandate_id=self.mandate.id,
            path=self.seed_path,
            source_class="earnings_release",
            rights={
                "retain": True,
                "internal_use": True,
                "model_access": True,
            },
            metadata={"issuer": "Micron"},
            published_at="2025-09-23T00:00:00+00:00",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _launch(self, branch_id: str, session: str, role: str):
        return self.workspace.launch_research_branch(
            branch_id=branch_id,
            controller=self.controller,
            codex_binary=self.codex_binary.resolve(),
            model="gpt-5.6-codex",
            role_name=role,
            actor="analyst",
            session=session,
        )

    def _acknowledge(self, branch_id: str, launch) -> None:
        branch = self.workspace.store.get_object(branch_id)
        binding = self.workspace.store.get_object(launch.binding_id)
        instruction = self.workspace.store.get_object(launch.instruction_id)
        paths = attempt_paths(self.workspace.store, branch_id, binding.id)
        atomic_write(
            paths.outbox / f"acknowledgement-{instruction.id}.json",
            canonical_json(
                {
                    "schema": "research-branch-acknowledgement/v1",
                    "branch_id": branch_id,
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
            branch_id=branch_id,
            binding_id=binding.id,
            instruction_id=instruction.id,
        )

    def _write_checkpoint(
        self,
        *,
        branch_id: str,
        binding_id: str,
        sequence: int,
        predecessor_id: str | None,
        candidate_claims: list[dict],
        source_request_ids: list[str],
        disposition: str,
        unresolved_questions: list[str] | None = None,
    ):
        paths = attempt_paths(self.workspace.store, branch_id, binding_id)
        filename = f"{sequence:04d}.json"
        atomic_write(
            paths.checkpoints / filename,
            canonical_json(
                {
                    "schema": "research-branch-checkpoint/v1",
                    "branch_id": branch_id,
                    "binding_id": binding_id,
                    "sequence": sequence,
                    "predecessor_id": predecessor_id,
                    "candidate_claims": candidate_claims,
                    "rivals": [],
                    "source_request_ids": source_request_ids,
                    "artifact_proposals": [],
                    "unresolved_questions": unresolved_questions or [],
                    "next_action": None,
                    "disposition": disposition,
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        return self.workspace.collect_branch_checkpoint(
            branch_id=branch_id,
            binding_id=binding_id,
            relative_path=filename,
        )

    def _complete_support_branch(
        self,
        *,
        branch_id: str,
        launch,
        claim_id: str,
        claim_text: str,
        assertion_id: str,
        uncertainty: list[str] | None = None,
    ):
        self._acknowledge(branch_id, launch)
        claim = {
            "claim_id": claim_id,
            "text": claim_text,
            "support_relations": [
                {
                    "assertion_id": assertion_id,
                    "professional_object_id": self.revenue_object.id,
                }
            ],
            "contradiction_relations": [],
            "uncertainty": uncertainty or [],
            "scope": {"use": "historical revenue analysis"},
        }
        checkpoint = self._write_checkpoint(
            branch_id=branch_id,
            binding_id=launch.binding_id,
            sequence=1,
            predecessor_id=None,
            candidate_claims=[claim],
            source_request_ids=[],
            disposition="complete",
        )
        self.workspace.observe_branch_completion(
            branch_id=branch_id,
            binding_id=launch.binding_id,
            controller=self.controller,
        )
        paths = attempt_paths(self.workspace.store, branch_id, launch.binding_id)
        atomic_write(
            paths.outbox / "result.json",
            canonical_json(
                {
                    "schema": "research-branch-result/v1",
                    "branch_id": branch_id,
                    "binding_id": launch.binding_id,
                    "checkpoint_id": checkpoint.id,
                    "summary": claim_text,
                    "claims": [claim],
                    "artifacts": [],
                    "memory_proposals": [],
                    "unresolved_questions": uncertainty or [],
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        return self.workspace.collect_branch_result(
            branch_id=branch_id,
            binding_id=launch.binding_id,
        )

    def _launch_record(self, binding_id: str) -> dict:
        events = [
            self.workspace.store.get_object(relation.object_id)
            for relation in self.workspace.store.relations_from(binding_id, "has_event")
        ]
        rows = [
            event.payload["details"]
            for event in events
            if event.payload["event_kind"] == "codex_launch_bound"
        ]
        self.assertEqual(1, len(rows))
        return rows[0]

    def test_discovery_support_and_fresh_challenge_use_separate_ntm_sessions(self) -> None:
        discovery_context = self.workspace.build_discovery_context(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            purpose="Discover a filing that can support the annual revenue object",
            professional_object_ids=[self.revenue_object.id],
            source_ids=[self.seed_source.id],
            allow_codex_search=True,
        )
        discovery_branch = self.workspace.create_research_branch(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            branch_kind="research",
            title="Discover annual revenue evidence",
            question="Find the filed annual source for FY2025 revenue.",
            context_ids=[discovery_context.id],
            expected_outputs=["source_requests", "leads"],
            authority_ceiling="discovery_only",
            created_by="analyst",
        )
        discovery_launch = self._launch(
            discovery_branch.id,
            "micron-discovery",
            "research_worker",
        )
        self._acknowledge(discovery_branch.id, discovery_launch)
        discovery_paths = attempt_paths(
            self.workspace.store,
            discovery_branch.id,
            discovery_launch.binding_id,
        )
        source_request_payload = {
            "schema": "research-source-request/v1",
            "branch_id": discovery_branch.id,
            "binding_id": discovery_launch.binding_id,
            "external_request_id": "micron-2025-10k",
            "request_kind": "url",
            "locator": "Micron FY2025 Form 10-K",
            "source_class": "annual_filing",
            "purpose": "Support FY2025 consolidated GAAP revenue",
            "rationale": "The preliminary earnings release cannot support the historical line.",
            "professional_object_ids": [self.revenue_object.id],
            "rights_needed": {"internal_use": True, "model_access": True},
        }
        atomic_write(
            discovery_paths.source_requests / "micron-2025-10k.json",
            canonical_json(source_request_payload).encode("utf-8"),
        )
        source_request = self.workspace.collect_branch_source_request(
            branch_id=discovery_branch.id,
            binding_id=discovery_launch.binding_id,
            relative_path="micron-2025-10k.json",
        )
        discovery_checkpoint = self._write_checkpoint(
            branch_id=discovery_branch.id,
            binding_id=discovery_launch.binding_id,
            sequence=1,
            predecessor_id=None,
            candidate_claims=[],
            source_request_ids=[source_request.id],
            disposition="complete",
            unresolved_questions=["The filing must be captured and admitted by the host."],
        )
        self.workspace.observe_branch_completion(
            branch_id=discovery_branch.id,
            binding_id=discovery_launch.binding_id,
            controller=self.controller,
        )
        atomic_write(
            discovery_paths.outbox / "result.json",
            canonical_json(
                {
                    "schema": "research-branch-result/v1",
                    "branch_id": discovery_branch.id,
                    "binding_id": discovery_launch.binding_id,
                    "checkpoint_id": discovery_checkpoint.id,
                    "summary": "The annual filing is the next evidence source to capture.",
                    "claims": [],
                    "artifacts": [],
                    "memory_proposals": [],
                    "source_request_ids": [source_request.id],
                    "leads": [
                        {
                            "description": "The annual filing should contain the final FY2025 revenue assertion.",
                            "authority": "discovery_only",
                        }
                    ],
                    "unresolved_questions": ["Capture and inspect the annual filing."],
                    "refusal": None,
                }
            ).encode("utf-8"),
        )
        discovery_outcome = self.workspace.collect_branch_result(
            branch_id=discovery_branch.id,
            binding_id=discovery_launch.binding_id,
        )
        discovery_result = self.workspace.store.get_object(discovery_outcome.result_id)
        discovery_control = self._launch_record(discovery_launch.binding_id)
        self.assertTrue(discovery_control["search_enabled"])
        self.assertIn(
            b"--search",
            read_regular_file(Path(discovery_control["launcher_path"])),
        )
        self.assertEqual([], discovery_result.payload["claim_ids"])

        filing_path = self.root / "micron-2025-10k.txt"
        filing_path.write_text(
            "Micron FY2025 consolidated GAAP revenue was 37,378 USDm.",
            encoding="utf-8",
        )
        filing_source = self.workspace.capture_source(
            mandate_id=self.mandate.id,
            path=filing_path,
            source_class="annual_filing",
            rights={
                "retain": True,
                "internal_use": True,
                "model_access": True,
            },
            metadata={"issuer": "Micron"},
            published_at="2025-10-03T00:00:00+00:00",
        )
        filing_assertion = self.workspace.create_assertion(
            source_id=filing_source.id,
            locator="consolidated statements of operations",
            content="FY2025 consolidated GAAP revenue was 37,378 USDm",
            attributes={"value": "37378", "unit": "USD millions"},
            proposed_by="host-capture",
        )
        self.workspace.decide_evidence_use(
            episode_id=self.episode.id,
            assertion_id=filing_assertion.id,
            professional_object_id=self.revenue_object.id,
            intended_use=self.episode.payload["intended_use"],
            permitted_actions=["support_claim"],
            decision="admit",
            rationale="The filed annual report is admitted for the historical revenue object.",
            actor="analyst",
        )
        support_context = self.workspace.build_context(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            purpose="Determine the supported historical revenue claim",
            assertion_ids=[filing_assertion.id],
            professional_object_ids=[self.revenue_object.id],
            required_action="support_claim",
        )
        support_branch = self.workspace.create_research_branch(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            branch_kind="research",
            title="Support annual revenue claim",
            question="What annual revenue claim is supported by the filed source?",
            context_ids=[support_context.id],
            expected_outputs=["typed_claims"],
            authority_ceiling="provisional_only",
            created_by="analyst",
            input_object_ids=[discovery_result.id],
            parent_branch_id=discovery_branch.id,
        )
        support_launch = self._launch(
            support_branch.id,
            "micron-support",
            "research_worker",
        )
        support_outcome = self._complete_support_branch(
            branch_id=support_branch.id,
            launch=support_launch,
            claim_id="supported-revenue",
            claim_text="Micron FY2025 consolidated GAAP revenue was 37,378 USDm.",
            assertion_id=filing_assertion.id,
        )
        support_result = self.workspace.store.get_object(support_outcome.result_id)
        support_control = self._launch_record(support_launch.binding_id)
        self.assertFalse(support_control["search_enabled"])
        self.assertNotIn(
            b"--search",
            read_regular_file(Path(support_control["launcher_path"])),
        )
        with self.assertRaises(AuthorityError):
            self.workspace.attach_branch_context_delta(
                branch_id=support_branch.id,
                binding_id=support_launch.binding_id,
                context_id=discovery_context.id,
                controller=self.controller,
                actor="analyst",
            )

        support_claim_id = support_result.payload["claim_ids"][0]
        challenge_branch = self.workspace.create_research_branch(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            branch_kind="challenge",
            title="Challenge annual revenue claim",
            question="Can the claim be narrowed or contradicted by its admitted evidence?",
            context_ids=[support_context.id],
            expected_outputs=["typed_claims"],
            authority_ceiling="provisional_challenge_only",
            created_by="analyst",
            input_object_ids=[support_result.id, support_claim_id],
            parent_branch_id=support_branch.id,
        )
        challenge_launch = self._launch(
            challenge_branch.id,
            "micron-challenge",
            "adversarial_review",
        )
        challenge_outcome = self._complete_support_branch(
            branch_id=challenge_branch.id,
            launch=challenge_launch,
            claim_id="challenged-revenue",
            claim_text=(
                "The filing supports FY2025 consolidated GAAP revenue of 37,378 USDm; "
                "the claim does not establish any forecast or non-GAAP measure."
            ),
            assertion_id=filing_assertion.id,
            uncertainty=["The claim is limited to the historical consolidated GAAP object."],
        )
        self.assertNotEqual(discovery_launch.binding_id, support_launch.binding_id)
        self.assertNotEqual(support_launch.binding_id, challenge_launch.binding_id)
        self.assertNotEqual(support_outcome.result_id, challenge_outcome.result_id)
        self.assertEqual(
            [support_branch.id],
            [
                relation.object_id
                for relation in self.workspace.store.relations_from(
                    discovery_branch.id,
                    "spawned_branch",
                )
            ],
        )
        self.assertEqual(
            [challenge_branch.id],
            [
                relation.object_id
                for relation in self.workspace.store.relations_from(
                    support_branch.id,
                    "spawned_branch",
                )
            ],
        )

    def test_discovery_context_requires_explicit_model_access_right(self) -> None:
        restricted_path = self.root / "restricted.txt"
        restricted_path.write_text("Restricted source.", encoding="utf-8")
        restricted = self.workspace.capture_source(
            mandate_id=self.mandate.id,
            path=restricted_path,
            source_class="licensed_research",
            rights={"retain": True, "internal_use": True, "model_access": False},
            metadata={},
        )
        with self.assertRaises(AuthorityError):
            self.workspace.build_discovery_context(
                episode_id=self.episode.id,
                commission_id=self.commission.id,
                method_id=self.method.id,
                purpose="Read a restricted source",
                professional_object_ids=[self.revenue_object.id],
                source_ids=[restricted.id],
                allow_codex_search=False,
            )

    def test_discovery_branch_rejects_supported_claim_output(self) -> None:
        context = self.workspace.build_discovery_context(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            purpose="Discover candidate annual sources",
            professional_object_ids=[self.revenue_object.id],
            source_ids=[self.seed_source.id],
            allow_codex_search=False,
        )
        branch = self.workspace.create_research_branch(
            episode_id=self.episode.id,
            commission_id=self.commission.id,
            method_id=self.method.id,
            branch_kind="research",
            title="Discovery cannot authorise claims",
            question="Find a candidate source.",
            context_ids=[context.id],
            expected_outputs=["source_requests"],
            authority_ceiling="discovery_only",
            created_by="analyst",
        )
        launch = self._launch(branch.id, "discovery-no-claims", "research_worker")
        self._acknowledge(branch.id, launch)
        paths = attempt_paths(self.workspace.store, branch.id, launch.binding_id)
        atomic_write(
            paths.checkpoints / "0001.json",
            canonical_json(
                {
                    "schema": "research-branch-checkpoint/v1",
                    "branch_id": branch.id,
                    "binding_id": launch.binding_id,
                    "sequence": 1,
                    "predecessor_id": None,
                    "candidate_claims": [
                        {
                            "claim_id": "forbidden-discovery-claim",
                            "text": "The source proves revenue.",
                            "support_relations": [],
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
                branch_id=branch.id,
                binding_id=launch.binding_id,
                relative_path="0001.json",
            )


if __name__ == "__main__":
    unittest.main()
