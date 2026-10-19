from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import ComplianceRule
from .serializers import ComplianceRuleSerializer

class ComplianceRuleListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = ComplianceRule.objects.filter(is_active=True)
        
        state = request.query_params.get('state')
        city = request.query_params.get('city')
        project_type = request.query_params.get('project_type')
        
        if state: queryset = queryset.filter(state=state)
        if city: queryset = queryset.filter(city__icontains=city)
        if project_type: queryset = queryset.filter(project_type=project_type)
        
        return Response(ComplianceRuleSerializer(queryset, many=True).data)
