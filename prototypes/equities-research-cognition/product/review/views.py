from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from hashlib import sha256
import json

from .models import AnalystEnrollment, FirstPass, QueueAssignment, ReviewCompletion
from .transitions import CompletionRejected, LockRejected, complete_review, lock_first_pass


def enrollment_for(request: HttpRequest) -> AnalystEnrollment:
    try:
        return AnalystEnrollment.objects.get(user=request.user, is_active=True)
    except AnalystEnrollment.DoesNotExist as exc:
        raise PermissionDenied("No active analyst enrollment for this session") from exc


def assigned_case(request: HttpRequest, case_id: int) -> tuple[AnalystEnrollment, QueueAssignment]:
    enrollment = enrollment_for(request)
    assignment = get_object_or_404(
        QueueAssignment.objects.select_related("case"),
        enrollment=enrollment, case_id=case_id, is_active=True,
        case__subject_mode__in=("legacy_fixture_import", "contract_fixture", "langfuse_observed_run"),
    )
    return enrollment, assignment


@login_required
def queue(request: HttpRequest) -> HttpResponse:
    enrollment = enrollment_for(request)
    assignments = QueueAssignment.objects.filter(
        enrollment=enrollment, is_active=True,
        case__subject_mode__in=("legacy_fixture_import", "contract_fixture", "langfuse_observed_run"),
    ).select_related("case", "first_pass__completion")
    return render(request, "review/queue.html", {"assignments": assignments, "enrollment": enrollment})


@login_required
def case(request: HttpRequest, case_id: int) -> HttpResponse:
    _enrollment, assignment = assigned_case(request, case_id)
    if FirstPass.objects.filter(assignment=assignment).exists():
        return redirect("reveal", case_id=case_id)
    return render(request, "review/case.html", {"case": assignment.case, "decision_choices": FirstPass.Decision.choices})


@login_required
def lock(request: HttpRequest, case_id: int) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseNotFound()
    _enrollment, assignment = assigned_case(request, case_id)
    if not request.session.session_key:
        request.session.create()
    try:
        lock_first_pass(
            assignment_id=assignment.pk,
            user=request.user,
            session_key=request.session.session_key,
            packet_digest=request.POST.get("packet_digest", ""),
            rubric_digest=request.POST.get("rubric_digest", ""),
            decision=request.POST.get("decision", ""),
            rationale=request.POST.get("rationale", ""),
        )
    except LockRejected as exc:
        return HttpResponse(str(exc), status=409)
    return redirect("reveal", case_id=case_id)


@login_required
def reveal(request: HttpRequest, case_id: int) -> HttpResponse:
    enrollment, assignment = assigned_case(request, case_id)
    first_pass = get_object_or_404(
        FirstPass.objects.select_related("exposure"),
        assignment=assignment,
        author_user=request.user,
        reviewer_scope_snapshot__enrollment_id=enrollment.pk,
    )
    if ReviewCompletion.objects.filter(first_pass=first_pass).exists():
        return redirect("completed", case_id=case_id)
    return render(request, "review/reveal.html", {
        "packet": first_pass.packet_snapshot,
        "current_subject_mode": assignment.case.subject_mode,
        "first_pass": first_pass,
        "records": first_pass.exposure.lineage_snapshot,
    })


@login_required
def record(request: HttpRequest, case_id: int, sequence: int) -> HttpResponse:
    enrollment, assignment = assigned_case(request, case_id)
    first_pass = get_object_or_404(
        FirstPass, assignment=assignment, author_user=request.user,
        reviewer_scope_snapshot__enrollment_id=enrollment.pk,
    )
    snapshot = next(
        (item for item in first_pass.exposure.lineage_snapshot
         if item["sequence"] == sequence and item["availability"] == "exact"), None,
    )
    lineage = get_object_or_404(assignment.case.lineage_records, sequence=sequence)
    if not snapshot or snapshot["content_digest"] != lineage.content_digest:
        return HttpResponse("Locked lineage record is unavailable", status=409)
    content = lineage.content
    try:
        if not content and lineage.artifact_id.startswith("runtime:"):
            role = lineage.artifact_id.removeprefix("runtime:")
            binding = next(item for item in assignment.case.population_admission.runtime_receipt["roles"]
                           if item["role_id"] == role)
            value = binding["receipt"] if assignment.case.subject_mode == "contract_fixture" else {
                "receipt": binding["receipt"], "thread_record": binding["thread_record"],
            }
            content = json.dumps(value, sort_keys=True, separators=(",", ":"))
        elif not content:
            artifact = next(item for item in assignment.case.artifact_seal.manifest["artifacts"]
                            if item["artifact_id"] == lineage.artifact_id)
            content = artifact["content"]
    except (KeyError, StopIteration, TypeError):
        return HttpResponse("Locked lineage content is unavailable", status=409)
    if sha256(content.encode()).hexdigest() != lineage.content_digest:
        return HttpResponse("Locked lineage content failed its digest", status=409)
    return render(request, "review/record.html", {"record": lineage, "content": content})


@login_required
def complete(request: HttpRequest, case_id: int) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseNotFound()
    assigned_case(request, case_id)
    if not request.session.session_key:
        request.session.create()
    keys = (
        "first_pass_id", "packet_digest", "lineage_digest", "adjudicated_decision",
        "diagnosis", "corrected_judgment", "current_action", "current_payload",
        "current_rationale", "rubric_action", "rubric_payload", "rubric_rationale",
        "future_action", "future_payload", "future_reversibility", "future_rationale",
    )
    try:
        complete_review(
            user=request.user,
            session_key=request.session.session_key,
            case_id=case_id,
            data={key: request.POST.get(key, "") for key in keys},
        )
    except CompletionRejected as exc:
        return HttpResponse(str(exc), status=409)
    return redirect("completed", case_id=case_id)


@login_required
def completed(request: HttpRequest, case_id: int) -> HttpResponse:
    enrollment, assignment = assigned_case(request, case_id)
    first_pass = get_object_or_404(
        FirstPass,
        assignment=assignment,
        author_user=request.user,
        reviewer_scope_snapshot__enrollment_id=enrollment.pk,
    )
    completion = get_object_or_404(
        ReviewCompletion.objects.prefetch_related("decisions"), first_pass=first_pass, author_user=request.user
    )
    return render(request, "review/completed.html", {
        "packet": first_pass.packet_snapshot,
        "current_subject_mode": assignment.case.subject_mode,
        "first_pass": first_pass,
        "completion": completion,
        "decisions": [completion.decisions.get(family=family) for family in ("current", "rubric", "future")],
        "current": getattr(completion, "current_correction", None),
        "rubric": getattr(completion, "rubric_eval_state", None),
        "future": getattr(completion, "future_proposal", None),
    })
