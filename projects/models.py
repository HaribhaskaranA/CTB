"""
projects/models.py
Project lifecycle models for CONNECT TO BUILD
"""
from django.db import models
from django.utils import timezone

PROJECT_TYPE_CHOICES = [
    ('NEW_CONSTRUCTION', 'New Construction'),
    ('RENOVATION', 'Renovation'),
    ('EXTENSION', 'Extension'),
    ('INTERIOR', 'Interior Work'),
    ('REPAIR', 'Repair'),
]

DEFAULT_MILESTONE_STAGES = [
    'Planning',
    'Site Preparation',
    'Foundation',
    'Structural Work',
    'Electrical',
    'Plumbing',
    'Roofing',
    'Flooring',
    'Carpentry',
    'Painting',
    'Inspection',
    'Completed',
]

LAND_STATUS_CHOICES = [
    ('HAS_LAND', 'Has Land'),
    ('NEEDS_LAND', 'Needs Land / Finding Land'),
]

PROJECT_STATUS_CHOICES = [
    ('DRAFT', 'Draft'),
    ('ACTIVE', 'Active'),
    ('PAUSED', 'Paused'),
    ('COMPLETED', 'Completed'),
    ('CANCELLED', 'Cancelled'),
]

DEFAULT_MILESTONE_STAGES = [
    'Planning', 'Site Preparation', 'Foundation', 'Structural Work',
    'Electrical', 'Plumbing', 'Roofing', 'Flooring',
    'Carpentry', 'Painting', 'Inspection', 'Completed',
]


class Project(models.Model):
    owner = models.ForeignKey(
        'owners.HouseOwnerProfile', on_delete=models.CASCADE, related_name='projects'
    )
    project_id = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=200)
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPE_CHOICES, default='NEW_CONSTRUCTION')
    land_status = models.CharField(max_length=15, choices=LAND_STATUS_CHOICES, default='HAS_LAND')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=5)
    area = models.CharField(max_length=100, blank=True)
    # Construction specs
    num_floors = models.IntegerField(default=1)
    built_up_area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    kitchens = models.IntegerField(default=1)
    halls = models.IntegerField(default=1)
    balconies = models.IntegerField(default=0)
    parking = models.IntegerField(default=0)
    has_swimming_pool = models.BooleanField(default=False)
    has_terrace = models.BooleanField(default=False)
    other_requirements = models.TextField(blank=True)
    estimated_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    expected_completion = models.DateField(null=True, blank=True)
    current_stage = models.CharField(max_length=50, default='Planning')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='DRAFT')
    # AI structured output — non-private, Gemini-generated only
    ai_structured_data = models.JSONField(null=True, blank=True)
    # Workflow flags
    land_verified = models.BooleanField(default=False)
    compliance_acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project_id} — {self.title}"

    @property
    def overall_progress(self):
        milestones = self.milestones.all()
        if not milestones.exists():
            return 0
        total = milestones.count()
        completed = milestones.filter(status='COMPLETED').count()
        in_progress = milestones.filter(status='IN_PROGRESS')
        partial = sum(m.progress_percent for m in in_progress) / 100
        return int(((completed + partial) / total) * 100)

    def get_required_professions(self):
        """Return list of professions from AI data or defaults."""
        if self.ai_structured_data and 'required_professions' in self.ai_structured_data:
            return self.ai_structured_data['required_professions']
        return ['MASON', 'ELECTRICIAN', 'PLUMBER', 'CARPENTER', 'PAINTER']


class ProjectMilestone(models.Model):
    MILESTONE_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    stage_name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    assigned_worker = models.ForeignKey(
        'workers.WorkerProfile', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_milestones'
    )
    start_date = models.DateField(null=True, blank=True)
    expected_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)
    progress_percent = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=MILESTONE_STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    is_approved_by_owner = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'project_milestones'
        ordering = ['order']

    def __str__(self):
        return f"{self.project.project_id} — {self.stage_name} ({self.status})"


class MilestoneEvidence(models.Model):
    milestone = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='evidence')
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='evidence/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    approved_by_owner = models.BooleanField(default=False)

    class Meta:
        db_table = 'milestone_evidence'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Evidence: {self.milestone.stage_name} — {self.timestamp.strftime('%d %b %Y')}"
