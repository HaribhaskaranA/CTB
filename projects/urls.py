from django.urls import path
from .views import (ProjectListView, NewProjectView, ProjectComplianceView, 
                    ProjectRequirementsView, AIAssistView, WorkerSearchView, 
                    WorkerPublicProfileView, QuotationListView, ProjectRoadmapView, 
                    ProjectProgressView)

urlpatterns = [
    path('', ProjectListView.as_view(), name='project_list'),
    path('new/', NewProjectView.as_view(), name='project_new'),
    
    # Standalone routes (no pk required)
    path('compliance/', ProjectComplianceView.as_view(), name='compliance'),
    path('requirements/', ProjectRequirementsView.as_view(), name='requirements'),
    path('roadmap/', ProjectRoadmapView.as_view(), name='roadmap'),
    path('progress/', ProjectProgressView.as_view(), name='progress'),
    path('workers/search/', WorkerSearchView.as_view(), name='worker_search'),
    path('workers/<int:worker_pk>/', WorkerPublicProfileView.as_view(), name='worker_public_profile'),
    path('workers/profile/', WorkerPublicProfileView.as_view(), name='worker_public_profile_default'),

    # Project-specific routes
    path('<int:pk>/compliance/', ProjectComplianceView.as_view(), name='project_compliance'),
    path('<int:pk>/requirements/', ProjectRequirementsView.as_view(), name='project_requirements'),
    path('<int:pk>/ai-assist/', AIAssistView.as_view(), name='project_ai_assist'),
    path('<int:pk>/workers/', WorkerSearchView.as_view(), name='project_worker_search'),
    path('<int:pk>/workers/<int:worker_pk>/', WorkerPublicProfileView.as_view(), name='project_worker_public_profile'),
    path('<int:pk>/quotations/', QuotationListView.as_view(), name='project_quotations'),
    path('<int:pk>/roadmap/', ProjectRoadmapView.as_view(), name='project_roadmap'),
    path('<int:pk>/progress/', ProjectProgressView.as_view(), name='project_progress'),
]
