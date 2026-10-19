from django.urls import path
from .api_views import PaymentListView, PaymentCreateView

urlpatterns = [
    path('', PaymentListView.as_view(), name='api_payment_list'),
    path('create/', PaymentCreateView.as_view(), name='api_payment_create'),
]
