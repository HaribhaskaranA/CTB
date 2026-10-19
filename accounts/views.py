"""
accounts/views.py
Authentication views: Registration, Login, OTP, Dashboard redirect

Registration flow (owner):
  1. GET  /register/owner/          — show form
  2. POST /register/owner/send-otp/ — send Twilio Verify SMS, store phone in session
  3. POST /register/owner/verify-otp/ — check OTP with Twilio, set session flag
  4. POST /register/owner/          — final submit; blocked if phone not verified
"""
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.db import transaction
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .models import User, OTPRecord
from .utils import generate_unique_id, generate_otp, get_state_code_from_name, generate_tracking_id
from .services import get_sms_verify_service, get_otp_service, SupabaseStorageService
from owners.models import HouseOwnerProfile, OwnerDocument
from workers.models import WorkerProfile

logger = logging.getLogger(__name__)

# Language display name → Django language code
_LANG_NAME_TO_CODE = {
    'english': 'en', 'tamil': 'ta', 'telugu': 'te',
    'kannada': 'kn', 'malayalam': 'ml', 'hindi': 'hi',
}

# Allowed government ID file types (extension + MIME)
_ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
_ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'application/pdf',
}
_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# OTP resend cooldown in seconds
_OTP_RESEND_COOLDOWN = 60

# Document type value from HTML form → model choice
_ID_TYPE_MAP = {
    'Aadhaar':          'AADHAAR',
    'PAN Card':         'PAN',
    'Voter ID':         'VOTER_ID',
    'Driving License':  'DRIVING_LICENCE',
    'Passport':         'PASSPORT',
    'Other':            'OTHER',
}


