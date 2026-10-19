from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['raised_by', 'project', 'category', 'status', 'created_at']
    list_filter = ['status', 'category']
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        queryset.update(status='RESOLVED')
