from django.urls import path

from . import views

app_name = "spaces"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("spaces/new/", views.space_create, name="create"),
    path("spaces/<slug:slug>/", views.space_detail, name="detail"),
    path("spaces/<slug:slug>/edit/", views.space_edit, name="edit"),
    path("spaces/<slug:slug>/delete/", views.space_delete, name="delete"),
    path("spaces/<slug:slug>/inbox/", views.inbox, name="inbox"),
    path(
        "spaces/<slug:slug>/inbox/<int:pk>/approve/",
        views.approve_testimonial,
        name="approve",
    ),
    path(
        "spaces/<slug:slug>/inbox/<int:pk>/reject/",
        views.reject_testimonial,
        name="reject",
    ),
    path("s/<slug:slug>/", views.collect, name="collect"),
    path("s/<slug:slug>/submit/", views.collect_submit, name="collect_submit"),
    path("s/<slug:slug>/wall/", views.wall, name="wall"),
]
