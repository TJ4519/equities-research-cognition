from __future__ import annotations

from os import environ
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from harness.langfuse.transport import LangfuseRejected

from .models import (
    Artifact,
    ArtifactVersion,
    Proposal,
    ResearchCampaign,
    ResearchStateTransition,
    WorkOrder,
)
from .services import (
    CampaignRejected,
    accept_research_state,
    approve_planner_programme,
    approve_proposal,
    campaign_profile_state,
    collect_artifacts,
    configured_langfuse_connection,
    correlate_campaign,
    create_owned_job,
    challenge_research_state,
    launch_role,
    refresh_status,
    reject_proposal,
    reject_research_state,
    request_planner_reentry,
    request_proposal_revision,
    rewrite_proposal,
    send_dispatch,
    stop_campaign,
)


def owned_campaign(request: HttpRequest, campaign_id: UUID) -> ResearchCampaign:
    return get_object_or_404(ResearchCampaign, pk=campaign_id, director=request.user)


def rejected(exc: Exception) -> HttpResponse:
    return HttpResponse(str(exc), status=409)


def render_campaign(
    request: HttpRequest,
    item: ResearchCampaign,
    *,
    status: int = 200,
    runtime_block: str | None = None,
    runtime_attempted: bool = False,
) -> HttpResponse:
    if runtime_block is None:
        try:
            configured_langfuse_connection(environ)
        except LangfuseRejected as exc:
            runtime_block = str(exc)
    template = (
        "campaign/job.html"
        if hasattr(item, "run_spec")
        else "campaign/casebook.html"
    )
    return render(
        request,
        template,
        {
            "campaign": item,
            "runtime_block": runtime_block,
            "runtime_attempted": runtime_attempted,
            **campaign_profile_state(item),
        },
        status=status,
    )


@login_required
def campaigns(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            item = create_owned_job(
                director=request.user,
                title=request.POST.get("title", ""),
                issuer_or_security=request.POST.get("issuer_or_security", ""),
                equities_decision_use=request.POST.get(
                    "equities_decision_use", ""
                ),
                evidence_cutoff=request.POST.get("evidence_cutoff", ""),
                question=request.POST.get("commissioned_question", ""),
                run_instruction=request.POST.get("run_instruction", ""),
                starting_artifact=request.FILES.get("starting_artifact"),
                sources=request.FILES.getlist("sources"),
            )
        except CampaignRejected as exc:
            return rejected(exc)
        return redirect("campaign", campaign_id=item.pk)
    rows = ResearchCampaign.objects.filter(director=request.user).order_by(
        "-created_at"
    )
    return render(request, "campaign/index.html", {"campaigns": rows})


@login_required
def campaign(request: HttpRequest, campaign_id: UUID) -> HttpResponse:
    item = owned_campaign(request, campaign_id)
    return render_campaign(request, item)


@login_required
@require_POST
def approve_planner_programme_input(
    request: HttpRequest, campaign_id: UUID
) -> HttpResponse:
    item = owned_campaign(request, campaign_id)
    try:
        approve_planner_programme(item, request.user)
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=item.pk)


def _proposal(
    request: HttpRequest, campaign_id: UUID, proposal_id: UUID
) -> Proposal:
    item = owned_campaign(request, campaign_id)
    return get_object_or_404(Proposal, pk=proposal_id, campaign=item)


@login_required
@require_POST
def approve_proposal_view(
    request: HttpRequest, campaign_id: UUID, proposal_id: UUID
) -> HttpResponse:
    proposal = _proposal(request, campaign_id, proposal_id)
    try:
        state_basis = request.POST.get("state_basis", "commission")
        input_state = None
        if state_basis == "accepted_transition":
            input_state = ResearchStateTransition.objects.filter(
                pk=request.POST.get("input_state"),
                campaign=proposal.campaign,
            ).first()
            if input_state is None:
                raise CampaignRejected("research state is unavailable")
        elif state_basis != "commission":
            raise CampaignRejected("research-state basis is invalid")
        supporting_ids = request.POST.getlist("supporting_states")
        supporting_states = list(
            ResearchStateTransition.objects.filter(
                pk__in=supporting_ids,
                campaign=proposal.campaign,
            )
        )
        if len(supporting_states) != len(set(supporting_ids)):
            raise CampaignRejected("supporting research state is unavailable")
        approve_proposal(
            proposal,
            user=request.user,
            input_artifact_ids=[
                int(value) for value in request.POST.getlist("input_artifacts")
            ],
            input_state=input_state,
            supporting_states=supporting_states,
        )
    except (CampaignRejected, ValidationError, ValueError) as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


def _state(
    request: HttpRequest, campaign_id: UUID, transition_id: UUID
) -> ResearchStateTransition:
    item = owned_campaign(request, campaign_id)
    return get_object_or_404(
        ResearchStateTransition,
        pk=transition_id,
        campaign=item,
    )


