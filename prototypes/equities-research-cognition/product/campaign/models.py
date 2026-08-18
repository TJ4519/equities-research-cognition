from __future__ import annotations

from hashlib import sha256
import json
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def canonical_digest(value: object) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def canonical_decimal(value: object) -> str:
    return format(Decimal(str(value)).normalize(), "f")


class ImmutableQuerySet(models.QuerySet):
    def reject_mutation(self, *args: object, **kwargs: object) -> None:
        raise ValidationError("campaign facts are append-only")

    update = delete = bulk_create = bulk_update = reject_mutation


class AppendOnlyModel(models.Model):
    objects = ImmutableQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args: object, **kwargs: object) -> None:
        if not self._state.adding:
            raise ValidationError("campaign facts are append-only")
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args: object, **kwargs: object) -> None:
        raise ValidationError("campaign facts are append-only")


class ResearchCampaign(AppendOnlyModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    director = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=180)
    issuer_or_security = models.CharField(max_length=240)
    equities_decision_use = models.TextField()
    evidence_cutoff = models.DateField()
    commissioned_question = models.TextField()
    ntm_session = models.CharField(max_length=80, unique=True, editable=False)
    artifact_root = models.TextField(unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Proposal(AppendOnlyModel):
    class Author(models.TextChoices):
        PLANNER = "planner", "Planner"
        DIRECTOR = "director", "Research director"
        RESEARCHER = "researcher", "Research worker"
        REVIEWER = "reviewer", "Adversarial reviewer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        ResearchCampaign, on_delete=models.PROTECT, related_name="proposals"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )
    author = models.CharField(max_length=16, choices=Author)
    author_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="campaign_proposals",
    )
    protocol = models.CharField(max_length=80)
    title = models.CharField(max_length=240)
    task = models.TextField()
    contract = models.JSONField(default=dict, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if self.parent_id and self.parent.campaign_id != self.campaign_id:
            raise ValidationError("proposal parent crosses campaign custody")
        if self.author == self.Author.DIRECTOR and not self.author_user_id:
            raise ValidationError("director proposal requires attributed authorship")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "campaign": str(self.campaign_id),
                "parent": str(self.parent_id) if self.parent_id else None,
                "author": self.author,
                "author_user": self.author_user_id,
                "protocol": self.protocol,
                "title": self.title,
                "task": self.task,
                "contract": self.contract,
            }
        )
        if self.digest != expected:
            raise ValidationError("proposal digest does not match its exact content")


class ProposalDisposition(AppendOnlyModel):
    class Kind(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REVISION_REQUESTED = "revision_requested", "Revision requested"

    proposal = models.OneToOneField(
        Proposal, on_delete=models.PROTECT, related_name="disposition"
    )
    kind = models.CharField(max_length=24, choices=Kind)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ArtifactVersion(AppendOnlyModel):
    class Role(models.TextChoices):
        STARTING_ARTIFACT = "starting_artifact", "Starting artifact"
        SOURCE = "source", "Source"
        CANDIDATE = "candidate", "Candidate"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        ResearchCampaign, on_delete=models.PROTECT, related_name="input_artifacts"
    )
    role = models.CharField(max_length=32, choices=Role)
    filename = models.CharField(max_length=240)
    media_type = models.CharField(max_length=120)
    content = models.BinaryField()
    digest = models.CharField(max_length=64, editable=False)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="candidate_children",
    )
    candidate_from_pass = models.ForeignKey(
        "AdmissibilityDecision",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="candidate_artifacts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            not self.filename
            or self.filename in {".", ".."}
            or "/" in self.filename
            or "\\" in self.filename
        ):
            raise ValidationError("input artifact filename is unsafe")
        if self.digest != sha256(bytes(self.content)).hexdigest():
            raise ValidationError("input artifact digest does not match exact bytes")
        is_candidate = self.role == self.Role.CANDIDATE
        if is_candidate != bool(self.parent_id and self.candidate_from_pass_id):
            raise ValidationError(
                "candidate artifact requires exact parentage and pass authority"
            )
        if self.parent_id:
            decision = self.candidate_from_pass
            proposal = decision.proposal
            episode = proposal.episode
            if (
                self.parent.campaign_id != self.campaign_id
                or decision.outcome != AdmissibilityDecision.Outcome.PASS
                or proposal.starting_artifact_id != self.parent_id
                or episode.starting_artifact_id != self.parent_id
                or episode.campaign_id != self.campaign_id
                or episode.job.owner_id != self.campaign.director_id
            ):
                raise ValidationError(
                    "candidate artifact crosses its exact passing closure"
                )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("candidate_from_pass",),
                condition=models.Q(candidate_from_pass__isnull=False),
                name="model_change_one_candidate_per_pass",
            )
        ]


class RunSpecVersion(AppendOnlyModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.OneToOneField(
        ResearchCampaign, on_delete=models.PROTECT, related_name="run_spec"
    )
    objective = models.TextField()
    instruction = models.TextField()
    input_manifest = models.JSONField(default=list, editable=False)
    outcome_contract = models.JSONField(default=dict, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if not isinstance(self.input_manifest, list) or not self.input_manifest:
            raise ValidationError("run specification requires exact input artifacts")
        expected_keys = {"id", "role", "filename", "media_type", "sha256"}
        if any(
            not isinstance(item, dict) or set(item) != expected_keys
            for item in self.input_manifest
        ):
            raise ValidationError("run specification input manifest is malformed")
        ids = [item["id"] for item in self.input_manifest]
        if len(ids) != len(set(ids)):
            raise ValidationError("run specification repeats an input artifact")
        observed = {
            str(item.pk): {
                "id": str(item.pk),
                "role": item.role,
                "filename": item.filename,
                "media_type": item.media_type,
                "sha256": item.digest,
            }
            for item in ArtifactVersion.objects.filter(
                campaign_id=self.campaign_id, pk__in=ids
            )
        }
        if len(observed) != len(ids) or any(observed.get(item["id"]) != item for item in self.input_manifest):
            raise ValidationError("run specification input custody does not match")
        expected_outcome = {
            "schema_version": "bound-run-outcome/v1",
            "allowed_kinds": ["candidate", "refusal"],
            "authority": "provisional_only",
        }
        if self.outcome_contract != expected_outcome:
            raise ValidationError("run specification outcome contract is not bounded")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "campaign": str(self.campaign_id),
                "objective": self.objective,
                "instruction": self.instruction,
                "input_manifest": self.input_manifest,
                "outcome_contract": self.outcome_contract,
            }
        )
        if self.digest != expected:
            raise ValidationError("run specification digest does not match exact content")


