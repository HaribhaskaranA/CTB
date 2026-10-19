from rest_framework import serializers
from .models import Project, ProjectMilestone, MilestoneEvidence
from workers.serializers import WorkerPublicSerializer

class ProjectListSerializer(serializers.ModelSerializer):
    overall_progress = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = ['id', 'project_id', 'title', 'project_type', 'status', 'current_stage', 'city', 'state', 'estimated_budget', 'overall_progress', 'created_at']

class ProjectDetailSerializer(serializers.ModelSerializer):
    overall_progress = serializers.ReadOnlyField()

    class Meta:
        model = Project
        exclude = ['owner']

class MilestoneSerializer(serializers.ModelSerializer):
    assigned_worker = WorkerPublicSerializer(read_only=True)

    class Meta:
        model = ProjectMilestone
        fields = '__all__'

class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneEvidence
        fields = ['id', 'milestone', 'photo', 'caption', 'timestamp', 'approved_by_owner']

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['project_id', 'status', 'current_stage', 'created_at', 'updated_at', 'overall_progress', 'owner']
