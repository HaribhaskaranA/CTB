from rest_framework import serializers
from .models import WorkerProfile, WorkerCertificate

class WorkerPublicSerializer(serializers.ModelSerializer):
    """Public serializer - NEVER exposes phone, email, address, identity documents."""
    worker_id = serializers.SerializerMethodField()

    class Meta:
        model = WorkerProfile
        fields = [
            'id', 'worker_id', 'full_name', 'profession', 'bio', 'skills',
            'years_experience', 'service_areas', 'daily_rate', 'city',
            'state', 'area', 'availability', 'verification_status',
            'overall_rating', 'total_reviews', 'completed_projects', 'profile_photo'
        ]
        # phone_number, email, address, identity_type are EXCLUDED

    def get_worker_id(self, obj):
        return obj.user.user_id if obj.user and hasattr(obj.user, 'user_id') else None

class WorkerPrivateSerializer(serializers.ModelSerializer):
    """Private serializer - for worker's own profile only."""
    worker_id = serializers.SerializerMethodField()

    class Meta:
        model = WorkerProfile
        fields = '__all__'

    def get_worker_id(self, obj):
        return obj.user.user_id if obj.user and hasattr(obj.user, 'user_id') else None

class WorkerCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerCertificate
        fields = '__all__'
