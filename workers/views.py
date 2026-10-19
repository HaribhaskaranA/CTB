from django.views.generic import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import WorkerProfile
from projects.models import Project, ProjectMilestone
from quotations.models import Quotation


class WorkerDashboardView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        profile = WorkerProfile.objects.filter(user=request.user).first()
        available_projects_count = 0
        quotations = []
        active_milestones = []
        recommended_projects = []

        if profile:
            available_projects_count = Project.objects.filter(status='ACTIVE').count()
            recommended_projects = Project.objects.filter(status='ACTIVE').order_by('-created_at')[:4]
            quotations = Quotation.objects.filter(worker=profile).order_by('-submitted_at')[:5]
            active_milestones = ProjectMilestone.objects.filter(
                assigned_worker=profile, status__in=['PENDING', 'IN_PROGRESS']
            ).select_related('project')[:5]

        context = {
            'profile': profile,
            'available_projects_count': available_projects_count,
            'recommended_projects': recommended_projects,
            'quotations': quotations,
            'active_milestones': active_milestones,
        }
        return render(request, 'worker/dashboard.html', context)


class WorkerProjectsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        projects = Project.objects.filter(status='ACTIVE').order_by('-created_at')
        profile = WorkerProfile.objects.filter(user=request.user).first()
        quoted_project_ids = []
        if profile:
            quoted_project_ids = list(
                Quotation.objects.filter(worker=profile).values_list('project_id', flat=True)
            )
        context = {
            'projects': projects,
            'profile': profile,
            'quoted_project_ids': quoted_project_ids,
        }
        return render(request, 'worker/projects.html', context)


class WorkerPassportView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        profile = get_object_or_404(WorkerProfile, user=request.user)
        milestones = ProjectMilestone.objects.filter(
            assigned_worker=profile, status='COMPLETED'
        ).select_related('project').order_by('-actual_completion')[:10]
        certificates = profile.certificates.all().order_by('-uploaded_at')
        context = {
            'profile': profile,
            'milestones': milestones,
            'certificates': certificates,
        }
        return render(request, 'worker/passport.html', context)


class WorkerProfileEditView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        profile = WorkerProfile.objects.filter(user=request.user).first()
        return render(request, 'worker/profile.html', {'profile': profile})

    def post(self, request):
        profile = WorkerProfile.objects.filter(user=request.user).first()
        if not profile:
            messages.error(request, 'Profile not found.')
            return redirect('worker_dashboard')

        data = request.POST
        if 'full_name' in data and data['full_name'].strip():
            profile.full_name = data['full_name'].strip()
            name_parts = profile.full_name.split()
            request.user.first_name = name_parts[0] if name_parts else ''
            request.user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            request.user.save(update_fields=['first_name', 'last_name'])

        if 'skills' in data:
            profile.skills = [s.strip() for s in data['skills'].split(',') if s.strip()]
        if 'service_areas' in data:
            profile.service_areas = [s.strip() for s in data['service_areas'].split(',') if s.strip()]
        if 'daily_rate' in data:
            try:
                profile.daily_rate = float(data['daily_rate'])
            except (ValueError, TypeError):
                pass
        profile.availability = bool(data.get('availability'))
        if 'bio' in data:
            profile.bio = data['bio'].strip()

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('worker_profile')


class WorkerTrackStatusView(View):
    """
    Public tracking view for worker applicants to check their verification status.
    Workers enter their Tracking ID (or access via ?tracking_id=TRK-TN-XXXXX).
    Once verification_status is set to 'VERIFIED' in Supabase,
    the Worker Login ID is revealed. Otherwise, it remains concealed.
    """
    template_name = 'worker/track_status.html'

    def _get_context(self, tracking_id):
        tracking_id = (tracking_id or '').strip()
        context = {
            'tracking_id': tracking_id,
            'searched': bool(tracking_id),
            'worker': None,
            'is_verified': False,
            'worker_login_id': None,
            'error': None,
        }

        if tracking_id:
            worker = WorkerProfile.objects.filter(
                tracking_id__iexact=tracking_id
            ).select_related('user').first()

            if worker:
                context['worker'] = worker
                is_verified = (worker.verification_status == 'VERIFIED')
                context['is_verified'] = is_verified
                if is_verified:
                    context['worker_login_id'] = worker.user.user_id
            else:
                context['error'] = f"No application found with Tracking ID '{tracking_id}'. Please check and try again."
        return context

    def get(self, request):
        tracking_id = request.GET.get('tracking_id', '').strip()
        context = self._get_context(tracking_id)
        return render(request, self.template_name, context)

    def post(self, request):
        tracking_id = request.POST.get('tracking_id', '').strip()
        context = self._get_context(tracking_id)
        if not tracking_id:
            context['error'] = "Please enter your Application Tracking ID."
        return render(request, self.template_name, context)

