from django.urls import path
from .api_views import ComplianceRuleListView

urlpatterns = [
    path('', ComplianceRuleListView.as_view(), name='api_compliance_list'),
]
