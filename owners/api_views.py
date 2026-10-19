from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsOwner
from .models import HouseOwnerProfile
from .serializers import OwnerPrivateSerializer

class OwnerMeView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        profile, _ = HouseOwnerProfile.objects.get_or_create(user=request.user)
        serializer = OwnerPrivateSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile, _ = HouseOwnerProfile.objects.get_or_create(user=request.user)
        serializer = OwnerPrivateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
