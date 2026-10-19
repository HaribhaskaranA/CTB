"""complaints/models.py"""
from django.db import models
from django.utils import timezone


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('WORKER_ABANDONED', 'Worker Abandoned Project'),
        ('WORK_QUALITY', 'Poor Work Quality'),
        ('WORK_INCOMPLETE', 'Work Not Completed as Agreed'),
        ('PAYMENT_DELAYED', 'Payment Delayed or Not Made'),
        ('CONTRACT_CANCELLED', 'Contract Cancelled Without Notice'),
        ('INCORRECT_INFO', 'Incorrect Project Information Provided'),
        ('OTHER', 'Other'),
    ]
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('UNDER_REVIEW', 'Under Review'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    raised_by = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='complaints_raised'
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='complaints'
    )
    against_user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='complaints_against'
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField()
    evidence = models.FileField(upload_to='complaints/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'complaints'
        ordering = ['-created_at']

    def __str__(self):
        return f"Complaint #{self.pk}: {self.get_category_display()} ({self.status})"

    def resolve(self, admin_notes=''):
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.admin_notes = admin_notes
        self.save(update_fields=['status', 'resolved_at', 'admin_notes'])
