"""quotations/models.py"""
from django.db import models
from django.utils import timezone


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    worker = models.ForeignKey(
        'workers.WorkerProfile', on_delete=models.CASCADE, related_name='quotations'
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='quotations'
    )
    milestone_name = models.CharField(max_length=100, blank=True, help_text="Which phase/milestone")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # breakdown: {"materials": 10000, "labor": 25000, "other": 3000}
    breakdown = models.JSONField(default=dict, blank=True)
    estimated_days = models.IntegerField(default=0)
    message = models.TextField(blank=True, help_text="Cover message from worker")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'quotations'
        unique_together = ['worker', 'project']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Quote by {self.worker.user.user_id} for {self.project.project_id} — ₹{self.amount}"

    def accept(self):
        self.status = 'ACCEPTED'
        self.responded_at = timezone.now()
        self.save(update_fields=['status', 'responded_at'])
        # Reject all other quotes for same project
        Quotation.objects.filter(
            project=self.project, status='PENDING'
        ).exclude(pk=self.pk).update(status='REJECTED')

    def reject(self):
        self.status = 'REJECTED'
        self.responded_at = timezone.now()
        self.save(update_fields=['status', 'responded_at'])
