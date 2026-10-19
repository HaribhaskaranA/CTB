"""accounts/admin.py"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPRecord


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['user_id', 'get_full_name', 'role', 'phone_number', 'is_phone_verified', 'created_at']
    list_filter = ['role', 'is_phone_verified', 'preferred_language']
    search_fields = ['user_id', 'email', 'phone_number', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['user_id', 'created_at', 'updated_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('CTB Fields', {
            'fields': ('role', 'phone_number', 'user_id', 'preferred_language', 'is_phone_verified')
        }),
    )


@admin.register(OTPRecord)
class OTPRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'is_used', 'attempt_count']
    list_filter = ['is_used']
    readonly_fields = ['otp_hash', 'demo_otp_plain', 'created_at']
    search_fields = ['user__user_id']

    def has_add_permission(self, request):
        return False  # OTPs created only programmatically