class WorkOrder(AppendOnlyModel):
    class StateBasis(models.TextChoices):
        COMMISSION = "commission", "Commission"
        ACCEPTED_TRANSITION = "accepted_transition", "Accepted research state"
        CHALLENGED_TRANSITION = "challenged_transition", "Challenged research state"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        ResearchCampaign, on_delete=models.PROTECT, related_name="work_orders"
    )
    proposal = models.OneToOneField(
        Proposal, on_delete=models.PROTECT, related_name="work_order"
    )
    run_spec = models.ForeignKey(
        RunSpecVersion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="work_orders",
    )
    logical_role_id = models.UUIDField(default=uuid.uuid4, editable=False)
    protocol = models.CharField(max_length=80)
    proposal_digest = models.CharField(max_length=64, editable=False)
    input_artifact_ids = models.JSONField(default=list, editable=False)
    state_basis = models.CharField(
        max_length=24, choices=StateBasis, default=StateBasis.COMMISSION
    )
    input_state = models.ForeignKey(
        "ResearchStateTransition",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="dependent_work_orders",
    )
    packet = models.JSONField(default=dict, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            self.proposal.campaign_id != self.campaign_id
            or self.proposal_digest != self.proposal.digest
            or getattr(self.proposal, "disposition", None) is None
            or self.proposal.disposition.kind != ProposalDisposition.Kind.APPROVED
        ):
            raise ValidationError("work order lacks exact approved proposal authority")
        if (self.protocol == "bound_work") != bool(self.run_spec_id):
            raise ValidationError(
                "bound-work protocol and run specification must be present together"
            )
        if (
            self.proposal.protocol != self.protocol
            or self.packet.get("campaign_id") != str(self.campaign_id)
            or self.packet.get("work_order_id") != str(self.pk)
            or self.packet.get("logical_role_id") != str(self.logical_role_id)
            or self.packet.get("proposal_id") != str(self.proposal_id)
            or self.packet.get("proposal_digest") != self.proposal.digest
            or self.packet.get("protocol") != self.protocol
            or self.packet.get("task") != self.proposal.task
            or self.packet.get("contract") != self.proposal.contract
        ):
            raise ValidationError(
                "work-order packet does not derive from its exact approved proposal"
            )
        if self.run_spec_id:
            if self.run_spec.campaign_id != self.campaign_id:
                raise ValidationError("work order run specification crosses campaign custody")
            if (
                self.input_artifact_ids
                or self.state_basis != self.StateBasis.COMMISSION
                or self.input_state_id is not None
            ):
                raise ValidationError(
                    "bound work may use only its exact run-spec input custody"
                )
            expected_contract = {
                "workbenches": [],
                "reasoning_operators": [],
                "run_spec": {
                    "id": str(self.run_spec_id),
                    "sha256": self.run_spec.digest,
                },
                "authority": "provisional_only",
            }
            if (
                self.proposal.task != self.run_spec.instruction
                or self.proposal.contract != expected_contract
            ):
                raise ValidationError(
                    "bound proposal does not bind its exact run specification"
                )
            from .services import CampaignRejected, canonical_bound_work_packet

            try:
                expected_packet = canonical_bound_work_packet(
                    campaign=self.campaign,
                    proposal=self.proposal,
                    run_spec=self.run_spec,
                    order_id=self.pk,
                    logical_role_id=self.logical_role_id,
                )
            except CampaignRejected as exc:
                raise ValidationError(
                    "canonical bound work packet is unavailable"
                ) from exc
            if self.packet != expected_packet:
                raise ValidationError(
                    "work order packet does not match its canonical bound specification"
                )
        if self.protocol == "model_change_v0":
            if self.run_spec_id or self.input_artifact_ids:
                raise ValidationError(
                    "model change work may use only its exact versioned inputs"
                )
            from .model_change.services import (
                ModelChangeRejected,
                canonical_model_change_packet_for_order,
            )

            try:
                expected_packet = canonical_model_change_packet_for_order(self)
            except ModelChangeRejected as exc:
                raise ValidationError(
                    "canonical model change packet is unavailable"
                ) from exc
            if self.packet != expected_packet:
                raise ValidationError(
                    "work order packet does not match its canonical model change facts"
                )
        if self.state_basis == self.StateBasis.COMMISSION and self.input_state_id:
            raise ValidationError("commission-rooted work cannot bind a research state")
        if self.state_basis != self.StateBasis.COMMISSION:
            if not self.input_state_id or self.input_state.campaign_id != self.campaign_id:
                raise ValidationError("work-order research state crosses campaign custody")
            disposition = getattr(self.input_state, "disposition", None)
            permitted = (
                self.state_basis == self.StateBasis.ACCEPTED_TRANSITION
                and disposition
                and disposition.kind == ResearchStateDisposition.Kind.ACCEPTED
            ) or (
                self.state_basis == self.StateBasis.CHALLENGED_TRANSITION
                and self.protocol == "adversarial_review"
                and disposition
                and disposition.kind == ResearchStateDisposition.Kind.CHALLENGED
            )
            if not permitted:
                raise ValidationError("work order lacks exact research-state authority")
        digest_payload = {
                "id": str(self.pk),
                "campaign": str(self.campaign_id),
                "proposal": str(self.proposal_id),
                "logical_role_id": str(self.logical_role_id),
                "protocol": self.protocol,
                "proposal_digest": self.proposal_digest,
                "input_artifact_ids": self.input_artifact_ids,
                "state_basis": self.state_basis,
                "input_state": (
                    str(self.input_state_id) if self.input_state_id else None
                ),
                "packet": self.packet,
            }
        if self.run_spec_id:
            digest_payload["run_spec"] = str(self.run_spec_id)
            digest_payload["run_spec_sha256"] = self.run_spec.digest
        expected = canonical_digest(digest_payload)
        if self.digest != expected:
            raise ValidationError("work-order digest does not match its exact packet")


