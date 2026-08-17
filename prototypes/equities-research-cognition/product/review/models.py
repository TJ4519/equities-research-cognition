from __future__ import annotations
from hashlib import sha256
import json
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
def digest(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
_ADMISSION_TOKEN = object()
CONSEQUENCE_ACTIONS = {
    "current": {"apply_current_correction": ("current_report_state", "current"),
                "reject_current_correction": ("review_record", None),
                "defer_current_correction": ("current_deferred_queue", None),
                "absent_current_correction": ("no_target", None)},
    "rubric": {"create_rubric_precedent": ("rubric_precedent_pool", "rubric"),
               "create_eval_candidate": ("protected_eval_candidate_pool", "eval"),
               "reject_rubric_or_eval": ("review_record", None),
               "defer_rubric_or_eval": ("rubric_eval_deferred_queue", None),
               "absent_rubric_or_eval": ("no_target", None)},
    "future": {"propose_prompt_change": ("future_proposal_quarantine", "prompt"),
               "propose_retrieval_change": ("future_proposal_quarantine", "retrieval"),
               "propose_workflow_change": ("future_proposal_quarantine", "workflow"),
               "reject_future_change": ("review_record", None),
               "defer_future_change": ("future_deferred_queue", None),
               "absent_future_change": ("no_target", None)},
}
LEGAL_CONSEQUENCE_CONDITION = models.Q()
for _family, _actions in CONSEQUENCE_ACTIONS.items():
    for _action, (_target, _effect) in _actions.items():
        LEGAL_CONSEQUENCE_CONDITION |= models.Q(family=_family, action=_action, target=_target)
class AnalystEnrollment(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    scope_code = models.CharField(max_length=64)
    qualification_basis = models.TextField()
    attested_by = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
class ImmutableQuerySet(models.QuerySet):
    def reject_mutation(self, *args: object, **kwargs: object) -> None:
        raise ValidationError("locked records cannot be mutated")
    update = delete = bulk_create = bulk_update = reject_mutation
class ResearchCase(models.Model):
    class SubjectMode(models.TextChoices):
        LEGACY_FIXTURE_IMPORT = "legacy_fixture_import", "Legacy fixture — engineering only"
        CONTRACT_FIXTURE = "contract_fixture", "Contract fixture — engineering only"
        NATIVE_OBSERVED_RUN = "native_observed_run", "Native-observed NTM/Codex RIE run"
        LANGFUSE_OBSERVED_RUN = "langfuse_observed_run", "Langfuse-observed NTM/Codex RIE run"
    external_id = models.CharField(max_length=255, unique=True)
    subject_mode = models.CharField(max_length=32, choices=SubjectMode)
    question = models.TextField()
    source_identity = models.TextField()
    source_url = models.URLField()
    source_locator = models.TextField()
    exact_passage = models.TextField()
    context_items = models.JSONField()
    rubric = models.JSONField()
    custody_tree_digest = models.CharField(max_length=64)
    source_artifact_digest = models.CharField(max_length=64)
    evidence_artifact_digest = models.CharField(max_length=64)
    projection_version = models.CharField(max_length=64)
    artifact_seal = models.ForeignKey("ArtifactSeal", null=True, blank=True,
                                      on_delete=models.PROTECT, related_name="cases")
    population_admission = models.ForeignKey("PopulationAdmission", null=True, blank=True,
                                             on_delete=models.PROTECT, related_name="cases")
    packet_digest = models.CharField(max_length=64, editable=False)
    rubric_digest = models.CharField(max_length=64, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = ImmutableQuerySet.as_manager()
    def packet_body(self) -> dict[str, object]:
        return {
            "question": self.question, "source_identity": self.source_identity,
            "source_url": self.source_url, "source_locator": self.source_locator,
            "exact_passage": self.exact_passage, "context_items": self.context_items,
            "rubric_digest": digest(self.rubric), "subject_mode": self.subject_mode,
            "custody_tree_digest": self.custody_tree_digest,
            "source_artifact_digest": self.source_artifact_digest,
            "evidence_artifact_digest": self.evidence_artifact_digest,
            "projection_version": self.projection_version}
    def save(self, *args: object, **kwargs: object) -> None:
        admission_token = kwargs.pop("_admission_token", None)
        if self.pk:
            raise ValidationError("research packet is append-only")
        if (self.subject_mode != self.SubjectMode.LEGACY_FIXTURE_IMPORT
                and admission_token is not _ADMISSION_TOKEN):
            raise ValidationError("observed populations require the canonical atomic admission service")
        self.rubric_digest = digest(self.rubric)
        self.packet_digest = digest(self.packet_body())
        super().save(*args, **kwargs)
    def delete(self, *args: object, **kwargs: object) -> None:
        raise ValidationError("research packet is append-only")
    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(subject_mode="legacy_fixture_import",
                             artifact_seal__isnull=True, population_admission__isnull=True)
                    | models.Q(subject_mode__in=(
                        "contract_fixture", "native_observed_run", "langfuse_observed_run"),
                        artifact_seal__isnull=False, population_admission__isnull=False)
                ), name="research_case_admission_mode",
            )
        ]
