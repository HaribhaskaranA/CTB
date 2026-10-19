"""
compliance/models.py
Configurable government compliance rules for CONNECT TO BUILD.

⚠️ IMPORTANT: All rules in the hackathon demo are marked is_demo=True.
They are configurable reference checklists, NOT official government approvals.
"""
from django.db import models


class ComplianceRule(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('NEW_CONSTRUCTION', 'New Construction'),
        ('RENOVATION', 'Renovation'),
        ('EXTENSION', 'Extension'),
        ('INTERIOR', 'Interior Work'),
        ('ALL', 'All Project Types'),
    ]

    state = models.CharField(max_length=5, help_text="State code e.g. TN, KA")
    city = models.CharField(max_length=100, blank=True, help_text="Blank = applies state-wide")
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPE_CHOICES, default='ALL')
    requirement_name = models.CharField(max_length=200)
    description = models.TextField()
    # List of document names required
    required_documents = models.JSONField(default=list)
    authority_name = models.CharField(max_length=200)
    authority_url = models.URLField(blank=True, help_text="Official portal URL if available")
    order = models.IntegerField(default=0)
    # is_demo=True MUST show disclaimer on all UI screens
    is_demo = models.BooleanField(
        default=True,
        help_text="True = show 'DEMO — not official government data' disclaimer"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance_rules'
        ordering = ['state', 'city', 'order']

    def __str__(self):
        loc = f"{self.city}, " if self.city else ""
        return f"[{loc}{self.state}] {self.requirement_name}"
