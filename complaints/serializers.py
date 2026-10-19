from rest_framework import serializers
from .models import Complaint

class ComplaintSerializer(serializers.ModelSerializer):
    raised_by_id = serializers.ReadOnlyField(source='raised_by.id')

    class Meta:
        model = Complaint
        fields = ['id', 'raised_by_id', 'project', 'category', 'description', 'evidence', 'status', 'created_at', 'admin_notes']

class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['project', 'category', 'description', 'evidence']
