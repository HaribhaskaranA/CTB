from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsOwnerOrWorker
from .models import Complaint
from .serializers import ComplaintSerializer, ComplaintCreateSerializer

class ComplaintListView(APIView):
    permission_classes = [IsOwnerOrWorker]

    def get(self, request):
        complaints = Complaint.objects.filter(raised_by=request.user)
        return Response(ComplaintSerializer(complaints, many=True).data)

class ComplaintCreateView(APIView):
    permission_classes = [IsOwnerOrWorker]

    def post(self, request):
        file = request.FILES.get('evidence')
        if file:
            allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                return Response({"error": "Invalid file type. Only JPG/PNG/PDF are allowed."}, status=status.HTTP_400_BAD_REQUEST)
                
        serializer = ComplaintCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(raised_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
