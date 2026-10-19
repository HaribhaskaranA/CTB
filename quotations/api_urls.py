from django.urls import path
from .api_views import QuotationListView, QuotationCreateView, QuotationActionView

urlpatterns = [
    path('', QuotationCreateView.as_view(), name='api_quotation_create'),
    path('list/', QuotationListView.as_view(), name='api_quotation_list'),
    path('<int:pk>/action/', QuotationActionView.as_view(), name='api_quotation_action'),
]
