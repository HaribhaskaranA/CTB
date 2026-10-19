from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project
from .models import PaymentRecord

class PaymentListView(LoginRequiredMixin, View):
    def get(self, request, project_pk=None):
        project = None
        if project_pk:
            project = get_object_or_404(Project, pk=project_pk)
        elif hasattr(request.user, 'owner_profile'):
            project = Project.objects.filter(owner=request.user.owner_profile).first()

        payments = []
        if project:
            payments = PaymentRecord.objects.filter(project=project).order_by('-recorded_at')
        elif request.user.role == 'WORKER' and hasattr(request.user, 'worker_profile'):
            payments = PaymentRecord.objects.filter(worker=request.user.worker_profile).order_by('-recorded_at')
        elif hasattr(request.user, 'owner_profile'):
            payments = PaymentRecord.objects.filter(project__owner=request.user.owner_profile).order_by('-recorded_at')

        return render(request, 'shared/payments.html', {'project': project, 'payments': payments})
