from django.urls import path

from . import views


urlpatterns = [
    path("", views.jobs, name="model_change_jobs"),
    path(
        "<uuid:job_id>/model-change/<uuid:episode_id>/",
        views.episode,
        name="model_change_episode",
    ),
    path(
        "<uuid:job_id>/model-change/<uuid:episode_id>/confirm-meaning/",
        views.confirm_meaning,
        name="model_change_confirm_meaning",
    ),
    path(
        "<uuid:job_id>/model-change/<uuid:episode_id>/authorize-method/",
        views.authorize_method,
        name="model_change_authorize_method",
    ),
    path(
        "<uuid:job_id>/model-change/<uuid:episode_id>/run/",
        views.run_work,
        name="model_change_run",
    ),
    path(
        "<uuid:job_id>/model-change/<uuid:episode_id>/use-filed-report/",
        views.use_filed_report,
        name="model_change_use_filed_report",
    ),
    path(
        "<uuid:job_id>/model-change/<uuid:episode_id>/record-review/",
        views.record_review,
        name="model_change_record_review",
    ),
]
