from django.urls import path
from .views import ComplaintListView, ComplaintCreateView

urlpatterns = [
    path('', ComplaintListView.as_view(), name='complaint_list'),
    path('new/', ComplaintCreateView.as_view(), name='complaint_create'),
]
