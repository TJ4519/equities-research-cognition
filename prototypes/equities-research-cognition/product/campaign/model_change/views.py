from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from product.campaign.models import (
    AdmissibilityDecision,
    ObjectDisposition,
    ResearchJob,
    SourceAssertion,
    SourceDocumentVersion,
)

from .adapter import case_a_profile
from .forms import (
    CandidateDispositionForm,
    FiledReportRepairForm,
    MeaningConfirmationForm,
    MethodAuthorizationForm,
    RunWorkForm,
)
from .projections import episode_page
from .services import (
    CandidateService,
    DispositionService,
    InvalidationService,
    ModelChangeRejected,
    ObjectService,
    PROTOCOL_VERSION,
    ProjectionService,
    RunService,
    WorkCompiler,
)


def _state(request: HttpRequest, job_id, episode_id) -> dict[str, object]:
    try:
        return ProjectionService.resume(request.user, job_id, episode_id)
    except ModelChangeRejected as exc:
        raise Http404 from exc


def _redirect(state: dict[str, object]) -> HttpResponse:
    return redirect(
        "model_change_episode",
        job_id=state["job"].pk,
        episode_id=state["episode"].pk,
    )


def _render(
    request: HttpRequest,
    state: dict[str, object],
    *,
    message: str | None = None,
    status: int = 200,
) -> HttpResponse:
    return render(
        request,
        "model_change/episode.html",
        {
            **episode_page(state),
            "meaning_form": MeaningConfirmationForm(),
            "method_form": MethodAuthorizationForm(),
            "run_form": RunWorkForm(),
            "repair_form": FiledReportRepairForm(),
            "review_form": CandidateDispositionForm(),
            "message": message,
        },
        status=status,
    )


@login_required
def jobs(request: HttpRequest) -> HttpResponse:
    if not settings.MODEL_CHANGE_V0:
        raise Http404
    rows = ResearchJob.objects.filter(owner=request.user).prefetch_related(
        "model_change_episodes"
    ).order_by("-created_at")
    return render(request, "model_change/index.html", {"jobs": rows})


@login_required
def episode(request: HttpRequest, job_id, episode_id) -> HttpResponse:
    return _render(request, _state(request, job_id, episode_id))


@login_required
@require_POST
def confirm_meaning(request: HttpRequest, job_id, episode_id) -> HttpResponse:
    state = _state(request, job_id, episode_id)
    form = MeaningConfirmationForm(request.POST)
    if not form.is_valid() or state["current_object"] is None:
        return _render(request, state, message="Meaning confirmation was not recorded.", status=409)
    try:
        ObjectService.disposition(
            request.user,
            state["current_object"],
            ObjectDisposition.Action.CONFIRM_MEANING,
            {"confirmed": True},
        )
    except ModelChangeRejected as exc:
        return _render(request, state, message=str(exc), status=409)
    return _redirect(state)


@login_required
@require_POST
def authorize_method(request: HttpRequest, job_id, episode_id) -> HttpResponse:
    state = _state(request, job_id, episode_id)
    form = MethodAuthorizationForm(request.POST)
    actions = {item.action for item in state["object_authorities"]}
    if (
        not form.is_valid()
        or state["current_object"] is None
        or ObjectDisposition.Action.CONFIRM_MEANING not in actions
    ):
        return _render(request, state, message="Confirm the target meaning first.", status=409)
    try:
        ObjectService.disposition(
            request.user,
            state["current_object"],
            ObjectDisposition.Action.AUTHORIZE_METHOD,
            {
                "method": "reported_value",
                "source_rule": "filed_annual_report_for_annual_target",
            },
        )
    except ModelChangeRejected as exc:
        return _render(request, state, message=str(exc), status=409)
    return _redirect(state)


@login_required
@require_POST
def run_work(request: HttpRequest, job_id, episode_id) -> HttpResponse:
    state = _state(request, job_id, episode_id)
    if not RunWorkForm(request.POST).is_valid():
        return _render(request, state, message="Work was not started.", status=409)
    try:
        order = state["work_order"]
        if order is None:
            assertions = list(
                SourceAssertion.objects.select_related(
                    "document_version__artifact"
                ).filter(document_version__episode=state["episode"])
            )
            order = WorkCompiler.compile(
                state["episode"],
                state["current_object"],
                state["object_authorities"],
                state["manifest"],
                assertions,
                PROTOCOL_VERSION,
            )
        RunService.run(request.user, order)
    except ModelChangeRejected as exc:
        return _render(
            request,
            ProjectionService.resume(request.user, job_id, episode_id),
            message=str(exc),
            status=409,
        )
    return _redirect(state)


@login_required
@require_POST
def use_filed_report(request: HttpRequest, job_id, episode_id) -> HttpResponse:
    state = _state(request, job_id, episode_id)
    if not FiledReportRepairForm(request.POST).is_valid():
        return _render(request, state, message="The correction was not recorded.", status=409)
    decision = state["decision"]
    if (
        decision is None
        or decision.outcome != AdmissibilityDecision.Outcome.BLOCK
        or decision.reason_code != "BLOCK_WRONG_DOCUMENT_CLASS"
    ):
        return _render(request, state, message="There is no current source exception to repair.", status=409)
    annual = SourceAssertion.objects.filter(
        document_version__episode=state["episode"],
        document_version__document_class=SourceDocumentVersion.DocumentClass.FILED_ANNUAL_REPORT_10K,
    ).first()
    if annual is None:
        return _render(request, state, message="The captured filed annual report is unavailable.", status=409)
    try:
        _, _, passed = InvalidationService.repair_wrong_source(
            request.user, decision, annual
        )
        if passed.outcome != AdmissibilityDecision.Outcome.PASS:
            raise ModelChangeRejected("REPAIR_BLOCKED", "The replacement did not pass the bounded checks.")
        CandidateService.create(passed, state["episode"].starting_artifact, case_a_profile())
    except ModelChangeRejected as exc:
        return _render(request, state, message=str(exc), status=409)
    return _redirect(state)


@login_required
@require_POST
def record_review(request: HttpRequest, job_id, episode_id) -> HttpResponse:
    state = _state(request, job_id, episode_id)
    form = CandidateDispositionForm(request.POST)
    if not form.is_valid() or state["candidate"] is None:
        return _render(request, state, message="Candidate review was not recorded.", status=409)
    try:
        DispositionService.record(
            request.user,
            state["candidate"],
            state["episode"].named_use,
            form.cleaned_data["action"],
            form.cleaned_data["rationale"],
        )
    except ModelChangeRejected as exc:
        return _render(request, state, message=str(exc), status=409)
    return _redirect(state)