class RuntimeEvent(AppendOnlyModel):
    class Kind(models.TextChoices):
        LAUNCH = "launch", "Launch capacity"
        STATUS = "status", "Observe readiness"
        SEND = "send", "Send exact work order"
        STOP = "stop", "Stop campaign runtime"
        READBACK = "readback", "Read back Langfuse observations"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        ResearchCampaign, on_delete=models.PROTECT, related_name="runtime_events"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="runtime_events",
    )
    kind = models.CharField(max_length=16, choices=Kind)
    generation = models.PositiveIntegerField(default=1)
    request = models.JSONField(default=dict, editable=False)
    response = models.JSONField(null=True, editable=False)
    succeeded = models.BooleanField(default=False, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if self.work_order_id and self.work_order.campaign_id != self.campaign_id:
            raise ValidationError("runtime event crosses campaign custody")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "campaign": str(self.campaign_id),
                "work_order": (
                    str(self.work_order_id) if self.work_order_id else None
                ),
                "kind": self.kind,
                "generation": self.generation,
                "request": self.request,
                "response": self.response,
                "succeeded": self.succeeded,
            }
        )
        if self.digest != expected:
            raise ValidationError("runtime-event digest does not match exact evidence")


class Artifact(AppendOnlyModel):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(
        ResearchCampaign, on_delete=models.PROTECT, related_name="artifacts"
    )
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.PROTECT, related_name="artifacts"
    )
    kind = models.CharField(max_length=80)
    relative_path = models.TextField()
    version = models.PositiveIntegerField()
    media_type = models.CharField(max_length=120)
    content = models.BinaryField()
    digest = models.CharField(max_length=64, editable=False)
    observed_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if self.work_order.campaign_id != self.campaign_id:
            raise ValidationError("artifact crosses work-order custody")
        if self.relative_path.startswith("/") or ".." in self.relative_path.split("/"):
            raise ValidationError("artifact path escapes campaign custody")
        if self.digest != sha256(bytes(self.content)).hexdigest():
            raise ValidationError("artifact digest does not match exact bytes")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("work_order", "relative_path", "version"),
                name="lean_artifact_path_version",
            )
        ]


class ResearchStateTransition(AppendOnlyModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        ResearchCampaign, on_delete=models.PROTECT, related_name="state_transitions"
    )
    work_order = models.OneToOneField(
        WorkOrder, on_delete=models.PROTECT, related_name="state_transition"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="successors",
    )
    workbench_artifact = models.OneToOneField(
        Artifact, on_delete=models.PROTECT, related_name="research_workbench_result"
    )
    state_artifact = models.OneToOneField(
        Artifact, on_delete=models.PROTECT, related_name="research_state"
    )
    delta_artifact = models.OneToOneField(
        Artifact, on_delete=models.PROTECT, related_name="epistemic_delta"
    )
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            self.work_order.campaign_id != self.campaign_id
            or self.workbench_artifact.campaign_id != self.campaign_id
            or self.state_artifact.campaign_id != self.campaign_id
            or self.delta_artifact.campaign_id != self.campaign_id
            or self.workbench_artifact.work_order_id != self.work_order_id
            or self.state_artifact.work_order_id != self.work_order_id
            or self.delta_artifact.work_order_id != self.work_order_id
        ):
            raise ValidationError("research-state transition crosses exact custody")
        if self.parent_id != self.work_order.input_state_id:
            raise ValidationError("research-state parent differs from the work order")
        if (
            self.workbench_artifact.relative_path != "workbench-result.json"
            or self.state_artifact.relative_path != "research-state.json"
            or self.delta_artifact.relative_path != "epistemic-delta.json"
        ):
            raise ValidationError("research-state transition binds the wrong artifacts")
        try:
            state = json.loads(bytes(self.state_artifact.content))
            delta = json.loads(bytes(self.delta_artifact.content))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError(
                "research-state transition binds malformed artifacts"
            ) from exc
        parent_digest = self.parent.state_artifact.digest if self.parent_id else None
        if (
            not isinstance(state, dict)
            or state.get("workbench_result_sha256")
            != self.workbench_artifact.digest
            or state.get("parent_state_sha256") != parent_digest
            or not isinstance(delta, dict)
            or delta.get("parent_state_sha256") != parent_digest
            or delta.get("after_state_sha256") != self.state_artifact.digest
        ):
            raise ValidationError(
                "research-state transition artifacts do not reconcile"
            )
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "campaign": str(self.campaign_id),
                "work_order": str(self.work_order_id),
                "parent": str(self.parent_id) if self.parent_id else None,
                "workbench_artifact": self.workbench_artifact_id,
                "workbench_sha256": self.workbench_artifact.digest,
                "state_artifact": self.state_artifact_id,
                "state_sha256": self.state_artifact.digest,
                "delta_artifact": self.delta_artifact_id,
                "delta_sha256": self.delta_artifact.digest,
            }
        )
        if self.digest != expected:
            raise ValidationError("research-state transition digest is not exact")


