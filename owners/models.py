"""
owners/models.py
House Owner profile + government ID document metadata for CONNECT TO BUILD
"""
from django.db import models
from accounts.models import User

STATE_CHOICES = [
    ('AN', 'Andaman and Nicobar Islands'), ('AP', 'Andhra Pradesh'),
    ('AR', 'Arunachal Pradesh'), ('AS', 'Assam'), ('BR', 'Bihar'),
    ('CH', 'Chandigarh'), ('CG', 'Chhattisgarh'), ('DN', 'Dadra and Nagar Haveli'),
    ('DD', 'Daman and Diu'), ('DL', 'Delhi'), ('GA', 'Goa'),
    ('GJ', 'Gujarat'), ('HR', 'Haryana'), ('HP', 'Himachal Pradesh'),
    ('JK', 'Jammu and Kashmir'), ('JH', 'Jharkhand'), ('KA', 'Karnataka'),
    ('KL', 'Kerala'), ('LA', 'Ladakh'), ('LD', 'Lakshadweep'),
    ('MP', 'Madhya Pradesh'), ('MH', 'Maharashtra'), ('MN', 'Manipur'),
    ('ML', 'Meghalaya'), ('MZ', 'Mizoram'), ('NL', 'Nagaland'),
    ('OR', 'Odisha'), ('PY', 'Puducherry'), ('PB', 'Punjab'),
    ('RJ', 'Rajasthan'), ('SK', 'Sikkim'), ('TN', 'Tamil Nadu'),
    ('TS', 'Telangana'), ('TR', 'Tripura'), ('UP', 'Uttar Pradesh'),
    ('UK', 'Uttarakhand'), ('WB', 'West Bengal'),
]


class HouseOwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    full_name = models.CharField(max_length=100)
    area = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=5, choices=STATE_CHOICES)
    # PRIVATE — never returned in public API responses
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    identity_type = models.CharField(max_length=50, blank=True,
                                     help_text="Type of ID provided (e.g. Voter ID, Passport). Number NOT stored.")
    preferred_language = models.CharField(max_length=5, default='en')
    profile_photo = models.ImageField(upload_to='owner_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'owner_profiles'

    def __str__(self):
        return f"{self.full_name} ({self.user.user_id})"

    def get_state_display_name(self):
        return dict(STATE_CHOICES).get(self.state, self.state)


# ---------------------------------------------------------------------------
# Government ID document metadata
# The actual file is stored in a PRIVATE Supabase Storage bucket.
# PostgreSQL stores ONLY path/metadata — never the binary file.
# ---------------------------------------------------------------------------

class OwnerDocument(models.Model):
    """
    Metadata for a government ID document uploaded during owner registration.

    The binary file lives in Supabase Storage bucket 'government-ids'.
    This model stores only the path and metadata required to retrieve it.
    """

    DOC_TYPE_CHOICES = [
        ('AADHAAR',          'Aadhaar Card'),
        ('PAN',              'PAN Card'),
        ('VOTER_ID',         'Voter ID'),
        ('DRIVING_LICENCE',  'Driving Licence'),
        ('PASSPORT',         'Passport'),
        ('OTHER',            'Other Government ID'),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ('PENDING',   'Pending Review'),
        ('VERIFIED',  'Verified'),
        ('REJECTED',  'Rejected'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owner_documents'
    )
    id_type = models.CharField(max_length=30, choices=DOC_TYPE_CHOICES)
    # Path inside the 'government-ids' Supabase Storage bucket
    # e.g. "HO-TN-XXXXX/a3f9b1c2d4e5.pdf"
    storage_path = models.CharField(max_length=500)
    original_filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='PENDING'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'owner_documents'

    def __str__(self):
        return f"{self.user.user_id} — {self.get_id_type_display()} ({self.verification_status})"
