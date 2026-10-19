from django.urls import path
from .api_views import WorkerListView, WorkerSearchView, WorkerPublicDetailView, WorkerMeView, WorkerCertificateView

urlpatterns = [
    path('', WorkerListView.as_view(), name='api_worker_list'),
    path('search/', WorkerSearchView.as_view(), name='api_worker_search'),
    path('<int:pk>/public/', WorkerPublicDetailView.as_view(), name='api_worker_public_detail'),
    path('me/', WorkerMeView.as_view(), name='api_worker_me'),
    path('me/certificates/', WorkerCertificateView.as_view(), name='api_worker_certificates'),
]
