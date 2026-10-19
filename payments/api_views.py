from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.permissions import IsOwnerOrWorker, IsOwner
from .models import PaymentRecord
from .serializers import PaymentRecordSerializer
from projects.models import Project

class PaymentListView(APIView):
    permission_classes = [IsOwnerOrWorker]

    def get(self, request):
        project_id = request.query_params.get('project')
        if not project_id:
            return Response({"error": "Project ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
        project = get_object_or_404(Project, id=project_id)
        payments = PaymentRecord.objects.filter(project=project)
        return Response(PaymentRecordSerializer(payments, many=True).data)

class PaymentCreateView(APIView):
    permission_classes = [IsOwner]

    def post(self, request):
        serializer = PaymentRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