@login_required
@require_POST
def accept_state(
    request: HttpRequest, campaign_id: UUID, transition_id: UUID
) -> HttpResponse:
    transition = _state(request, campaign_id, transition_id)
    try:
        accept_research_state(transition, request.user)
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def replan_state(
    request: HttpRequest, campaign_id: UUID, transition_id: UUID
) -> HttpResponse:
    transition = _state(request, campaign_id, transition_id)
    try:
        request_planner_reentry(transition, request.user)
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def challenge_state(
    request: HttpRequest, campaign_id: UUID, transition_id: UUID
) -> HttpResponse:
    transition = _state(request, campaign_id, transition_id)
    try:
        challenge_research_state(
            transition,
            request.user,
            feedback=request.POST.get("feedback", ""),
        )
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def reject_state(
    request: HttpRequest, campaign_id: UUID, transition_id: UUID
) -> HttpResponse:
    transition = _state(request, campaign_id, transition_id)
    try:
        reject_research_state(
            transition,
            request.user,
            reason=request.POST.get("reason", ""),
        )
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def reject_dispatch_proposal(
    request: HttpRequest, campaign_id: UUID, proposal_id: UUID
) -> HttpResponse:
    proposal = _proposal(request, campaign_id, proposal_id)
    try:
        reject_proposal(
            proposal, request.user, reason=request.POST.get("reason", "")
        )
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def request_dispatch_proposal_revision(
    request: HttpRequest, campaign_id: UUID, proposal_id: UUID
) -> HttpResponse:
    proposal = _proposal(request, campaign_id, proposal_id)
    try:
        request_proposal_revision(
            proposal,
            request.user,
            feedback=request.POST.get("feedback", ""),
        )
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def rewrite_dispatch_proposal(
    request: HttpRequest, campaign_id: UUID, proposal_id: UUID
) -> HttpResponse:
    proposal = _proposal(request, campaign_id, proposal_id)
    try:
        rewrite_proposal(
            proposal,
            request.user,
            protocol=request.POST.get("target_role", ""),
            task=request.POST.get("task", ""),
            rationale=request.POST.get("rationale", ""),
        )
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


def _order(
    request: HttpRequest, campaign_id: UUID, order_id: UUID
) -> WorkOrder:
    item = owned_campaign(request, campaign_id)
    return get_object_or_404(WorkOrder, pk=order_id, campaign=item)


@login_required
@require_POST
def launch(
    request: HttpRequest, campaign_id: UUID, order_id: UUID
) -> HttpResponse:
    order = _order(request, campaign_id, order_id)
    try:
        launch_role(order, request.user)
    except CampaignRejected as exc:
        return render_campaign(
            request,
            order.campaign,
            status=409,
            runtime_block=str(exc),
            runtime_attempted=True,
        )
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def send(
    request: HttpRequest, campaign_id: UUID, order_id: UUID
) -> HttpResponse:
    order = _order(request, campaign_id, order_id)
    try:
        send_dispatch(order, request.user)
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def refresh(
    request: HttpRequest, campaign_id: UUID, order_id: UUID
) -> HttpResponse:
    order = _order(request, campaign_id, order_id)
    try:
        refresh_status(order, request.user)
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=campaign_id)


@login_required
@require_POST
def collect(request: HttpRequest, campaign_id: UUID) -> HttpResponse:
    item = owned_campaign(request, campaign_id)
    try:
        collect_artifacts(item, request.user)
    except (CampaignRejected, OSError) as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=item.pk)


@login_required
@require_POST
def stop(request: HttpRequest, campaign_id: UUID) -> HttpResponse:
    item = owned_campaign(request, campaign_id)
    try:
        stop_campaign(item, request.user)
    except CampaignRejected as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=item.pk)


@login_required
@require_POST
def correlate(request: HttpRequest, campaign_id: UUID) -> HttpResponse:
    item = owned_campaign(request, campaign_id)
    try:
        correlate_campaign(
            item,
            request.user,
            configured_langfuse_connection(environ),
        )
    except (CampaignRejected, LangfuseRejected) as exc:
        return rejected(exc)
    return redirect("campaign", campaign_id=item.pk)


@login_required
def artifact(
    request: HttpRequest, campaign_id: UUID, artifact_id: int
) -> HttpResponse:
    item = owned_campaign(request, campaign_id)
    observed = get_object_or_404(Artifact, pk=artifact_id, campaign=item)
    response = HttpResponse(bytes(observed.content), content_type=observed.media_type)
    response["X-Content-SHA256"] = observed.digest
    response["Content-Disposition"] = (
        f'inline; filename="artifact-{observed.pk}-v{observed.version}"'
    )
    return response


@login_required
def input_artifact(
    request: HttpRequest, campaign_id: UUID, artifact_id: UUID
) -> HttpResponse:
    item = owned_campaign(request, campaign_id)
    observed = get_object_or_404(
        ArtifactVersion, pk=artifact_id, campaign=item
    )
    response = HttpResponse(bytes(observed.content), content_type=observed.media_type)
    response["X-Content-SHA256"] = observed.digest
    response["Content-Disposition"] = (
        f'attachment; filename="input-{observed.pk}"'
    )
    return response
