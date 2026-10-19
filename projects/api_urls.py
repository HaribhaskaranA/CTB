from django.urls import path
from .api_views import (ProjectCreateView, ProjectListView, ProjectDetailView, 
                        ProjectMilestoneListView, MilestoneUpdateView, EvidenceUploadView, 
                        AIAssistAPIView, AvailableProjectsView)

urlpatterns = [
    path('', ProjectListView.as_view(), name='api_project_list'),
    path('create/', ProjectCreateView.as_view(), name='api_project_create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='api_project_detail'),
    path('<int:pk>/milestones/', ProjectMilestoneListView.as_view(), name='api_project_milestones'),
    path('<int:pk>/milestones/<int:m_pk>/', MilestoneUpdateView.as_view(), name='api_milestone_update'),
    path('<int:pk>/evidence/', EvidenceUploadView.as_view(), name='api_evidence_upload'),
    path('ai-assist/', AIAssistAPIView.as_view(), name='api_ai_assist'),
    path('available/', AvailableProjectsView.as_view(), name='api_available_projects'),
]