class LandingView(TemplateView):
    """Public landing page."""
    template_name = 'landing.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('role_dashboard')
        return super().get(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Owner Registration — Step: Send OTP (AJAX endpoint)
# ---------------------------------------------------------------------------

def _normalize_phone_e164(phone: str) -> str:
    """
    Convert Indian 10-digit phone to E.164 format (+91XXXXXXXXXX).
    Accepts: '9876543210', '09876543210', '+919876543210'
    """
    phone = phone.strip().replace(' ', '').replace('-', '')
    if phone.startswith('+91'):
        return phone
    if phone.startswith('91') and len(phone) == 12:
        return '+' + phone
    if phone.startswith('0') and len(phone) == 11:
        return '+91' + phone[1:]
    if len(phone) == 10:
        return '+91' + phone
    return '+91' + phone  # best effort


def owner_registration_send_otp(request):
    """
    POST /register/owner/send-otp/
    Sends a real SMS OTP via Twilio Verify.
    Rate-limited: 1 request per _OTP_RESEND_COOLDOWN seconds.
    Returns JSON — called by frontend JavaScript.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed.'}, status=405)

    import time

    phone_raw = request.POST.get('phone', '').strip()
    if not phone_raw or len(phone_raw) < 10:
        return JsonResponse({'success': False, 'error': 'Please enter a valid 10-digit phone number.'})

    # Rate limiting: check last send time in session
    last_sent = request.session.get('otp_last_sent', 0)
    elapsed = time.time() - last_sent
    if elapsed < _OTP_RESEND_COOLDOWN:
        wait = int(_OTP_RESEND_COOLDOWN - elapsed)
        return JsonResponse({
            'success': False,
            'error': f'Please wait {wait} seconds before requesting another OTP.',
        })

    # Check if this phone is already registered
    if User.objects.filter(phone_number=phone_raw).exists():
        return JsonResponse({
            'success': False,
            'error': 'This phone number is already registered. Please login instead.',
        })

    phone_e164 = _normalize_phone_e164(phone_raw)

    # Reset any previous verification for this session
    request.session['phone_verified'] = False
    request.session['verified_phone'] = ''

    from django.conf import settings

    try:
        svc = get_sms_verify_service()
        result = svc.send_otp(phone_e164)
    except RuntimeError as exc:
        logger.error("send_otp: service config error: %s", exc)
        return JsonResponse({'success': False, 'error': 'SMS service not configured.'})

    if not result.get('success'):
        raw_err = result.get('error', '')
        logger.warning("Twilio send_otp failed for %s: %s", phone_e164, raw_err)

        # If in DEMO_MODE, provide a fallback demo OTP so testing is never blocked
        if getattr(settings, 'DEMO_MODE', False):
            demo_code = generate_otp()
            request.session['demo_reg_otp'] = demo_code
            request.session['otp_phone_raw'] = phone_raw
            request.session['otp_phone_e164'] = phone_e164
            request.session['otp_last_sent'] = time.time()
            request.session.modified = True
            logger.info("DEMO_MODE active: fallback OTP generated for phone %s", phone_raw)
            return JsonResponse({
                'success': True,
                'demo_mode': True,
                'demo_otp': demo_code,
                'message': f"Demo Mode: Twilio Trial unverified number. Your OTP is: {demo_code}",
            })
        else:
            if 'verified tester' in raw_err.lower() or 'unverified' in raw_err.lower():
                err_msg = (
                    "Twilio Free Trial restriction: In Twilio Trial accounts, SMS can only be sent to "
                    "Verified Caller IDs. Please add your phone number in Twilio Console "
                    "or enable DEMO_MODE."
                )
            else:
                err_msg = f"SMS failed: {raw_err}" if raw_err else "Failed to send OTP. Please check your phone number."
            return JsonResponse({'success': False, 'error': err_msg})

    # Store phone (raw + E.164) and timestamp in session
    request.session.pop('demo_reg_otp', None)
    request.session['otp_phone_raw'] = phone_raw
    request.session['otp_phone_e164'] = phone_e164
    request.session['otp_last_sent'] = time.time()
    request.session.modified = True

    logger.info("OTP send initiated via Twilio for phone ending ...%s", phone_raw[-4:])
    return JsonResponse({'success': True, 'message': 'OTP sent to your phone via SMS.'})


def owner_registration_verify_otp(request):
    """
    POST /register/owner/verify-otp/
    Checks submitted OTP against Twilio Verify.
    Returns JSON — called by frontend JavaScript.
    Never logs or stores the OTP code.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed.'}, status=405)

    code = request.POST.get('otp_code', '').strip()
    phone_e164 = request.session.get('otp_phone_e164', '')
    phone_raw = request.session.get('otp_phone_raw', '')

    if not code or not phone_e164:
        return JsonResponse({
            'success': False,
            'error': 'Session expired. Please request a new OTP.',
        })

    if len(code) != 6 or not code.isdigit():
        return JsonResponse({'success': False, 'error': 'Please enter the 6-digit OTP.'})

    # Check demo fallback OTP if active
    demo_code = request.session.get('demo_reg_otp')
    if demo_code and code == demo_code:
        request.session['phone_verified'] = True
        request.session['verified_phone'] = phone_raw
        request.session.pop('demo_reg_otp', None)
        request.session.modified = True
        logger.info("Phone verified via DEMO OTP for number ending ...%s", phone_raw[-4:])
        return JsonResponse({'success': True, 'message': 'Phone number verified (Demo Mode)'})

    try:
        svc = get_sms_verify_service()
        result = svc.check_otp(phone_e164, code)
    except RuntimeError as exc:
        logger.error("verify_otp: service config error: %s", exc)
        return JsonResponse({'success': False, 'error': 'Verification service unavailable.'})

    if result.get('verified'):
        # Mark this phone as verified in the session
        request.session['phone_verified'] = True
        request.session['verified_phone'] = phone_raw
        request.session.modified = True
        logger.info("Phone verified for number ending ...%s", phone_raw[-4:])
        return JsonResponse({'success': True, 'message': 'Phone number verified'})
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'OTP is incorrect or has expired.'),
        })


# ---------------------------------------------------------------------------
# Owner Registration — Main view (GET form + POST final submit)
# ---------------------------------------------------------------------------