class AppendOnlyModel(models.Model):
    objects = ImmutableQuerySet.as_manager()
    admission_guard = False
    class Meta:
        abstract = True
    def save(self, *args: object, **kwargs: object) -> None:
        admission_token = kwargs.pop("_admission_token", None)
        if self.pk:
            raise ValidationError(f"{self._meta.verbose_name} is append-only")
        if self.admission_guard and admission_token is not _ADMISSION_TOKEN:
            raise ValidationError(f"{self._meta.verbose_name} requires canonical atomic admission")
        self.full_clean()
        super().save(*args, **kwargs)
    def delete(self, *args: object, **kwargs: object) -> None:
        raise ValidationError(f"{self._meta.verbose_name} is append-only")
class QueueAssignment(AppendOnlyModel):
    admission_guard = False
    enrollment = models.ForeignKey(AnalystEnrollment, on_delete=models.PROTECT)
    case = models.ForeignKey(ResearchCase, on_delete=models.PROTECT)
    population_admission = models.ForeignKey("PopulationAdmission", null=True, blank=True,
                                             on_delete=models.PROTECT, related_name="assignments")
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"
        constraints = [models.UniqueConstraint(fields=("enrollment", "case"), name="one_case_per_enrollment")]
    def save(self, *args: object, **kwargs: object) -> None:
        admission_token = kwargs.get("_admission_token")
        if (self.case.subject_mode != ResearchCase.SubjectMode.LEGACY_FIXTURE_IMPORT
                and admission_token is not _ADMISSION_TOKEN):
            raise ValidationError("observed queues require the canonical atomic admission service")
        super().save(*args, **kwargs)