class ResearchStateDisposition(AppendOnlyModel):
    class Kind(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        CHALLENGED = "challenged", "Challenge and route back"
        REJECTED = "rejected", "Rejected"

    transition = models.OneToOneField(
        ResearchStateTransition,
        on_delete=models.PROTECT,
        related_name="disposition",
    )
    kind = models.CharField(max_length=16, choices=Kind)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TraceLink(AppendOnlyModel):
    campaign = models.ForeignKey(
        ResearchCampaign, on_delete=models.PROTECT, related_name="trace_links"
    )
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.PROTECT, related_name="trace_links"
    )
    artifact = models.OneToOneField(
        Artifact, on_delete=models.PROTECT, related_name="trace_link"
    )
    trace_id = models.CharField(max_length=64)
    observation_id = models.CharField(max_length=64)
    conversation_id = models.CharField(max_length=160)
    call_id = models.CharField(max_length=160)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            self.work_order.campaign_id != self.campaign_id
            or self.artifact.campaign_id != self.campaign_id
            or self.artifact.work_order_id != self.work_order_id
        ):
            raise ValidationError("trace relation crosses exact campaign custody")
        expected = canonical_digest(
            {
                "campaign": str(self.campaign_id),
                "work_order": str(self.work_order_id),
                "artifact": self.artifact_id,
                "artifact_digest": self.artifact.digest,
                "trace_id": self.trace_id,
                "observation_id": self.observation_id,
                "conversation_id": self.conversation_id,
                "call_id": self.call_id,
            }
        )
        if self.digest != expected:
            raise ValidationError("trace link does not match its exact joined facts")


class ResearchJob(AppendOnlyModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="model_change_jobs",
    )
    company_ref = models.CharField(max_length=240)
    mandate_ref = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ModelChangeEpisode(AppendOnlyModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        ResearchJob, on_delete=models.PROTECT, related_name="model_change_episodes"
    )
    campaign = models.OneToOneField(
        ResearchCampaign,
        on_delete=models.PROTECT,
        related_name="model_change_episode",
    )
    objective = models.TextField()
    named_use = models.TextField()
    cutoff = models.DateField()
    starting_artifact = models.ForeignKey(
        ArtifactVersion,
        on_delete=models.PROTECT,
        related_name="starting_model_change_episodes",
    )
    input_revision = models.PositiveIntegerField(default=1)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            self.job.owner_id != self.campaign.director_id
            or self.starting_artifact.campaign_id != self.campaign_id
            or self.starting_artifact.role
            != ArtifactVersion.Role.STARTING_ARTIFACT
            or self.input_revision != 1
        ):
            raise ValidationError("model-change episode crosses exact job custody")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "job": str(self.job_id),
                "campaign": str(self.campaign_id),
                "objective": self.objective,
                "named_use": self.named_use,
                "cutoff": self.cutoff.isoformat(),
                "starting_artifact": str(self.starting_artifact_id),
                "starting_artifact_sha256": self.starting_artifact.digest,
                "input_revision": self.input_revision,
            }
        )
        if self.digest != expected:
            raise ValidationError("model-change episode digest is not exact")


class ArtifactManifestVersion(AppendOnlyModel):
    class Support(models.TextChoices):
        SUPPORTED = "SUPPORTED", "Supported"
        UNSUPPORTED_PROFILE = "UNSUPPORTED_PROFILE", "Unsupported profile"
        UNSUPPORTED_STRUCTURAL_OPERATION = (
            "UNSUPPORTED_STRUCTURAL_OPERATION",
            "Unsupported structural operation",
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="artifact_manifests",
    )
    artifact = models.ForeignKey(
        ArtifactVersion,
        on_delete=models.PROTECT,
        related_name="model_change_manifests",
    )
    adapter_profile = models.CharField(max_length=120)
    adapter_version = models.CharField(max_length=80)
    target_ref = models.CharField(max_length=160)
    target_address = models.CharField(max_length=160)
    target_value = models.DecimalField(max_digits=30, decimal_places=8)
    target_unit = models.CharField(max_length=40)
    allowed_operation = models.CharField(max_length=80)
    dependency_closure = models.JSONField(default=list, editable=False)
    formula_bindings = models.JSONField(default=dict, editable=False)
    inspection_digest = models.CharField(max_length=64, editable=False)
    support_status = models.CharField(
        max_length=40, choices=Support, default=Support.SUPPORTED
    )
    warnings = models.JSONField(default=list, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            self.artifact_id != self.episode.starting_artifact_id
            or self.artifact.campaign_id != self.episode.campaign_id
            or not isinstance(self.dependency_closure, list)
            or len(self.dependency_closure) != 2
            or len(set(self.dependency_closure)) != 2
            or not isinstance(self.formula_bindings, dict)
            or set(self.formula_bindings) != set(self.dependency_closure)
            or not isinstance(self.warnings, list)
        ):
            raise ValidationError("artifact manifest exceeds the bounded profile")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "episode": str(self.episode_id),
                "artifact": str(self.artifact_id),
                "artifact_sha256": self.artifact.digest,
                "adapter_profile": self.adapter_profile,
                "adapter_version": self.adapter_version,
                "target_ref": self.target_ref,
                "target_address": self.target_address,
                "target_value": canonical_decimal(self.target_value),
                "target_unit": self.target_unit,
                "allowed_operation": self.allowed_operation,
                "dependency_closure": self.dependency_closure,
                "formula_bindings": self.formula_bindings,
                "inspection_digest": self.inspection_digest,
                "support_status": self.support_status,
                "warnings": self.warnings,
            }
        )
        if self.digest != expected:
            raise ValidationError("artifact manifest digest is not exact")


