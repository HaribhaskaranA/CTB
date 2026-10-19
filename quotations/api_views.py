from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.permissions import IsOwner, IsWorker
from .models import Quotation
from .serializers import QuotationSerializer, QuotationCreateSerializer
from projects.models import Project, ProjectMilestone
from workers.models import WorkerProfile

class QuotationListView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        project_id = request.query_params.get('project')
        if not project_id:
            return Response({"error": "Project ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
        project = get_object_or_404(Project, id=project_id, owner__user=request.user)
        quotations = Quotation.objects.filter(project=project)
        return Response(QuotationSerializer(quotations, many=True).data)

class QuotationCreateView(APIView):
    permission_classes = [IsWorker]

    def post(self, request):
        worker_profile = get_object_or_404(WorkerProfile, user=request.user)
        project_id = request.data.get('project')
        
        if Quotation.objects.filter(worker=worker_profile, project_id=project_id, status='ACCEPTED').exists():
            return Response({"error": "You already have an accepted quote for this project."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = QuotationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(worker=worker_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuotationActionView(APIView):
    permission_classes = [IsOwner]

    def patch(self, request, pk):
        quotation = get_object_or_404(Quotation, pk=pk)
        if quotation.project.owner.user != request.user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            
        action = request.data.get('action')
        if action == 'accept':
            quotation.accept()
            # Auto assign to first unassigned milestone
            first_unassigned = ProjectMilestone.objects.filter(project=quotation.project, assigned_worker__isnull=True).order_by('order').first()
            if first_unassigned:
                first_unassigned.assigned_worker = quotation.worker
                first_unassigned.save()
            return Response({"status": "accepted"})
        elif action == 'reject':
            quotation.reject()
            return Response({"status": "rejected"})
        
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
