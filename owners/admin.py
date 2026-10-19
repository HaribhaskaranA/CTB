from django.contrib import admin
from .models import HouseOwnerProfile

@admin.register(HouseOwnerProfile)
class HouseOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'state', 'created_at']
    search_fields = ['full_name', 'user__user_id']
    list_filter = ['state']
