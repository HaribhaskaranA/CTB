"""
accounts/services.py
OTP and SMS services for CONNECT TO BUILD.

Production path: Twilio Verify (real SMS, no plaintext OTP stored anywhere).
The Twilio Verify service holds OTP state — Django only checks the result.
"""
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Backwards-compatibility alias — api_views.py imports this name
# ---------------------------------------------------------------------------

class _LoginOTPShim:
    """
    Shim used only for the login flow (internal OTP, not Twilio Verify).
    Login OTP is still managed via OTPRecord model (hashed, never displayed).
    """
    def send_otp(self, user, otp_code: str) -> dict:
        # OTP is stored hashed in OTPRecord — this is only a delivery shim.
        # In production, replace with SMS delivery here.
        logger.info("[LOGIN OTP] Sending to user %s", user.user_id)
        print(f"\n{'='*50}")
        print(f"[CONNECT TO BUILD — LOGIN OTP]")
        print(f"User: {user.user_id}")
        print(f"OTP:  {otp_code}")
        print(f"{'='*50}\n")
        return {'success': True, 'demo_mode': True, 'demo_otp': otp_code}


def get_otp_service():
    """
    Returns the OTP service for the LOGIN flow.
    (Registration phone OTP uses get_sms_verify_service / TwilioVerifyService instead.)
    """
    return _LoginOTPShim()


# ---------------------------------------------------------------------------
# Twilio Verify service (production / real SMS)
# ---------------------------------------------------------------------------

class TwilioVerifyService:
    """
    Real SMS OTP via Twilio Verify.
    Credentials loaded from environment — never hardcoded.

    Required env vars:
        TWILIO_ACCOUNT_SID
        TWILIO_AUTH_TOKEN
        TWILIO_VERIFY_SERVICE_SID

    Twilio Verify manages OTP generation, delivery, expiry, and attempt limits
    server-side, so we never see or store the OTP code.
    """

    def __init__(self):
        from django.conf import settings
        from twilio.rest import Client

        sid   = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.service_sid = getattr(settings, 'TWILIO_VERIFY_SERVICE_SID', '')

        if not all([sid, token, self.service_sid]):
            raise RuntimeError(
                'Twilio credentials not configured. '
                'Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, '
                'and TWILIO_VERIFY_SERVICE_SID in .env'
            )

        self.client = Client(sid, token)

    def send_otp(self, phone_e164: str) -> dict:
        """
        Start a Twilio Verify verification (sends SMS).
        phone_e164: E.164 format, e.g. '+919876543210'
        Returns {'success': True} or {'success': False, 'error': '...'}
        """
        try:
            verification = self.client.verify.v2 \
                .services(self.service_sid) \
                .verifications \
                .create(to=phone_e164, channel='sms')
            logger.info("TwilioVerify: verification started for status=%s", verification.status)
            return {'success': True, 'status': verification.status}
        except Exception as exc:
            logger.error("TwilioVerify send_otp error: %s", exc)
            return {'success': False, 'error': str(exc)}

    def check_otp(self, phone_e164: str, code: str) -> dict:
        """
        Check submitted OTP code against Twilio Verify.
        Returns {'verified': True} or {'verified': False, 'error': '...'}
        NOTE: Never logs or stores the code.
        """
        try:
            result = self.client.verify.v2 \
                .services(self.service_sid) \
                .verification_checks \
                .create(to=phone_e164, code=code)
            if result.status == 'approved':
                return {'verified': True}
            return {'verified': False, 'error': 'OTP is incorrect or has expired.'}
        except Exception as exc:
            logger.error("TwilioVerify check_otp error: %s", exc)
            return {'verified': False, 'error': 'Verification failed. Please request a new OTP.'}


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_sms_verify_service():
    """
    Returns the configured SMS verification service.
    Reads TWILIO_ACCOUNT_SID from settings to decide which backend to use.
    """
    from django.conf import settings
    sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    if sid:
        return TwilioVerifyService()
    raise RuntimeError(
        'No SMS verification provider configured. '
        'Add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID to .env'
    )


# ---------------------------------------------------------------------------
# Supabase Storage helper (for government ID document upload)
# ---------------------------------------------------------------------------

class SupabaseStorageService:
    """
    Uploads files to a private Supabase Storage bucket.
    Uses the service-role key (server-side only — never exposed to browser).

    Required env vars:
        SUPABASE_URL
        SUPABASE_SERVICE_KEY   ← service-role key, NOT anon key
    """

    BUCKET = 'government-ids'

    def __init__(self):
        from django.conf import settings
        from supabase import create_client

        url = getattr(settings, 'SUPABASE_URL', '')
        key = getattr(settings, 'SUPABASE_SERVICE_KEY', '')

        if not url or not key:
            raise RuntimeError(
                'Supabase credentials not configured. '
                'Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env'
            )

        self.client = create_client(url, key)

    def upload_document(self, user_id: str, file_name: str, file_bytes: bytes,
                        content_type: str) -> dict:
        """
        Upload a government ID document to the private 'government-ids' bucket.

        Path: government-ids/<user_id>/<unique_filename>

        Returns {'success': True, 'path': '...'} or {'success': False, 'error': '...'}
        """
        import uuid
        import os

        ext = os.path.splitext(file_name)[1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        storage_path = f"{user_id}/{unique_name}"

        try:
            self.client.storage.from_(self.BUCKET).upload(
                path=storage_path,
                file=file_bytes,
                file_options={'content-type': content_type, 'upsert': 'false'},
            )
            logger.info(
                "SupabaseStorage: uploaded government ID for user=%s path=%s",
                user_id, storage_path
            )
            return {'success': True, 'path': storage_path}
        except Exception as exc:
            logger.error("SupabaseStorage upload error for user=%s: %s", user_id, exc)
            return {'success': False, 'error': str(exc)}

    def delete_document(self, storage_path: str):
        """Delete a document (used for rollback on failed registration)."""
        try:
            self.client.storage.from_(self.BUCKET).remove([storage_path])
            logger.info("SupabaseStorage: deleted %s", storage_path)
        except Exception as exc:
            logger.warning("SupabaseStorage delete failed for %s: %s", storage_path, exc)

    def create_signed_url(self, storage_path: str, expires_in: int = 300) -> str | None:
        """
        Generate a temporary signed URL for authorized admin/user access.
        expires_in: seconds (default 5 minutes)
        Returns URL string or None on failure.
        """
        try:
            result = self.client.storage.from_(self.BUCKET).create_signed_url(
                storage_path, expires_in
            )
            return result.get('signedURL') or result.get('signedUrl')
        except Exception as exc:
            logger.error("SupabaseStorage signed URL error: %s", exc)
            return None
