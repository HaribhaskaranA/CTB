from django.contrib import admin
from .models import Project, ProjectMilestone, MilestoneEvidence

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'title', 'owner', 'status', 'current_stage', 'city']

admin.site.register(ProjectMilestone)
admin.site.register(MilestoneEvidence)
