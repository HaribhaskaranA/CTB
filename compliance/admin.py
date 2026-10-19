from django.contrib import admin
from .models import ComplianceRule

@admin.register(ComplianceRule)
class ComplianceRuleAdmin(admin.ModelAdmin):
    list_display = ['state', 'city', 'project_type', 'requirement_name', 'authority_name', 'is_demo', 'is_active']
    list_filter = ['state', 'project_type', 'is_demo', 'is_active']
