from django.urls import path
from .api_views import ComplaintListView, ComplaintCreateView

urlpatterns = [
    path('', ComplaintListView.as_view(), name='api_complaint_list'),
    path('create/', ComplaintCreateView.as_view(), name='api_complaint_create'),
]
