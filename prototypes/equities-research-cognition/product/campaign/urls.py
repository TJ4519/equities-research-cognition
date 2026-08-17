from django.urls import path

from . import views


urlpatterns = [
    path("", views.campaigns, name="campaigns"),
    path("<uuid:campaign_id>/", views.campaign, name="campaign"),
    path(
        "<uuid:campaign_id>/planner/approve/",
        views.approve_planner_programme_input,
        name="campaign_approve_planner_programme",
    ),
    path(
        "<uuid:campaign_id>/proposals/<uuid:proposal_id>/approve/",
        views.approve_proposal_view,
        name="campaign_approve_proposal",
    ),
    path(
        "<uuid:campaign_id>/proposals/<uuid:proposal_id>/reject/",
        views.reject_dispatch_proposal,
        name="campaign_reject_proposal",
    ),
    path(
        "<uuid:campaign_id>/proposals/<uuid:proposal_id>/request-revision/",
        views.request_dispatch_proposal_revision,
        name="campaign_request_proposal_revision",
    ),
    path(
        "<uuid:campaign_id>/proposals/<uuid:proposal_id>/rewrite/",
        views.rewrite_dispatch_proposal,
        name="campaign_rewrite_proposal",
    ),
    path(
        "<uuid:campaign_id>/states/<uuid:transition_id>/accept/",
        views.accept_state,
        name="campaign_accept_state",
    ),
    path(
        "<uuid:campaign_id>/states/<uuid:transition_id>/replan/",
        views.replan_state,
        name="campaign_replan_state",
    ),
    path(
        "<uuid:campaign_id>/states/<uuid:transition_id>/challenge/",
        views.challenge_state,
        name="campaign_challenge_state",
    ),
    path(
        "<uuid:campaign_id>/states/<uuid:transition_id>/reject/",
        views.reject_state,
        name="campaign_reject_state",
    ),
    path(
        "<uuid:campaign_id>/work/<uuid:order_id>/launch/",
        views.launch,
        name="campaign_launch",
    ),
    path(
        "<uuid:campaign_id>/work/<uuid:order_id>/send/",
        views.send,
        name="campaign_send",
    ),
    path(
        "<uuid:campaign_id>/work/<uuid:order_id>/refresh/",
        views.refresh,
        name="campaign_refresh",
    ),
    path("<uuid:campaign_id>/collect/", views.collect, name="campaign_collect"),
    path("<uuid:campaign_id>/stop/", views.stop, name="campaign_stop"),
    path(
        "<uuid:campaign_id>/correlate/",
        views.correlate,
        name="campaign_correlate",
    ),
    path(
        "<uuid:campaign_id>/artifacts/<int:artifact_id>/",
        views.artifact,
        name="campaign_artifact",
    ),
    path(
        "<uuid:campaign_id>/inputs/<uuid:artifact_id>/",
        views.input_artifact,
        name="campaign_input_artifact",
    ),
]
