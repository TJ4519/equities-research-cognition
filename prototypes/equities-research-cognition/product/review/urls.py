from django.urls import path

from . import views


urlpatterns = [
    path("", views.queue, name="queue"),
    path("cases/<int:case_id>/", views.case, name="case"),
    path("cases/<int:case_id>/lock/", views.lock, name="lock"),
    path("cases/<int:case_id>/reveal/", views.reveal, name="reveal"),
    path("cases/<int:case_id>/lineage/<int:sequence>/", views.record, name="record"),
    path("cases/<int:case_id>/complete/", views.complete, name="complete"),
    path("cases/<int:case_id>/completed/", views.completed, name="completed"),
]
