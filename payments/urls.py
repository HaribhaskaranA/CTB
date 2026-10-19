from django.urls import path
from .views import PaymentListView

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment_list'),
    path('<int:project_pk>/', PaymentListView.as_view(), name='project_payments'),
    path('<int:project_pk>/payments/', PaymentListView.as_view(), name='project_payments_legacy'),
]
