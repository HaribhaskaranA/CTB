from django.contrib import admin
from .models import Quotation

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['worker', 'project', 'amount', 'status', 'submitted_at']
    list_filter = ['status']
    actions = ['accept_quote']

    def accept_quote(self, request, queryset):
        for q in queryset:
            q.accept()