class LineageRecord(AppendOnlyModel):
    class Kind(models.TextChoices):
        ROLE = "role", "Agent role"
        PROMPT = "prompt", "Prompt"
        SKILL = "skill", "Skill"
        TOOL = "tool", "Tool trace"
        SOURCE = "source", "Source use"
        ARTIFACT = "artifact", "Artifact evolution"
        CLAIM = "claim_transition", "Claim transition"
        SYNTHESIS = "synthesis", "Synthesis use"
        JUDGMENT = "machine_judgment", "Machine judgment"
        RUNTIME = "runtime", "Exact runtime correlation"
    class Availability(models.TextChoices):
        EXACT = "exact", "Exact captured record"
        MISSING = "missing", "Missing"
        REDACTED = "redacted", "Redacted"
        DIGEST_ONLY = "digest_only", "Digest only"
    case = models.ForeignKey(ResearchCase, on_delete=models.PROTECT, related_name="lineage_records")
    sequence = models.PositiveIntegerField()
    kind = models.CharField(max_length=32, choices=Kind)
    label = models.CharField(max_length=255)
    availability = models.CharField(max_length=16, choices=Availability)
    locator = models.TextField()
    content = models.TextField(blank=True)
    content_digest = models.CharField(max_length=64, blank=True)
    artifact_id = models.CharField(max_length=255, blank=True, default="", editable=False)
    trace_id = models.CharField(max_length=64, blank=True, default="", editable=False)
    span_id = models.CharField(max_length=64, blank=True, default="", editable=False)
    producer = models.TextField(blank=True, default="", editable=False)
    relations = models.JSONField(default=list, editable=False)
    class Meta:
        ordering = ("sequence",)
        constraints = [models.UniqueConstraint(fields=("case", "sequence"), name="lineage_sequence_per_case")]
    def save(self, *args: object, **kwargs: object) -> None:
        token = kwargs.get("_admission_token")
        if (self.case.subject_mode != ResearchCase.SubjectMode.LEGACY_FIXTURE_IMPORT
                and token is not _ADMISSION_TOKEN):
            raise ValidationError("admitted lineage requires the canonical atomic admission service")
        super().save(*args, **kwargs)
    def clean(self) -> None:
        if self.availability == self.Availability.EXACT:
            valid_digest = (len(self.content_digest) == 64
                and all(character in "0123456789abcdef" for character in self.content_digest))
            if (not valid_digest or (self.content
                    and self.content_digest != sha256(self.content.encode()).hexdigest())
                    or (not self.content and self.case_id
                        and self.case.subject_mode == ResearchCase.SubjectMode.LEGACY_FIXTURE_IMPORT)):
                raise ValidationError("exact records require canonical or inline content matching their SHA-256 digest")
        if (self.availability == self.Availability.DIGEST_ONLY and (
                self.content or len(self.content_digest) != 64
                or any(character not in "0123456789abcdef" for character in self.content_digest))):
            raise ValidationError("digest-only records require one lowercase SHA-256 digest and no content")
        if self.availability in (self.Availability.MISSING, self.Availability.REDACTED) and (self.content or self.content_digest):
            raise ValidationError("missing and redacted records cannot imply captured content or digest")
        if self.availability != self.Availability.EXACT and self.content:
            raise ValidationError("unavailable records cannot imply captured content")
        if self.case_id and self.case.subject_mode != ResearchCase.SubjectMode.LEGACY_FIXTURE_IMPORT:
            if (self.availability != self.Availability.EXACT or not self.artifact_id
                    or not self.producer or not isinstance(self.relations, list)):
                raise ValidationError("admitted lineage requires exact captured provenance")
            if self.kind == self.Kind.RUNTIME and not all((self.trace_id, self.span_id)):
                raise ValidationError("runtime lineage requires exact trace and span identity")
class FirstPass(AppendOnlyModel):
    class Decision(models.TextChoices):
        LICENSED = "licensed", "Licensed"
        NARROW = "requires_narrowing", "Requires narrowing"
        REJECT = "reject", "Reject"
        AMBIGUOUS = "ambiguous", "Ambiguous"
    assignment = models.OneToOneField(QueueAssignment, on_delete=models.PROTECT, related_name="first_pass")
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    session_fingerprint = models.CharField(max_length=64)
    reviewer_scope_snapshot = models.JSONField()
    packet_digest_snapshot = models.CharField(max_length=64)
    rubric_digest_snapshot = models.CharField(max_length=64)
    subject_mode_snapshot = models.CharField(max_length=32)
    packet_snapshot = models.JSONField(default=dict, editable=False)
    decision = models.CharField(max_length=32, choices=Decision)
    rationale = models.TextField()
    locked_at = models.DateTimeField(auto_now_add=True)
class ExposureEvent(AppendOnlyModel):
    first_pass = models.OneToOneField(FirstPass, on_delete=models.PROTECT, related_name="exposure")
    lineage_digest = models.CharField(max_length=64)
    lineage_snapshot = models.JSONField(default=list, editable=False)
    exposed_at = models.DateTimeField(auto_now_add=True)
class ReviewCompletion(AppendOnlyModel):
    first_pass = models.OneToOneField(FirstPass, on_delete=models.PROTECT, related_name="completion")
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    session_fingerprint = models.CharField(max_length=64)
    adjudicated_decision = models.CharField(max_length=32, choices=FirstPass.Decision)
    diagnosis = models.TextField()
    corrected_judgment = models.TextField()
    completed_at = models.DateTimeField(auto_now_add=True)
