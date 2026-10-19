"""
workers/models.py
Worker / Service Provider profile for CONNECT TO BUILD
"""
from django.db import models
from accounts.models import User

PROFESSION_CHOICES = [
    ('MASON', 'Mason'),
    ('ELECTRICIAN', 'Electrician'),
    ('PLUMBER', 'Plumber'),
    ('CARPENTER', 'Carpenter'),
    ('PAINTER', 'Painter'),
    ('WELDER', 'Welder'),
    ('FLOORING', 'Flooring Worker'),
    ('ROOFER', 'Roofer'),
    ('HVAC', 'HVAC Technician'),
    ('INTERIOR', 'Interior Worker'),
    ('CIVIL_CONTRACTOR', 'Civil Contractor'),
    ('SUB_CONTRACTOR', 'Sub-Contractor'),
    ('ARCHITECT', 'Architect / Designer'),
    ('OTHER', 'Other'),
]

VERIFICATION_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('UNDER_REVIEW', 'Under Review'),
    ('VERIFIED', 'Verified'),
    ('ADDITIONAL_INFO', 'Additional Information Required'),
    ('REJECTED', 'Rejected'),
]


class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    full_name = models.CharField(max_length=100)
    profession = models.CharField(max_length=30, choices=PROFESSION_CHOICES)
    bio = models.TextField(blank=True, help_text="Short professional bio (public)")
    # Public info
    skills = models.JSONField(default=list, help_text='List of skill strings e.g. ["Wiring", "Solar"]')
    years_experience = models.IntegerField(default=0)
    service_areas = models.JSONField(default=list, help_text='List of city/area strings')
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=5)
    area = models.CharField(max_length=100, blank=True)
    availability = models.BooleanField(default=True)
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='PENDING'
    )
    tracking_id = models.CharField(
        max_length=30, unique=True, null=True, blank=True, db_index=True,
        help_text="Application tracking ID for status check before verification (e.g. TRK-TN-XXXXX)"
    )
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.IntegerField(default=0)
    completed_projects = models.IntegerField(default=0)
    profile_photo = models.ImageField(upload_to='worker_photos/', null=True, blank=True)
    # PRIVATE fields — excluded from public serializers
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField(blank=True)
    identity_type = models.CharField(max_length=50, blank=True)
    preferred_language = models.CharField(max_length=5, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'worker_profiles'

    def __str__(self):
        return f"{self.full_name} — {self.get_profession_display()} ({self.user.user_id})"

    @property
    def verification_badge_class(self):
        mapping = {
            'VERIFIED': 'badge-verified',
            'PENDING': 'badge-pending',
            'UNDER_REVIEW': 'badge-review',
            'ADDITIONAL_INFO': 'badge-warning',
            'REJECTED': 'badge-rejected',
        }
        return mapping.get(self.verification_status, 'badge-pending')


class WorkerCertificate(models.Model):
    worker = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='certificates')
    certificate_name = models.CharField(max_length=200)
    issuing_authority = models.CharField(max_length=200, blank=True)
    document = models.FileField(upload_to='worker_certs/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)  # Set by admin only
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'worker_certificates'

    def __str__(self):
        return f"{self.certificate_name} — {self.worker.full_name}"