class ConceptualObjectVersion(AppendOnlyModel):
    class BindingStatus(models.TextChoices):
        PROPOSED = "PROPOSED", "Proposed"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROPOSED_STRUCTURE = "PROPOSED_STRUCTURE", "Proposed structure"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="conceptual_objects",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="replacement_objects",
    )
    manifest = models.ForeignKey(
        ArtifactManifestVersion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="conceptual_objects",
    )
    binding_status = models.CharField(max_length=32, choices=BindingStatus)
    economic_meaning = models.JSONField(default=dict, editable=False)
    method_policy = models.JSONField(default=dict, editable=False)
    claim_ceiling = models.TextField()
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if self.parent_id and self.parent.episode_id != self.episode_id:
            raise ValidationError("conceptual object parent crosses episode custody")
        if self.manifest_id and self.manifest.episode_id != self.episode_id:
            raise ValidationError("conceptual object manifest crosses episode custody")
        if (
            self.binding_status == self.BindingStatus.PROPOSED_STRUCTURE
            and self.manifest_id is not None
        ):
            raise ValidationError("proposed structure cannot claim an artifact binding")
        if not isinstance(self.economic_meaning, dict) or not isinstance(
            self.method_policy, dict
        ):
            raise ValidationError("conceptual object bindings are malformed")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "episode": str(self.episode_id),
                "parent": str(self.parent_id) if self.parent_id else None,
                "manifest": str(self.manifest_id) if self.manifest_id else None,
                "manifest_sha256": self.manifest.digest if self.manifest_id else None,
                "binding_status": self.binding_status,
                "economic_meaning": self.economic_meaning,
                "method_policy": self.method_policy,
                "claim_ceiling": self.claim_ceiling,
            }
        )
        if self.digest != expected:
            raise ValidationError("conceptual object digest is not exact")


class ObjectDisposition(AppendOnlyModel):
    class Action(models.TextChoices):
        CONFIRM_MEANING = "CONFIRM_MEANING", "Confirm meaning"
        AMEND_MEANING = "AMEND_MEANING", "Amend meaning"
        AUTHORIZE_METHOD = "AUTHORIZE_METHOD", "Authorise method"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.ForeignKey(
        ConceptualObjectVersion,
        on_delete=models.PROTECT,
        related_name="object_dispositions",
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=32, choices=Action)
    bounded_payload = models.JSONField(default=dict, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if self.actor_id != self.object_version.episode.job.owner_id:
            raise ValidationError("object disposition crosses owner custody")
        if not isinstance(self.bounded_payload, dict):
            raise ValidationError("object disposition payload is malformed")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "object_version": str(self.object_version_id),
                "object_sha256": self.object_version.digest,
                "actor": self.actor_id,
                "action": self.action,
                "bounded_payload": self.bounded_payload,
            }
        )
        if self.digest != expected:
            raise ValidationError("object disposition digest is not exact")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("object_version", "action"),
                name="model_change_object_disposition_once",
            )
        ]


class SourceDocumentVersion(AppendOnlyModel):
    class DocumentClass(models.TextChoices):
        EARNINGS_RELEASE_8K = "EARNINGS_RELEASE_8K", "8-K earnings release"
        FILED_ANNUAL_REPORT_10K = (
            "FILED_ANNUAL_REPORT_10K",
            "Filed annual report",
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="source_documents",
    )
    artifact = models.OneToOneField(
        ArtifactVersion,
        on_delete=models.PROTECT,
        related_name="source_document",
    )
    document_class = models.CharField(max_length=40, choices=DocumentClass)
    identity = models.JSONField(default=dict, editable=False)
    access_context = models.JSONField(default=dict, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            self.artifact.campaign_id != self.episode.campaign_id
            or self.artifact.role != ArtifactVersion.Role.SOURCE
            or self.episode.campaign.director_id != self.episode.job.owner_id
            or self.artifact.campaign.director_id != self.episode.job.owner_id
            or not isinstance(self.identity, dict)
            or not isinstance(self.access_context, dict)
        ):
            raise ValidationError("source document crosses exact capture custody")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "episode": str(self.episode_id),
                "artifact": str(self.artifact_id),
                "artifact_sha256": self.artifact.digest,
                "document_class": self.document_class,
                "identity": self.identity,
                "access_context": self.access_context,
            }
        )
        if self.digest != expected:
            raise ValidationError("source document digest is not exact")


class SourceAssertion(AppendOnlyModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_version = models.ForeignKey(
        SourceDocumentVersion,
        on_delete=models.PROTECT,
        related_name="assertions",
    )
    locator = models.TextField()
    value = models.DecimalField(max_digits=30, decimal_places=8)
    unit = models.CharField(max_length=40)
    dimensions = models.JSONField(default=dict, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        document = self.document_version
        episode = document.episode
        if (
            not self.locator.strip()
            or not isinstance(self.dimensions, dict)
            or document.artifact.role != ArtifactVersion.Role.SOURCE
            or document.artifact.campaign_id != episode.campaign_id
            or episode.campaign.director_id != episode.job.owner_id
            or document.artifact.campaign.director_id != episode.job.owner_id
        ):
            raise ValidationError("source assertion is malformed")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "document_version": str(self.document_version_id),
                "document_sha256": self.document_version.digest,
                "locator": self.locator,
                "value": canonical_decimal(self.value),
                "unit": self.unit,
                "dimensions": self.dimensions,
            }
        )
        if self.digest != expected:
            raise ValidationError("source assertion digest is not exact")


