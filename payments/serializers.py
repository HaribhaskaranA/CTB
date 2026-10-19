from rest_framework import serializers
from .models import PaymentRecord

class PaymentRecordSerializer(serializers.ModelSerializer):
    pending_amount = serializers.ReadOnlyField()

    class Meta:
        model = PaymentRecord
        fields = '__all__'