class RegisterOwnerView(View):
    """
    House Owner registration.

    GET:  Display the registration form.
    POST: Final registration submission.
          Blocked if phone_verified != True in session.
          Uploads government ID to Supabase Storage.
          Creates User + HouseOwnerProfile + OwnerDocument atomically.
    """
    template_name = 'auth/register_owner.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('role_dashboard')
        return render(request, self.template_name)

    def post(self, request):
        data = request.POST

        # ── Read field names as posted by the HTML template ──
        full_name = data.get('full_name', '').strip()
        phone     = data.get('phone', '').strip()
        email     = data.get('email', '').strip()
        language  = data.get('language', 'English').strip()
        state_val = data.get('state', '').strip()
        city      = data.get('city', '').strip()
        area      = data.get('area', '').strip()
        address   = data.get('address', '').strip()
        id_type   = data.get('id_type', '').strip()
        password  = data.get('password', '').strip()

        errors = {}

        # ── GATE 1: Phone must be verified via OTP ──
        session_verified = request.session.get('phone_verified', False)
        verified_phone   = request.session.get('verified_phone', '')

        if not session_verified:
            errors['phone'] = 'Phone number must be verified before registration.'
        elif verified_phone and phone and phone != verified_phone:
            # User changed the phone number after verifying a different one
            errors['phone'] = 'Phone number changed after OTP verification. Please verify the new number.'
            request.session['phone_verified'] = False
            request.session['verified_phone'] = ''

        # ── Required field validation ──
        if not full_name:
            errors['full_name'] = 'Full Name is required.'
        if not phone:
            errors['phone'] = errors.get('phone', 'Phone Number is required.')
        if not city:
            errors['city'] = 'City is required.'
        if not state_val:
            errors['state'] = 'Please select your state.'
        if not password:
            errors['password'] = 'Password is required.'

        # Phone uniqueness (extra safety)
        if phone and not errors.get('phone') and User.objects.filter(phone_number=phone).exists():
            errors['phone'] = 'This phone number is already registered.'

        # Email uniqueness (optional field)
        if email and User.objects.filter(email=email).exists():
            errors['email'] = 'This email is already registered.'

        # ── GATE 2: Government ID document validation ──
        doc_file = request.FILES.get('id_document')
        if doc_file:
            import os
            ext = os.path.splitext(doc_file.name)[1].lower()
            if ext not in _ALLOWED_EXTENSIONS:
                errors['id_document'] = 'Invalid file type. Allowed: JPG, PNG, PDF.'
            elif doc_file.content_type not in _ALLOWED_MIME_TYPES:
                errors['id_document'] = 'Invalid file type detected. Allowed: JPG, PNG, PDF.'
            elif doc_file.size > _MAX_FILE_SIZE:
                errors['id_document'] = 'File too large. Maximum 5 MB allowed.'

        if errors:
            logger.debug("RegisterOwnerView POST validation failed: %s", list(errors.keys()))
            return render(request, self.template_name, {'errors': errors, 'data': data})

        # ── Resolve state and language codes ──
        state_code = state_val.upper() if len(state_val) == 2 else get_state_code_from_name(state_val)
        lang_code  = _LANG_NAME_TO_CODE.get(language.lower(), 'en')

        # Generate unique user ID
        user_id = generate_unique_id('OWNER', state_code, User)

        # ── Upload document to Supabase Storage BEFORE DB transaction ──
        storage_path = None
        if doc_file:
            doc_file.seek(0)
            file_bytes = doc_file.read()
            try:
                storage_svc = SupabaseStorageService()
                upload_result = storage_svc.upload_document(
                    user_id=user_id,
                    file_name=doc_file.name,
                    file_bytes=file_bytes,
                    content_type=doc_file.content_type,
                )
            except RuntimeError as exc:
                logger.error("Supabase Storage not configured: %s", exc)
                return render(request, self.template_name, {
                    'errors': {'id_document': 'Document storage service not available. Please try again.'},
                    'data': data,
                })

            if not upload_result.get('success'):
                return render(request, self.template_name, {
                    'errors': {'id_document': 'Document upload failed. Please try again.'},
                    'data': data,
                })
            storage_path = upload_result['path']

        # ── DB transaction: create User + Profile + Document atomically ──
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=user_id,
                    password=password,
                    email=email or '',
                    role='OWNER',
                    phone_number=phone,
                    user_id=user_id,
                    preferred_language=lang_code,
                    is_phone_verified=True,  # verified via Twilio before reaching here
                )
                name_parts = full_name.split()
                user.first_name = name_parts[0] if name_parts else ''
                user.last_name  = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                user.save(update_fields=['first_name', 'last_name'])

                HouseOwnerProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    area=area,
                    city=city,
                    state=state_code,
                    address=address,
                    phone_number=phone,
                    email=email or '',
                    identity_type=id_type,
                    preferred_language=lang_code,
                )

                if storage_path and doc_file:
                    doc_type_code = _ID_TYPE_MAP.get(id_type, 'OTHER')
                    OwnerDocument.objects.create(
                        user=user,
                        id_type=doc_type_code,
                        storage_path=storage_path,
                        original_filename=doc_file.name,
                        content_type=doc_file.content_type,
                    )

                logger.info(
                    "RegisterOwnerView: created owner user_id=%s pk=%s city=%s doc_uploaded=%s",
                    user_id, user.pk, city, bool(storage_path)
                )

        except Exception as exc:
            logger.error("RegisterOwnerView: DB error: %s", exc, exc_info=True)
            # If DB creation fails AFTER upload, clean up the orphaned storage object
            if storage_path:
                try:
                    storage_svc = SupabaseStorageService()
                    storage_svc.delete_document(storage_path)
                    logger.info("Cleaned up orphaned document: %s", storage_path)
                except Exception:
                    pass
            return render(request, self.template_name, {
                'errors': {'general': 'Registration failed due to a server error. Please try again.'},
                'data': data,
            })

        # Clear OTP session state
        for key in ['phone_verified', 'verified_phone', 'otp_phone_e164',
                    'otp_phone_raw', 'otp_last_sent']:
            request.session.pop(key, None)

        return render(request, 'auth/register_success.html', {
            'user_id': user_id,
            'role': 'Owner',
            'name': full_name,
        })