class ModelChangeProposal(AppendOnlyModel):
    class ProposerKind(models.TextChoices):
        MODEL = "MODEL", "Model"
        HOST_DERIVED = "HOST_DERIVED", "Host-derived replacement"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="model_change_proposals",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="replacement_proposals",
    )
    work_order = models.ForeignKey(
        WorkOrder,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="model_change_proposals",
    )
    proposer_kind = models.CharField(max_length=20, choices=ProposerKind)
    conceptual_object = models.ForeignKey(
        ConceptualObjectVersion,
        on_delete=models.PROTECT,
        related_name="model_change_proposals",
    )
    starting_artifact = models.ForeignKey(
        ArtifactVersion,
        on_delete=models.PROTECT,
        related_name="model_change_proposals",
    )
    source_assertion = models.ForeignKey(
        SourceAssertion,
        on_delete=models.PROTECT,
        related_name="model_change_proposals",
    )
    manifest = models.ForeignKey(
        ArtifactManifestVersion,
        on_delete=models.PROTECT,
        related_name="model_change_proposals",
    )
    input_revision = models.PositiveIntegerField()
    operation = models.JSONField(default=dict, editable=False)
    protocol_version = models.CharField(max_length=80)
    claim_ceiling = models.TextField()
    closure_digest = models.CharField(max_length=64, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if self.parent_id and self.parent.episode_id != self.episode_id:
            raise ValidationError("model-change proposal parent crosses episode custody")
        if (
            self.conceptual_object.episode_id != self.episode_id
            or self.starting_artifact_id != self.episode.starting_artifact_id
            or self.source_assertion.document_version.episode_id != self.episode_id
            or self.source_assertion.document_version.artifact.role
            != ArtifactVersion.Role.SOURCE
            or self.source_assertion.document_version.artifact.campaign_id
            != self.episode.campaign_id
            or self.episode.campaign.director_id != self.episode.job.owner_id
            or self.source_assertion.document_version.artifact.campaign.director_id
            != self.episode.job.owner_id
            or self.manifest.episode_id != self.episode_id
            or self.manifest.artifact_id != self.starting_artifact_id
            or self.input_revision != self.episode.input_revision
            or not isinstance(self.operation, dict)
            or self.proposer_kind == self.ProposerKind.MODEL
            and (
                self.work_order_id is None
                or self.work_order.campaign_id != self.episode.campaign_id
                or self.work_order.protocol != "model_change_v0"
            )
        ):
            raise ValidationError("model-change proposal crosses its exact closure")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "episode": str(self.episode_id),
                "parent": str(self.parent_id) if self.parent_id else None,
                "work_order": str(self.work_order_id) if self.work_order_id else None,
                "proposer_kind": self.proposer_kind,
                "conceptual_object": str(self.conceptual_object_id),
                "starting_artifact": str(self.starting_artifact_id),
                "source_assertion": str(self.source_assertion_id),
                "manifest": str(self.manifest_id),
                "input_revision": self.input_revision,
                "operation": self.operation,
                "protocol_version": self.protocol_version,
                "claim_ceiling": self.claim_ceiling,
                "closure_digest": self.closure_digest,
            }
        )
        if self.digest != expected:
            raise ValidationError("model-change proposal digest is not exact")


class AdmissibilityDecision(AppendOnlyModel):
    class Outcome(models.TextChoices):
        PASS = "PASS", "Pass"
        BLOCK = "BLOCK", "Block"
        UNSUPPORTED = "UNSUPPORTED", "Unsupported"
        JUDGMENT_REQUIRED = "JUDGMENT_REQUIRED", "Judgment required"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.OneToOneField(
        ModelChangeProposal,
        on_delete=models.PROTECT,
        related_name="admissibility_decision",
    )
    validator_version = models.CharField(max_length=80)
    outcome = models.CharField(max_length=24, choices=Outcome)
    reason_code = models.CharField(max_length=80)
    closure_digest = models.CharField(max_length=64, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if self.closure_digest != self.proposal.closure_digest:
            raise ValidationError("admissibility decision crosses proposal closure")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "proposal": str(self.proposal_id),
                "proposal_sha256": self.proposal.digest,
                "validator_version": self.validator_version,
                "outcome": self.outcome,
                "reason_code": self.reason_code,
                "closure_digest": self.closure_digest,
            }
        )
        if self.digest != expected:
            raise ValidationError("admissibility decision digest is not exact")


class CalculationReceipt(AppendOnlyModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="calculation_receipts",
    )
    candidate = models.OneToOneField(
        ArtifactVersion,
        on_delete=models.PROTECT,
        related_name="calculation_receipt",
    )
    pass_decision = models.OneToOneField(
        AdmissibilityDecision,
        on_delete=models.PROTECT,
        related_name="calculation_receipt",
    )
    manifest = models.ForeignKey(
        ArtifactManifestVersion,
        on_delete=models.PROTECT,
        related_name="calculation_receipts",
    )
    adapter_version = models.CharField(max_length=80)
    adapter_profile = models.CharField(max_length=120)
    engine_identity = models.CharField(max_length=240)
    engine_version = models.CharField(max_length=240)
    timeout_seconds = models.PositiveIntegerField()
    environment = models.JSONField(default=dict, editable=False)
    operation_receipt = models.JSONField(default=dict, editable=False)
    input_digest = models.CharField(max_length=64, editable=False)
    output_digest = models.CharField(max_length=64, editable=False)
    consequences = models.JSONField(default=list, editable=False)
    warnings = models.JSONField(default=list, editable=False)
    formula_errors = models.JSONField(default=list, editable=False)
    closure_digest = models.CharField(max_length=64, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        proposal = self.pass_decision.proposal
        if (
            self.pass_decision.outcome != AdmissibilityDecision.Outcome.PASS
            or self.candidate.candidate_from_pass_id != self.pass_decision_id
            or self.candidate.parent_id != self.episode.starting_artifact_id
            or self.candidate.campaign_id != self.episode.campaign_id
            or proposal.episode_id != self.episode_id
            or self.manifest_id != proposal.manifest_id
            or self.input_digest != self.episode.starting_artifact.digest
            or self.output_digest != self.candidate.digest
            or self.closure_digest != proposal.closure_digest
            or not isinstance(self.consequences, list)
            or len(self.consequences) != 2
            or not isinstance(self.warnings, list)
            or not isinstance(self.formula_errors, list)
        ):
            raise ValidationError("calculation receipt crosses exact candidate custody")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "episode": str(self.episode_id),
                "candidate": str(self.candidate_id),
                "candidate_sha256": self.candidate.digest,
                "pass_decision": str(self.pass_decision_id),
                "manifest": str(self.manifest_id),
                "adapter_version": self.adapter_version,
                "adapter_profile": self.adapter_profile,
                "engine_identity": self.engine_identity,
                "engine_version": self.engine_version,
                "timeout_seconds": self.timeout_seconds,
                "environment": self.environment,
                "operation_receipt": self.operation_receipt,
                "input_digest": self.input_digest,
                "output_digest": self.output_digest,
                "consequences": self.consequences,
                "warnings": self.warnings,
                "formula_errors": self.formula_errors,
                "closure_digest": self.closure_digest,
            }
        )
        if self.digest != expected:
            raise ValidationError("calculation receipt digest is not exact")


