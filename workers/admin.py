from django.contrib import admin
from .models import WorkerProfile, WorkerCertificate

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'profession', 'tracking_id', 'city', 'verification_status', 'availability', 'overall_rating']
    list_filter = ['verification_status', 'profession', 'availability', 'state']
    search_fields = ['full_name', 'user__user_id', 'tracking_id', 'city']
    actions = ['mark_verified', 'mark_under_review', 'mark_rejected']

    @admin.action(description='Mark selected workers as Verified')
    def mark_verified(self, request, queryset):
        queryset.update(verification_status='VERIFIED')
        self.message_user(request, f'{queryset.count()} workers marked as Verified.')

    @admin.action(description='Mark as Under Review')
    def mark_under_review(self, request, queryset):
        queryset.update(verification_status='UNDER_REVIEW')

    @admin.action(description='Reject selected workers')
    def mark_rejected(self, request, queryset):
        queryset.update(verification_status='REJECTED')

@admin.register(WorkerCertificate)
class WorkerCertificateAdmin(admin.ModelAdmin):
    list_display = ['worker', 'certificate_name', 'issuing_authority', 'is_verified', 'uploaded_at']
    list_filter = ['is_verified']
    actions = ['mark_verified']

    @admin.action(description='Mark certificate as Verified')
    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
