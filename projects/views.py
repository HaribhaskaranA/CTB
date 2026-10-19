from django.views.generic import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Project, ProjectMilestone, DEFAULT_MILESTONE_STAGES
from owners.models import HouseOwnerProfile
from workers.models import WorkerProfile
from accounts.utils import generate_project_id


class ProjectListView(LoginRequiredMixin, View):
    def get(self, request):
        projects = []
        if hasattr(request.user, 'owner_profile'):
            projects = Project.objects.filter(owner=request.user.owner_profile).order_by('-created_at')
        elif request.user.role == 'OWNER':
            profile = HouseOwnerProfile.objects.filter(user=request.user).first()
            if profile:
                projects = Project.objects.filter(owner=profile).order_by('-created_at')
        return render(request, 'owner/project_list.html', {'projects': projects})


class NewProjectView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'owner/project_new.html')


class ProjectComplianceView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk) if pk else None
        return render(request, 'owner/compliance.html', {'project': project})


class ProjectRequirementsView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk) if pk else None
        return render(request, 'owner/requirements.html', {'project': project})

    def post(self, request, pk=None):
        data = request.POST
        
        # Ensure owner profile exists
        owner_profile = getattr(request.user, 'owner_profile', None)
        if not owner_profile:
            owner_profile = HouseOwnerProfile.objects.filter(user=request.user).first()
        if not owner_profile:
            state_code = 'TN'
            owner_profile = HouseOwnerProfile.objects.create(
                user=request.user,
                full_name=request.user.get_display_name() or 'House Owner',
                city='Chennai',
                state=state_code,
                address='',
                phone_number=request.user.phone_number or '',
                email=request.user.email or '',
            )

        # Parse project type
        type_input = data.get('proj_type', 'New').strip().lower()
        type_map = {
            'new': 'NEW_CONSTRUCTION',
            'renovation': 'RENOVATION',
            'extension': 'EXTENSION',
            'interior': 'INTERIOR',
            'repair': 'REPAIR',
        }
        project_type = type_map.get(type_input, 'NEW_CONSTRUCTION')

        # Clean numeric inputs
        try:
            built_up_area = float(data.get('area', 1500) or 1500)
        except (ValueError, TypeError):
            built_up_area = 1500.0

        try:
            num_floors = int(data.get('floors', 1) or 1)
        except (ValueError, TypeError):
            num_floors = 1

        try:
            bedrooms = int(data.get('bedrooms', 2) or 2)
        except (ValueError, TypeError):
            bedrooms = 2

        try:
            bathrooms = int(data.get('bathrooms', 2) or 2)
        except (ValueError, TypeError):
            bathrooms = 2

        try:
            kitchens = int(data.get('kitchens', 1) or 1)
        except (ValueError, TypeError):
            kitchens = 1

        has_swimming_pool = bool(data.get('has_swimming_pool'))
        has_terrace = bool(data.get('has_terrace'))

        # Budget parsing
        raw_budget = str(data.get('estimated_budget', '50,00,000')).replace(',', '').replace('₹', '').strip()
        try:
            estimated_budget = float(raw_budget)
        except (ValueError, TypeError):
            estimated_budget = 5000000.0

        start_date_val = data.get('start_date') or None
        other_requirements = data.get('other_requirements', '').strip()

        state_code = owner_profile.state or 'TN'
        city = owner_profile.city or 'Chennai'
        area = owner_profile.area or ''

        if pk:
            project = get_object_or_404(Project, pk=pk)
            project.project_type = project_type
            project.built_up_area = built_up_area
            project.num_floors = num_floors
            project.bedrooms = bedrooms
            project.bathrooms = bathrooms
            project.kitchens = kitchens
            project.has_swimming_pool = has_swimming_pool
            project.has_terrace = has_terrace
            project.estimated_budget = estimated_budget
            if start_date_val:
                project.start_date = start_date_val
            project.other_requirements = other_requirements
            project.status = 'ACTIVE'
            project.save()
        else:
            project_id = generate_project_id(state_code, Project)
            title = f"{bedrooms}BHK {project.get_project_type_display() if hasattr(project_type, 'get_project_type_display') else type_input.title()} Construction"
            project = Project.objects.create(
                owner=owner_profile,
                project_id=project_id,
                title=title,
                project_type=project_type,
                land_status='HAS_LAND',
                city=city,
                state=state_code,
                area=area,
                num_floors=num_floors,
                built_up_area=built_up_area,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                kitchens=kitchens,
                has_swimming_pool=has_swimming_pool,
                has_terrace=has_terrace,
                estimated_budget=estimated_budget,
                start_date=start_date_val if start_date_val else None,
                other_requirements=other_requirements,
                status='ACTIVE',
                current_stage='Planning',
                land_verified=True,
                compliance_acknowledged=True,
            )

            # Auto-create all 12 default milestones
            for order, stage_name in enumerate(DEFAULT_MILESTONE_STAGES, 1):
                ProjectMilestone.objects.create(
                    project=project,
                    stage_name=stage_name,
                    order=order,
                    status='IN_PROGRESS' if order == 1 else 'PENDING',
                    payment_status='PENDING',
                    progress_percent=0,
                )

        return redirect('project_roadmap', pk=project.pk)


