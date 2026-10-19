from rest_framework import serializers
from .models import ComplianceRule

class ComplianceRuleSerializer(serializers.ModelSerializer):
    disclaimer_html = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceRule
        fields = '__all__'
        
    def get_disclaimer_html(self, obj):
        if obj.is_demo:
            return '<div class="alert alert-warning">Demo Mode: This is a sample compliance rule for Hackathon demonstration.</div>'
        return ''
