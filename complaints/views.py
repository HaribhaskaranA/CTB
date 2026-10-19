from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Complaint

class ComplaintListView(LoginRequiredMixin, View):
    def get(self, request):
        complaints = Complaint.objects.filter(raised_by=request.user)
        return render(request, 'shared/complaints.html', {'complaints': complaints})

class ComplaintCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'shared/complaint_new.html')
    
    def post(self, request):
        pass
