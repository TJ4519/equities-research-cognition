from __future__ import annotations

from hashlib import sha256
import json
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def canonical_digest(value: object) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        ResearchCampaign, on_delete=models.PROTECT, related_name="input_artifacts"
    )
    role = models.CharField(max_length=32, choices=Role)
    filename = models.CharField(max_length=240)
    media_type = models.CharField(max_length=120)
    content = models.BinaryField()
    digest = models.CharField(max_length=64, editable=False)
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
