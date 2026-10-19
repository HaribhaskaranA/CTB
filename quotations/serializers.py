from rest_framework import serializers
from .models import Quotation
from workers.serializers import WorkerPublicSerializer

class QuotationSerializer(serializers.ModelSerializer):
    worker = WorkerPublicSerializer(read_only=True)
    
    class Meta:
        model = Quotation
        fields = ['id', 'worker', 'project_id', 'milestone_name', 'amount', 'breakdown', 'estimated_days', 'message', 'status', 'submitted_at']

class QuotationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = ['project', 'milestone_name', 'amount', 'breakdown', 'estimated_days', 'message']