# ---------------------------------------------------------------------------
# Worker Registration (unchanged from working version)
# ---------------------------------------------------------------------------

class RegisterWorkerView(View):
    template_name = 'auth/register_worker.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('role_dashboard')
        return render(request, self.template_name)

    def post(self, request):
        data = request.POST
        errors = {}

        phone = (data.get('phone') or data.get('phone_number') or '').strip()
        required = ['full_name', 'profession', 'city', 'state', 'password']
        for field in required:
            if not data.get(field, '').strip():
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        if not phone:
            errors['phone'] = 'Phone number is required.'

        if phone and User.objects.filter(phone_number=phone).exists():
            errors['phone'] = 'This phone number is already registered. Please log in.'

        email = data.get('email', '').strip()
        if email and User.objects.filter(email=email).exists():
            errors['email'] = 'This email is already registered.'

        if errors:
            return render(request, self.template_name, {'errors': errors, 'data': data})

        state_val = data.get('state', 'TN').strip()
        state_code = state_val.upper() if len(state_val) == 2 else get_state_code_from_name(state_val)
        user_id = generate_unique_id('WORKER', state_code, User)
        tracking_id = generate_tracking_id(state_code, WorkerProfile)

        raw_exp = data.get('years_experience') or data.get('experience') or 0
        try:
            years_experience = int(raw_exp)
        except (ValueError, TypeError):
            years_experience = 0

        raw_rate = data.get('daily_rate') or 0
        try:
            daily_rate = float(raw_rate)
        except (ValueError, TypeError):
            daily_rate = 0.0

        lang = data.get('preferred_language') or data.get('language') or 'en'
        lang_code = _LANG_NAME_TO_CODE.get(lang.lower(), lang.lower()) if 'lang' in locals() else 'en'

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=user_id,
                    password=data['password'],
                    email=email,
                    role='WORKER',
                    phone_number=phone,
                    user_id=user_id,
                    preferred_language=lang_code,
                )
                name_parts = data.get('full_name', '').strip().split()
                user.first_name = name_parts[0] if name_parts else ''
                user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                user.save()

                skills_raw = data.get('skills', '')
                skills = [s.strip() for s in skills_raw.split(',') if s.strip()]
                service_areas_raw = data.get('service_areas', '')
                service_areas = [s.strip() for s in service_areas_raw.split(',') if s.strip()]

                worker_profile = WorkerProfile.objects.create(
                    user=user,
                    full_name=data.get('full_name', '').strip(),
                    profession=data.get('profession', 'OTHER').upper(),
                    bio=data.get('bio', '').strip(),
                    skills=skills,
                    years_experience=years_experience,
                    service_areas=service_areas,
                    daily_rate=daily_rate,
                    city=data.get('city', '').strip(),
                    state=state_code,
                    area=data.get('area', '').strip(),
                    phone_number=phone,
                    email=email,
                    address=data.get('address', '').strip(),
                    identity_type=data.get('id_type') or data.get('identity_type', ''),
                    preferred_language=lang_code,
                    verification_status='PENDING',
                    tracking_id=tracking_id,
                )

                # Process uploaded documents if present
                for doc_file in request.FILES.getlist('documents'):
                    from workers.models import WorkerCertificate
                    WorkerCertificate.objects.create(
                        worker=worker_profile,
                        certificate_name=doc_file.name,
                        issuing_authority='Uploaded by applicant',
                        document=doc_file,
                        is_verified=False,
                    )

                logger.info(
                    "RegisterWorkerView: created worker user_id=%s tracking_id=%s pk=%s",
                    user_id, tracking_id, user.pk
                )

        except Exception as exc:
            logger.error("RegisterWorkerView: DB error: %s", exc, exc_info=True)
            return render(request, self.template_name, {
                'errors': {'general': f'Registration failed: {str(exc)}'},
                'data': data,
            })

        request.session['worker_tracking_id'] = tracking_id

        return render(request, 'auth/register_worker_success.html', {
            'tracking_id': tracking_id,
            'name': data.get('full_name', ''),
            'profession': worker_profile.get_profession_display(),
            'city': data.get('city', ''),
        })


