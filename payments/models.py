"""payments/models.py — Payment Tracking (DEMO MODE, no real gateway)"""
from django.db import models


class PaymentRecord(models.Model):
    """
    ⚠️ DEMO: This tracks payment milestones only.
    No actual money transfer occurs. For demonstration purposes only.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
    ]

    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='payments'
    )
    worker = models.ForeignKey(
        'workers.WorkerProfile', on_delete=models.CASCADE, related_name='payments'
    )
    milestone = models.ForeignKey(
        'projects.ProjectMilestone', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='payments'
    )
    description = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    # Demo reference — not a real transaction
    demo_reference = models.CharField(max_length=50, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_records'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Payment: {self.project.project_id} — {self.description} ({self.status})"

    @property
    def pending_amount(self):
        return self.total_amount - self.paid_amount
