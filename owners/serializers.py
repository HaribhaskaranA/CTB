from rest_framework import serializers
from .models import HouseOwnerProfile

class OwnerPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseOwnerProfile
        fields = ['full_name', 'area', 'city', 'state', 'preferred_language', 'profile_photo', 'created_at', 'updated_at']

class OwnerPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseOwnerProfile
        fields = '__all__'
