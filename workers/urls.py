from django.urls import path
from .views import (
    WorkerDashboardView, WorkerProjectsView, WorkerPassportView,
    WorkerProfileEditView, WorkerTrackStatusView
)

urlpatterns = [
    path('dashboard/', WorkerDashboardView.as_view(), name='worker_dashboard'),
    path('projects/', WorkerProjectsView.as_view(), name='worker_projects'),
    path('passport/', WorkerPassportView.as_view(), name='worker_passport'),
    path('profile/', WorkerProfileEditView.as_view(), name='worker_profile_edit'),
    path('profile/edit/', WorkerProfileEditView.as_view(), name='worker_profile'),
    path('track-status/', WorkerTrackStatusView.as_view(), name='worker_track_status'),
]
