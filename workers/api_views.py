from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from accounts.permissions import IsOwner, IsWorker
from .models import WorkerProfile, WorkerCertificate
from .serializers import WorkerPublicSerializer, WorkerPrivateSerializer, WorkerCertificateSerializer
from django.db.models import Q

class WorkerListView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        queryset = WorkerProfile.objects.all()
        profession = request.query_params.get('profession')
        city = request.query_params.get('city')
        availability = request.query_params.get('availability')
        verification_status = request.query_params.get('verification_status')
        min_experience = request.query_params.get('min_experience')
        max_rate = request.query_params.get('max_rate')

        if profession:
            queryset = queryset.filter(profession=profession)
        if city:
            queryset = queryset.filter(Q(city__icontains=city) | Q(service_areas__icontains=city))
        if availability is not None:
            queryset = queryset.filter(availability=(availability.lower() == 'true'))
        if verification_status:
            queryset = queryset.filter(verification_status=verification_status)
        if min_experience:
            try:
                queryset = queryset.filter(years_experience__gte=int(min_experience))
            except ValueError:
                pass
        if max_rate:
            try:
                queryset = queryset.filter(daily_rate__lte=float(max_rate))
            except ValueError:
                pass

        serializer = WorkerPublicSerializer(queryset, many=True)
        return Response({'results': serializer.data, 'count': queryset.count()})

class WorkerSearchView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        queryset = WorkerProfile.objects.all()
        q = request.query_params.get('q', '')
        profession = request.query_params.get('profession')
        availability = request.query_params.get('availability')
        verified_only = request.query_params.get('verified_only')

        if q:
            queryset = queryset.filter(
                Q(full_name__icontains=q) |
                Q(skills__icontains=q) |
                Q(city__icontains=q) |
                Q(service_areas__icontains=q)
            )
        if profession:
            queryset = queryset.filter(profession=profession)
        if availability is not None:
            queryset = queryset.filter(availability=(availability.lower() == 'true'))
        if verified_only and verified_only.lower() == 'true':
            queryset = queryset.filter(verification_status='VERIFIED')

        serializer = WorkerPublicSerializer(queryset, many=True)
        return Response({'results': serializer.data, 'count': queryset.count()})

class WorkerPublicDetailView(RetrieveAPIView):
    queryset = WorkerProfile.objects.all()
    serializer_class = WorkerPublicSerializer
    permission_classes = [IsOwner]

class WorkerMeView(APIView):
    permission_classes = [IsWorker]

    def get(self, request):
        try:
            profile = WorkerProfile.objects.get(user=request.user)
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Worker profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WorkerPrivateSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        try:
            profile = WorkerProfile.objects.get(user=request.user)
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Worker profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WorkerPrivateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkerCertificateView(APIView):
    permission_classes = [IsWorker]

    def post(self, request):
        try:
            profile = WorkerProfile.objects.get(user=request.user)
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Worker profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get('document')
        if not file:
            return Response({'error': 'No document provided.'}, status=status.HTTP_400_BAD_REQUEST)

        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        ext = file.name.split('.')[-1].lower()

        if ext not in allowed_extensions or file.content_type not in allowed_types:
            return Response({'error': 'Invalid file type. Only PDF/JPG/PNG allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        if file.size > 5 * 1024 * 1024:
            return Response({'error': 'File size exceeds 5MB.'}, status=status.HTTP_400_BAD_REQUEST)

        cert = WorkerCertificate.objects.create(
            worker=profile,
            certificate_name=request.data.get('certificate_name', file.name),
            issuing_authority=request.data.get('issuing_authority', ''),
            document=file,
        )
        return Response(WorkerCertificateSerializer(cert).data, status=status.HTTP_201_CREATED)