class ConsequenceDecision(AppendOnlyModel):
    completion = models.ForeignKey(ReviewCompletion, on_delete=models.PROTECT, related_name="decisions")
    family = models.CharField(max_length=32)
    action = models.CharField(max_length=48)
    target = models.CharField(max_length=48)
    rationale = models.TextField()
    payload = models.TextField(blank=True)
    class Meta:
        ordering = ("family",)
        constraints = [
            models.UniqueConstraint(fields=("completion", "family"), name="one_decision_per_consequence_family"),
            models.CheckConstraint(condition=LEGAL_CONSEQUENCE_CONDITION,
                                   name="legal_consequence_action_target"),
        ]
class CurrentCorrection(AppendOnlyModel):
    completion = models.OneToOneField(ReviewCompletion, on_delete=models.PROTECT, related_name="current_correction")
    corrected_state = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
class RubricEvalState(AppendOnlyModel):
    completion = models.OneToOneField(ReviewCompletion, on_delete=models.PROTECT, related_name="rubric_eval_state")
    state_type = models.CharField(max_length=32)
    proposed_state = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(state_type__in=("rubric", "eval")), name="legal_rubric_eval_state_type")]
class FutureProposal(AppendOnlyModel):
    completion = models.OneToOneField(ReviewCompletion, on_delete=models.PROTECT, related_name="future_proposal")
    intervention_type = models.CharField(max_length=24)
    proposed_change = models.TextField()
    reversibility_plan = models.TextField()
    status = models.CharField(max_length=32, default="inactive_quarantined", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(intervention_type__in=("prompt", "retrieval", "workflow")), name="legal_future_intervention_type"),
            models.CheckConstraint(condition=models.Q(status="inactive_quarantined"), name="future_proposal_never_activates_itself")]
class RunRegistration(AppendOnlyModel):
    run_id = models.UUIDField(unique=True, editable=False)
    artifact_root = models.TextField(unique=True, editable=False)
    commissioned_question = models.TextField(editable=False)
    review_scope_code = models.CharField(max_length=64, editable=False)
    expected_unit_ids = models.JSONField(editable=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"
class ArtifactSeal(AppendOnlyModel):
    registration = models.OneToOneField(RunRegistration, on_delete=models.PROTECT,
                                        related_name="seal")
    manifest = models.JSONField(editable=False)
    manifest_digest = models.CharField(max_length=64, unique=True, editable=False)
    sealed_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"
    def clean(self) -> None:
        try:
            from .intake import IntakeRejected, validate_sealed_manifest
            validate_sealed_manifest(self.manifest, self.registration, self.manifest_digest)
        except (IntakeRejected, KeyError, TypeError, ValueError) as exc:
            raise ValidationError(str(exc)) from exc
class PopulationAdmission(AppendOnlyModel):
    admission_guard = True
    artifact_seal = models.OneToOneField(ArtifactSeal, on_delete=models.PROTECT,
                                         related_name="population_admission")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="population_admission_requests",
    )
    idempotency_key = models.CharField(max_length=64, unique=True)
    request_digest = models.CharField(max_length=64, editable=False)
    evidence_mode = models.CharField(max_length=32, choices=(
        ("contract_fixture", "Contract fixture — engineering only"), ("native_observed_run", "Native-observed NTM/Codex RIE run"),
        ("langfuse_observed_run", "Langfuse-observed NTM/Codex RIE run")))
    runtime_receipt = models.JSONField(editable=False)
    runtime_digest = models.CharField(max_length=64, editable=False)
    admitted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"
    def clean(self) -> None:
        if (not self.requested_by_id
                or self.runtime_digest != digest(self.runtime_receipt)
                or self.evidence_mode != self.runtime_receipt.get("evidence_mode")):
            raise ValidationError("admission runtime receipt or evidence mode is inconsistent")
class JudgmentUnit(AppendOnlyModel):
    admission_guard = True
    population_admission = models.ForeignKey(
        PopulationAdmission, on_delete=models.PROTECT, related_name="judgment_units")
    case = models.OneToOneField(ResearchCase, on_delete=models.PROTECT,
                                related_name="judgment_unit")
    unit_id = models.CharField(max_length=255)
    provisional = models.JSONField(editable=False)
    comparison = models.JSONField(editable=False)
    transition = models.JSONField(editable=False)
    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"
        constraints = [models.UniqueConstraint(fields=("population_admission", "unit_id"),
                                               name="one_judgment_unit_per_admission")]