class Amendment(AppendOnlyModel):
    class Action(models.TextChoices):
        USE_FILED_ANNUAL_REPORT = (
            "USE_FILED_ANNUAL_REPORT",
            "Use filed annual report",
        )
        AMEND_MEANING = "AMEND_MEANING", "Amend meaning"
        AMEND_METHOD_POLICY = "AMEND_METHOD_POLICY", "Amend method policy"
        AMEND_ASSUMPTION = "AMEND_ASSUMPTION", "Amend assumption"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="amendments",
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    object_version = models.ForeignKey(
        ConceptualObjectVersion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="amendments",
    )
    blocked_decision = models.ForeignKey(
        AdmissibilityDecision,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="amendments",
    )
    action = models.CharField(max_length=40, choices=Action)
    bounded_change = models.JSONField(default=dict, editable=False)
    rationale = models.TextField()
    replacement_object = models.ForeignKey(
        ConceptualObjectVersion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="replacement_amendments",
    )
    replacement_proposal = models.ForeignKey(
        ModelChangeProposal,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="replacement_amendments",
    )
    repair_key = models.CharField(
        max_length=64, null=True, blank=True, unique=True, editable=False
    )
    adapter_profile = models.CharField(max_length=120, blank=True)
    idempotency_key = models.CharField(max_length=120, blank=True)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        object_path = bool(self.object_version_id and self.replacement_object_id)
        proposal_path = bool(
            self.blocked_decision_id and self.replacement_proposal_id
        )
        if (
            object_path == proposal_path
            or self.actor_id != self.episode.job.owner_id
            or self.object_version_id
            and (
                self.object_version.episode_id != self.episode_id
                or self.replacement_object.episode_id != self.episode_id
            )
            or self.blocked_decision_id
            and (
                self.blocked_decision.proposal.episode_id != self.episode_id
                or self.replacement_proposal.episode_id != self.episode_id
            )
            or not isinstance(self.bounded_change, dict)
        ):
            raise ValidationError("amendment crosses exact episode custody")
        identity = {
            "id": str(self.pk),
            "episode": str(self.episode_id),
            "actor": self.actor_id,
            "object_version": str(self.object_version_id) if self.object_version_id else None,
            "blocked_decision": str(self.blocked_decision_id) if self.blocked_decision_id else None,
            "action": self.action,
            "bounded_change": self.bounded_change,
            "rationale": self.rationale,
            "replacement_object": str(self.replacement_object_id) if self.replacement_object_id else None,
            "replacement_proposal": str(self.replacement_proposal_id) if self.replacement_proposal_id else None,
        }
        if self.repair_key:
            identity.update(
                {
                    "repair_key": self.repair_key,
                    "adapter_profile": self.adapter_profile,
                    "idempotency_key": self.idempotency_key,
                }
            )
        expected = canonical_digest(identity)
        if self.digest != expected:
            raise ValidationError("amendment digest is not exact")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("blocked_decision",),
                condition=models.Q(
                    blocked_decision__isnull=False,
                    action="USE_FILED_ANNUAL_REPORT",
                ),
                name="model_change_one_filed_repair_per_block",
            )
        ]


class InvalidationEvent(AppendOnlyModel):
    class DescendantType(models.TextChoices):
        OBJECT = "OBJECT", "Conceptual object"
        PROPOSAL = "PROPOSAL", "Proposal"
        DECISION = "DECISION", "Decision"
        CANDIDATE = "CANDIDATE", "Candidate"
        CALCULATION = "CALCULATION", "Calculation receipt"
        DISPOSITION = "DISPOSITION", "Artifact disposition"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amendment = models.ForeignKey(
        Amendment,
        on_delete=models.PROTECT,
        related_name="invalidation_events",
    )
    descendant_type = models.CharField(max_length=24, choices=DescendantType)
    descendant_id = models.UUIDField()
    descendant_digest = models.CharField(max_length=64)
    reason = models.CharField(max_length=120)
    closure_digest = models.CharField(max_length=64)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "amendment": str(self.amendment_id),
                "descendant_type": self.descendant_type,
                "descendant_id": str(self.descendant_id),
                "descendant_digest": self.descendant_digest,
                "reason": self.reason,
                "closure_digest": self.closure_digest,
            }
        )
        if self.digest != expected:
            raise ValidationError("invalidation event digest is not exact")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("amendment", "descendant_type", "descendant_id"),
                name="model_change_invalidation_once",
            )
        ]


