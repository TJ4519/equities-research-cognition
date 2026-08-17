from __future__ import annotations

from hashlib import sha256
import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from product.campaign.models import Artifact, TraceLink, canonical_digest
from product.campaign.services import (
    approve_proposal,
    create_campaign,
    record_proposal,
    skill_catalog,
    workbench_catalog,
)
from product.review.intake import admit_population, assign_case, seal_campaign
from product.review.models import (
    AnalystEnrollment,
    QueueAssignment,
    ResearchCase,
)


class LeanCampaignAdmissionTests(TestCase):
    def setUp(self) -> None:
        self.director = get_user_model().objects.create_user("director")
        self.analyst = get_user_model().objects.create_user("analyst")
        self.enrollment = AnalystEnrollment.objects.create(
            user=self.analyst,
            scope_code="equities",
            qualification_basis="Named equities analyst",
            attested_by="research director",
        )
        self.campaign = create_campaign(
            director=self.director,
            title="Decision packet",
            issuer_or_security="NVIDIA",
            equities_decision_use="Decide whether evidence changes the position.",
            evidence_cutoff="2026-05-31",
            question="What explains the reported revenue change?",
        )
        proposal = record_proposal(
            campaign=self.campaign,
            author="planner",
            protocol="research_worker",
            title="Produce one reviewable judgment",
            task="Test the demand interpretation against exact evidence.",
            contract={
                "workbenches": [
                    {
                        key: workbench_catalog()[0][key]
                        for key in (
                            "workbench_id",
                            "version",
                            "protocol_sha256",
                        )
                    }
                ],
                "research_state": {"mode": "root"},
                "decision_hinge": (
                    "Does the exact evidence change the commissioned decision?"
                ),
                "claim_ceiling": "Preserve only the exact bounded claim.",
                "reasoning_operators": [
                    {
                        **next(
                            item
                            for item in skill_catalog()
                            if item["name"]
                            == "research-frame-search-with-domain-mechanisms"
                        ),
                        "failure_tested": "proxy-to-target substitution",
                        "expected_epistemic_delta": "preserve a bounded claim",
                        "kill_condition": "no research state changes",
                    }
                ],
            },
        )
        self.order = approve_proposal(proposal, user=self.director)
        unit = {
            "unit_id": "revenue-demand-claim",
            "question": "Does the evidence license a durable-demand claim?",
            "source_identity": "Issuer filing",
            "source_url": "https://example.com/filing",
            "source_locator": "Revenue note",
            "exact_passage": "Revenue increased during the period.",
            "context_items": [],
            "rubric": [
                {
                    "label": "requires narrowing",
                    "criterion": "Separate demand from price, mix and timing.",
                }
            ],
            "provisional": {"decision": "licensed"},
            "comparison": {"decision": "requires_narrowing"},
            "transition": {"state": "candidate"},
        }
        content = json.dumps(unit, sort_keys=True).encode() + b"\n"
        self.artifact = Artifact.objects.create(
            campaign=self.campaign,
            work_order=self.order,
            kind="review-units",
            relative_path="review-units.jsonl",
            version=1,
            media_type="application/jsonl",
            content=content,
            digest=sha256(content).hexdigest(),
        )
        relation = {
            "campaign": str(self.campaign.pk),
            "work_order": str(self.order.pk),
            "artifact": self.artifact.pk,
            "artifact_digest": self.artifact.digest,
            "trace_id": "a" * 32,
            "observation_id": "observation-1",
            "conversation_id": "conversation-1",
            "call_id": "call-1",
        }
        TraceLink.objects.create(
            campaign=self.campaign,
            work_order=self.order,
            artifact=self.artifact,
            trace_id=relation["trace_id"],
            observation_id=relation["observation_id"],
            conversation_id=relation["conversation_id"],
            call_id=relation["call_id"],
            digest=canonical_digest(relation),
        )

    def test_seal_admission_and_assignment_are_three_separate_transitions(self) -> None:
        seal = seal_campaign(self.campaign, self.director)
        admission = admit_population(
            seal,
            requested_by=self.director,
            idempotency_key="decision-packet-v1",
        )

        case = ResearchCase.objects.get(population_admission=admission)
        self.assertFalse(QueueAssignment.objects.filter(case=case).exists())

        assignment = assign_case(case=case, enrollment=self.enrollment)

        self.assertEqual(self.enrollment, assignment.enrollment)
        self.assertEqual(case, assignment.case)
        self.assertEqual("langfuse_observed_run", case.subject_mode)