# ---------------------------------------------------------------------------
# Login / OTP / Dashboard / Logout
# ---------------------------------------------------------------------------

class LoginView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('role_dashboard')
        return render(request, self.template_name, {'data': {}})

    def post(self, request):
        """Step 1: Validate ID + phone, send demo OTP."""
        data = request.POST
        user_id = data.get('user_id', '').strip().upper()
        phone = (data.get('phone') or data.get('phone_number') or '').strip()
        role = data.get('role', '').strip()

        if not user_id or not phone or not role:
            return render(request, self.template_name, {
                'error': 'Please fill all fields.', 'data': data,
            })

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return render(request, self.template_name, {
                'error': 'Invalid User ID. Please check and try again.', 'data': data,
            })

        role_upper = role.upper()
        expected_role = 'OWNER' if role_upper in ('OWNER', 'HOUSE OWNER') else 'WORKER'
        if user.role != expected_role:
            return render(request, self.template_name, {
                'error': f'Role does not match the User ID. User is registered as {user.get_role_display()}.', 'data': data,
            })

        if user.role == 'WORKER':
            worker_profile = getattr(user, 'worker_profile', None)
            if worker_profile and worker_profile.verification_status != 'VERIFIED':
                tracking_id = worker_profile.tracking_id or ''
                return render(request, self.template_name, {
                    'error': (
                        f"Your worker application is currently {worker_profile.get_verification_status_display().lower()}. "
                        "You can only log in after your application has been verified by the administrator."
                    ),
                    'unverified_worker': True,
                    'tracking_id': tracking_id,
                    'data': data,
                })

        clean_input_phone = phone.replace(' ', '').replace('-', '').replace('+91', '')
        clean_user_phone = (user.phone_number or '').replace(' ', '').replace('-', '').replace('+91', '')
        if clean_input_phone[-10:] != clean_user_phone[-10:]:
            return render(request, self.template_name, {
                'error': 'Phone number does not match our records for this User ID.', 'data': data,
            })

        otp_code = generate_otp()
        otp_record = OTPRecord.create_for_user(user, otp_code)
        otp_service = get_otp_service()
        otp_result = otp_service.send_otp(user, otp_code)

        request.session['otp_user_id'] = user.pk
        request.session['otp_pending'] = True

        return render(request, 'auth/otp_verify.html', {
            'user_id': user_id,
            'phone': phone,
            'demo_otp': otp_result.get('demo_otp', ''),
            'demo_mode': True,
            'masked_phone': f"XXXX-XX{phone[-4:]}" if len(phone) >= 4 else "XXXXXX",
        })




class OTPVerifyView(View):
    """Step 2: Verify login OTP and log user in."""
    template_name = 'auth/otp_verify.html'

    def post(self, request):
        otp_entered = request.POST.get('otp', '').strip()
        user_pk = request.session.get('otp_user_id')

        if not user_pk or not otp_entered:
            messages.error(request, 'Invalid session. Please log in again.')
            return redirect('login')

        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return redirect('login')

        otp_record = OTPRecord.objects.filter(
            user=user, is_used=False
        ).order_by('-created_at').first()

        if not otp_record:
            return render(request, self.template_name, {
                'error': 'OTP has expired. Please log in again.',
            })

        if otp_record.verify(otp_entered):
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            user.is_phone_verified = True
            user.save(update_fields=['is_phone_verified'])
            request.session.pop('otp_user_id', None)
            request.session.pop('otp_pending', None)
            messages.success(request, f'Welcome back, {user.get_display_name()}!')
            if user.role == 'OWNER':
                return redirect('owner_dashboard')
            elif user.role == 'WORKER':
                return redirect('worker_dashboard')
            return redirect('role_dashboard')
        else:
            remaining = 5 - otp_record.attempt_count
            return render(request, self.template_name, {
                'error': f'Incorrect OTP. {max(0, remaining)} attempts remaining.',
                'user_id': user.user_id,
                'demo_otp': otp_record.demo_otp_plain,
                'demo_mode': True,
            })


class RoleDashboardRedirectView(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.role == 'OWNER':
            return redirect('owner_dashboard')
        elif request.user.role == 'WORKER':
            return redirect('worker_dashboard')
        else:
            return redirect('/django-admin/')


class LogoutView(View):
    def post(self, request):
        auth_logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('landing')

    def get(self, request):
        auth_logout(request)
        return redirect('landing')
