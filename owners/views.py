from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import HouseOwnerProfile
from projects.models import Project
from complaints.models import Complaint
from payments.models import PaymentRecord
from workers.models import WorkerProfile


class OwnerDashboardView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        profile = HouseOwnerProfile.objects.filter(user=request.user).first()
        projects = []
        open_complaints = 0
        pending_payments = 0
        total_projects = 0
        active_projects = 0

        if profile:
            projects = Project.objects.filter(owner=profile).order_by('-created_at')[:5]
            total_projects = Project.objects.filter(owner=profile).count()
            active_projects = Project.objects.filter(owner=profile, status='ACTIVE').count()
            open_complaints = Complaint.objects.filter(
                raised_by=request.user, status__in=['OPEN', 'UNDER_REVIEW']
            ).count()
            pending_payments = PaymentRecord.objects.filter(
                project__owner=profile, status__in=['PENDING', 'PARTIAL']
            ).count()

        # Query ONLY registered and verified workers from database
        verified_workers = WorkerProfile.objects.filter(
            verification_status='VERIFIED'
        ).select_related('user').order_by('-overall_rating', '-created_at')[:6]

        context = {
            'profile': profile,
            'projects': projects,
            'open_complaints': open_complaints,
            'pending_payments': pending_payments,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'verified_workers': verified_workers,
        }
        return render(request, 'owner/dashboard.html', context)