class AIAssistView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk) if pk else None
        return render(request, 'owner/ai_assist.html', {'project': project})


class WorkerSearchView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk) if pk else None
        from workers.models import WorkerProfile
        from django.db.models import Q

        profession = request.GET.get('profession')
        city = request.GET.get('city')
        min_exp = request.GET.get('min_experience')
        max_rate = request.GET.get('max_rate')

        # Query ONLY verified workers registered on the website
        workers = WorkerProfile.objects.filter(
            verification_status='VERIFIED'
        ).select_related('user')

        if profession:
            workers = workers.filter(profession=profession)
        if city:
            workers = workers.filter(Q(city__icontains=city) | Q(area__icontains=city))
        if min_exp:
            try:
                workers = workers.filter(years_experience__gte=int(min_exp))
            except ValueError:
                pass
        if max_rate:
            try:
                workers = workers.filter(daily_rate__lte=float(max_rate))
            except ValueError:
                pass

        workers = workers.order_by('-overall_rating', '-created_at')

        return render(request, 'owner/worker_search.html', {
            'project': project,
            'workers': workers,
            'selected_profession': profession,
            'selected_city': city,
        })


class WorkerPublicProfileView(LoginRequiredMixin, View):
    def get(self, request, worker_pk=None, pk=None):
        project = Project.objects.filter(pk=pk).first() if pk else None
        from workers.models import WorkerProfile
        if worker_pk:
            worker = get_object_or_404(WorkerProfile, pk=worker_pk)
        else:
            worker = WorkerProfile.objects.filter(verification_status='VERIFIED').first()
            if not worker:
                worker = WorkerProfile.objects.first()
        return render(request, 'owner/worker_profile.html', {'project': project, 'worker': worker})


class QuotationListView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk) if pk else None
        return render(request, 'owner/quotations.html', {'project': project})


class ProjectRoadmapView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        project = None
        if pk:
            project = get_object_or_404(Project, pk=pk)
        elif hasattr(request.user, 'owner_profile'):
            project = Project.objects.filter(owner=request.user.owner_profile).order_by('-created_at').first()
        elif request.user.role == 'OWNER':
            profile = HouseOwnerProfile.objects.filter(user=request.user).first()
            if profile:
                project = Project.objects.filter(owner=profile).order_by('-created_at').first()
        elif hasattr(request.user, 'worker_profile'):
            milestone = ProjectMilestone.objects.filter(assigned_worker=request.user.worker_profile).first()
            if milestone:
                project = milestone.project
            else:
                project = Project.objects.filter(status='ACTIVE').first()

        milestones = []
        if project:
            milestones = list(project.milestones.all().select_related('assigned_worker').order_by('order'))

        return render(request, 'shared/roadmap.html', {
            'project': project,
            'milestones': milestones,
            'user_role': request.user.role,
        })

    def post(self, request, pk=None):
        return ProjectRequirementsView.as_view()(request, pk=pk)


class ProjectProgressView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        project = None
        if pk:
            project = get_object_or_404(Project, pk=pk)
        elif hasattr(request.user, 'owner_profile'):
            project = Project.objects.filter(owner=request.user.owner_profile).first()
        return render(request, 'shared/progress.html', {'project': project})