class ArtifactDisposition(AppendOnlyModel):
    class Kind(models.TextChoices):
        SIMULATE_NAMED_USE = "SIMULATE_NAMED_USE", "Simulate named use"
        REJECT = "REJECT", "Reject"
        REWORK = "REWORK", "Request rework"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="artifact_dispositions",
    )
    candidate = models.ForeignKey(
        ArtifactVersion,
        on_delete=models.PROTECT,
        related_name="model_change_dispositions",
    )
    calculation_receipt = models.ForeignKey(
        CalculationReceipt,
        on_delete=models.PROTECT,
        related_name="artifact_dispositions",
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    named_use = models.TextField()
    kind = models.CharField(max_length=24, choices=Kind)
    rationale = models.TextField(blank=True)
    closure_digest = models.CharField(max_length=64)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            self.actor_id != self.episode.job.owner_id
            or self.candidate.campaign_id != self.episode.campaign_id
            or self.calculation_receipt.candidate_id != self.candidate_id
            or self.calculation_receipt.episode_id != self.episode_id
            or self.named_use != self.episode.named_use
            or self.closure_digest != self.calculation_receipt.closure_digest
            or self.calculation_receipt.formula_errors
        ):
            raise ValidationError("artifact disposition crosses exact candidate scope")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "episode": str(self.episode_id),
                "candidate": str(self.candidate_id),
                "calculation_receipt": str(self.calculation_receipt_id),
                "actor": self.actor_id,
                "named_use": self.named_use,
                "kind": self.kind,
                "rationale": self.rationale,
                "closure_digest": self.closure_digest,
            }
        )
        if self.digest != expected:
            raise ValidationError("artifact disposition digest is not exact")


class CorrectionRecord(AppendOnlyModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="correction_records",
    )
    blocked_decision = models.ForeignKey(
        AdmissibilityDecision,
        on_delete=models.PROTECT,
        related_name="correction_records",
    )
    amendment = models.OneToOneField(
        Amendment,
        on_delete=models.PROTECT,
        related_name="correction_record",
    )
    replacement_proposal = models.ForeignKey(
        ModelChangeProposal,
        on_delete=models.PROTECT,
        related_name="correction_records",
    )
    source_assertions = models.JSONField(default=list, editable=False)
    candidate = models.ForeignKey(
        ArtifactVersion,
        on_delete=models.PROTECT,
        related_name="correction_records",
    )
    protocol_version = models.CharField(max_length=80)
    adapter_profile_version = models.CharField(max_length=160)
    reason_code = models.CharField(max_length=80)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if (
            self.blocked_decision.proposal.episode_id != self.episode_id
            or self.amendment.episode_id != self.episode_id
            or self.replacement_proposal.episode_id != self.episode_id
            or self.amendment.replacement_proposal_id != self.replacement_proposal_id
            or self.candidate.campaign_id != self.episode.campaign_id
            or self.candidate.candidate_from_pass.proposal_id
            != self.replacement_proposal_id
            or self.reason_code != self.blocked_decision.reason_code
            or not isinstance(self.source_assertions, list)
            or len(self.source_assertions) != 2
        ):
            raise ValidationError("correction record crosses exact correction custody")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "episode": str(self.episode_id),
                "blocked_decision": str(self.blocked_decision_id),
                "amendment": str(self.amendment_id),
                "replacement_proposal": str(self.replacement_proposal_id),
                "source_assertions": self.source_assertions,
                "candidate": str(self.candidate_id),
                "protocol_version": self.protocol_version,
                "adapter_profile_version": self.adapter_profile_version,
                "reason_code": self.reason_code,
            }
        )
        if self.digest != expected:
            raise ValidationError("correction record digest is not exact")


class ModelChangeOutcome(AppendOnlyModel):
    class Stage(models.TextChoices):
        RUNTIME_FAILURE = "RUNTIME_FAILURE", "Runtime failure"
        WORKER_REFUSAL = "WORKER_REFUSAL", "Worker refusal"
        CALCULATION_FAILURE = "CALCULATION_FAILURE", "Calculation failure"

    class NextAction(models.TextChoices):
        RETRY_WORK = "RETRY_WORK", "Retry this work"
        RETRY_CANDIDATE = "RETRY_CANDIDATE", "Retry creating the candidate"
        NONE = "NONE", "No next action"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(
        ModelChangeEpisode,
        on_delete=models.PROTECT,
        related_name="model_change_outcomes",
    )
    work_order = models.ForeignKey(
        WorkOrder,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="model_change_outcomes",
    )
    blocked_decision = models.ForeignKey(
        AdmissibilityDecision,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="model_change_outcomes",
    )
    stage = models.CharField(max_length=32, choices=Stage)
    reason_code = models.CharField(max_length=80)
    public_message = models.TextField()
    next_action = models.CharField(max_length=24, choices=NextAction)
    closure_digest = models.CharField(max_length=64)
    attempt_key = models.CharField(max_length=64)
    protocol_version = models.CharField(max_length=80)
    technical_details = models.JSONField(default=dict, editable=False)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        runtime_path = self.stage in {
            self.Stage.RUNTIME_FAILURE,
            self.Stage.WORKER_REFUSAL,
        }
        calculation_path = self.stage == self.Stage.CALCULATION_FAILURE
        if (
            runtime_path != bool(self.work_order_id)
            or calculation_path != bool(self.blocked_decision_id)
            or self.work_order_id
            and (
                self.work_order.campaign_id != self.episode.campaign_id
                or self.work_order.protocol != "model_change_v0"
            )
            or self.blocked_decision_id
            and self.blocked_decision.proposal.episode_id != self.episode_id
            or not self.public_message.strip()
            or not isinstance(self.technical_details, dict)
        ):
            raise ValidationError("model-change outcome crosses exact custody")
        expected = canonical_digest(
            {
                "id": str(self.pk),
                "episode": str(self.episode_id),
                "work_order": str(self.work_order_id) if self.work_order_id else None,
                "blocked_decision": (
                    str(self.blocked_decision_id)
                    if self.blocked_decision_id
                    else None
                ),
                "stage": self.stage,
                "reason_code": self.reason_code,
                "public_message": self.public_message,
                "next_action": self.next_action,
                "closure_digest": self.closure_digest,
                "attempt_key": self.attempt_key,
                "protocol_version": self.protocol_version,
                "technical_details": self.technical_details,
            }
        )
        if self.digest != expected:
            raise ValidationError("model-change outcome digest is not exact")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("stage", "attempt_key"),
                name="model_change_outcome_attempt_once",
            )
        ]
