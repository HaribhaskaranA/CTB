"""
accounts/models.py
Custom User model + OTP for CONNECT TO BUILD
"""
import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    ROLE_CHOICES = [
        ('OWNER', 'House Owner'),
        ('WORKER', 'Worker / Service Provider'),
        ('ADMIN', 'Admin'),
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
        ('hi', 'Hindi'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='OWNER')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    # Public unique ID — shown instead of phone/email
    user_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ctb_users'

    def __str__(self):
        return f"{self.user_id or self.username} ({self.get_role_display()})"

    def get_display_name(self):
        """Return full name from profile if available."""
        if self.role == 'OWNER' and hasattr(self, 'owner_profile'):
            return self.owner_profile.full_name
        if self.role == 'WORKER' and hasattr(self, 'worker_profile'):
            return self.worker_profile.full_name
        return self.get_full_name() or self.username


class OTPRecord(models.Model):
    """
    Stores OTP records for phone-based login verification.
    OTP is stored hashed. Demo mode stores plain for display.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_records')
    otp_hash = models.CharField(max_length=128)
    # DEMO ONLY: plain OTP for on-screen display. Remove in production.
    demo_otp_plain = models.CharField(max_length=6, blank=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'otp_records'

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired() and self.attempt_count < 5

    @classmethod
    def create_for_user(cls, user, otp_code, expiry_minutes=10):
        """Create a new OTP record, invalidating previous ones."""
        import hashlib
        # Invalidate all previous OTPs for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        otp_hash = hashlib.sha256(otp_code.encode()).hexdigest()
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        return cls.objects.create(
            user=user,
            otp_hash=otp_hash,
            demo_otp_plain=otp_code,  # Demo only — remove in production
            expires_at=expires_at,
        )

    def verify(self, otp_code):
        """Verify an OTP code. Returns True if valid."""
        import hashlib
        if not self.is_valid():
            return False
        self.attempt_count += 1
        self.save(update_fields=['attempt_count'])
        input_hash = hashlib.sha256(otp_code.encode()).hexdigest()
        if input_hash == self.otp_hash:
            self.is_used = True
            self.save(update_fields=['is_used'])
            return True
        return False
