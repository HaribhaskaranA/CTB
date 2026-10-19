import json
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import google.generativeai as genai
from accounts.permissions import IsOwner, IsOwnerOrWorker, IsProjectOwner, IsWorker
from .models import Project, ProjectMilestone, MilestoneEvidence
from .serializers import ProjectListSerializer, ProjectDetailSerializer, ProjectCreateSerializer, MilestoneSerializer, EvidenceSerializer
from accounts.utils import generate_project_id
from owners.models import HouseOwnerProfile

DEFAULT_MILESTONE_STAGES = [
    "Site Clearance & Markings", "Excavation & Foundation", "Plinth Beam & Slab",
    "Superstructure (Brickwork)", "Roofing", "Plumbing (Concealed)",
    "Electrical (Concealed)", "Plastering", "Flooring", "Painting",
    "Fittings & Fixtures", "Handover"
]

class ProjectCreateView(APIView):
    permission_classes = [IsOwner]

    def post(self, request):
        owner_profile, _ = HouseOwnerProfile.objects.get_or_create(user=request.user)
        data = request.data.copy()
        
        serializer = ProjectCreateSerializer(data=data)
        if serializer.is_valid():
            project = serializer.save(
                owner=owner_profile, 
                status='ACTIVE',
                project_id=generate_project_id(data.get('state', 'XX'), Project)
            )
            
            for i, stage in enumerate(DEFAULT_MILESTONE_STAGES):
                ProjectMilestone.objects.create(
                    project=project,
                    stage_name=stage,
                    order=i+1
                )
                
            return Response(ProjectDetailSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectListView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        owner_profile = HouseOwnerProfile.objects.get(user=request.user)
        projects = Project.objects.filter(owner=owner_profile)
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

class ProjectDetailView(RetrieveUpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    permission_classes = [IsOwner]

    def get_object(self):
        obj = super().get_object()
        if obj.owner.user != self.request.user:
            self.permission_denied(self.request)
        return obj

class ProjectMilestoneListView(APIView):
    permission_classes = [IsOwnerOrWorker]

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        milestones = ProjectMilestone.objects.filter(project=project).order_by('order')
        serializer = MilestoneSerializer(milestones, many=True)
        return Response(serializer.data)

class MilestoneUpdateView(APIView):
    permission_classes = [IsOwnerOrWorker]

    def patch(self, request, pk, m_pk):
        milestone = get_object_or_404(ProjectMilestone, pk=m_pk, project_id=pk)
        
        if request.user.role == 'WORKER':
            if milestone.assigned_worker and milestone.assigned_worker.user != request.user:
                return Response({"error": "Not assigned to this milestone"}, status=status.HTTP_403_FORBIDDEN)
            allowed_fields = ['progress_percent', 'status', 'notes']
        else:
            allowed_fields = ['status', 'notes', 'payment_status', 'is_approved_by_owner']
            
        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        serializer = MilestoneSerializer(milestone, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EvidenceUploadView(APIView):
    permission_classes = [IsOwnerOrWorker]

    def post(self, request, pk):
        file = request.FILES.get('photo')
        if not file:
            return Response({"error": "No photo provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        allowed_extensions = ['jpg', 'jpeg', 'png']
        allowed_content_types = ['image/jpeg', 'image/png']
        
        ext = file.name.split('.')[-1].lower()
        if ext not in allowed_extensions or file.content_type not in allowed_content_types:
            return Response({"error": "Invalid file type. Only JPG/PNG are allowed."}, status=status.HTTP_400_BAD_REQUEST)
            
        if file.size > 5 * 1024 * 1024:
            return Response({"error": "File size exceeds 5MB limit."}, status=status.HTTP_400_BAD_REQUEST)
            
        data = request.data.copy()
        data['uploaded_by'] = request.user.id
        serializer = EvidenceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AIAssistAPIView(APIView):
    permission_classes = [IsOwner]

    def post(self, request):
        user_text = request.data.get('text', '')
        if not user_text:
            return Response({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        prompt = f"Extract structured construction project requirements from this text and return JSON with keys: project_type, bedrooms, bathrooms, kitchens, halls, balconies, num_floors, built_up_area_sqft, estimated_budget_inr, city, state, required_professions (list from: MASON,ELECTRICIAN,PLUMBER,CARPENTER,PAINTER,WELDER,FLOORING,ROOFER,CIVIL_CONTRACTOR,INTERIOR,ARCHITECT). Text: {user_text}"
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            result = json.loads(response.text.strip('```json').strip('```').strip())
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AvailableProjectsView(APIView):
    permission_classes = [IsWorker]

    def get(self, request):
        projects = Project.objects.filter(status='ACTIVE')
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)
