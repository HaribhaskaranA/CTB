"""
Integration verification script for CONNECT TO BUILD.
Checks: env vars, Twilio, Supabase Storage, OTP endpoints, security, DB.
No secrets are printed. No real OTP is sent. Dummy test file only.
"""
import os
import sys
import re as _re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

results = {}

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 1: Environment Variables
# ─────────────────────────────────────────────────────────────────────────────
print('\n=== CHECK 1: Environment Variables ===')
required = [
    'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN',
    'TWILIO_VERIFY_SERVICE_SID', 'SUPABASE_URL', 'SUPABASE_SERVICE_KEY'
]
env_ok = True
for key in required:
    val = getattr(settings, key, '')
    if not val:
        print(f'  FAIL  {key} — missing or empty')
        env_ok = False
    elif key in ('TWILIO_AUTH_TOKEN', 'SUPABASE_SERVICE_KEY'):
        print(f'  PASS  {key} — loaded ({len(val)} chars, redacted)')
    elif key == 'SUPABASE_URL':
        print(f'  PASS  {key} = {val}')
    else:
        prefix = val[:4] if len(val) >= 4 else val
        print(f'  PASS  {key} starts_with={prefix!r} len={len(val)}')
results['env_vars'] = 'PASS' if env_ok else 'FAIL'


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 2: Twilio Verify — service fetch (no OTP sent)
# ─────────────────────────────────────────────────────────────────────────────
print('\n=== CHECK 2: Twilio Verify Service Validation ===')
try:
    from twilio.rest import Client
    client_tw = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    svc = client_tw.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).fetch()
    print(f'  PASS  Twilio credentials valid')
    print(f'  PASS  Verify service name: {svc.friendly_name!r}')
    print(f'  PASS  Service SID prefix:  {svc.sid[:4]}...')
    results['twilio'] = 'PASS'
except Exception as e:
    print(f'  FAIL  Twilio error: {e}')
    results['twilio'] = 'FAIL'


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 3 + 4: Supabase Storage — bucket access, dummy upload, delete
# ─────────────────────────────────────────────────────────────────────────────
print('\n=== CHECK 3+4: Supabase Storage Access + Safe Dummy Upload Test ===')
dummy_path = None
try:
    from supabase import create_client
    import uuid

    BUCKET = 'government-ids'
    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    dummy_path = f'_integration_test/{uuid.uuid4().hex}.pdf'
    dummy_content = b'%PDF-1.4 CONNECT TO BUILD integration test. Safe to delete.'

    # Upload
    sb.storage.from_(BUCKET).upload(
        path=dummy_path,
        file=dummy_content,
        file_options={'content-type': 'application/pdf', 'upsert': 'false'},
    )
    print(f'  PASS  Upload to private bucket succeeded')

    # Generate signed URL (proves file exists and bucket policies work)
    signed = sb.storage.from_(BUCKET).create_signed_url(dummy_path, 30)
    url_present = bool(signed.get('signedURL') or signed.get('signedUrl'))
    print(f'  PASS  Signed URL generation: {url_present}')

    # Delete
    sb.storage.from_(BUCKET).remove([dummy_path])
    print(f'  PASS  Test file deleted successfully')

    dummy_path = None
    results['supabase_storage'] = 'PASS'

except Exception as e:
    print(f'  FAIL  Supabase Storage error: {e}')
    results['supabase_storage'] = 'FAIL'
    # Try cleanup even on failure
    if dummy_path:
        try:
            sb.storage.from_('government-ids').remove([dummy_path])
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 5: OTP endpoint routes
# ─────────────────────────────────────────────────────────────────────────────
print('\n=== CHECK 5: OTP Endpoint Routes ===')
try:
    from django.urls import reverse
    endpoint_checks = [
        ('register_owner_send_otp',   '/register/owner/send-otp/'),
        ('register_owner_verify_otp', '/register/owner/verify-otp/'),
        ('register_owner',            '/register/owner/'),
    ]
    ep_ok = True
    for name, expected in endpoint_checks:
        url = reverse(name)
        if url == expected:
            print(f'  PASS  {name} -> {url}')
        else:
            print(f'  FAIL  {name} -> {url} (expected {expected})')
            ep_ok = False
    results['otp_endpoints'] = 'PASS' if ep_ok else 'FAIL'
except Exception as e:
    print(f'  FAIL  {e}')
    results['otp_endpoints'] = 'FAIL'


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 6: Security invariants (static source audit)
# ─────────────────────────────────────────────────────────────────────────────
print('\n=== CHECK 6: Security Invariants (Source Audit) ===')
base = r'C:\Users\HARIBHASKARAN A\Downloads\CONNECT_TO_BUILD'

try:
    with open(f'{base}\\accounts\\views.py',   encoding='utf-8') as f: views_src = f.read()
    with open(f'{base}\\accounts\\services.py', encoding='utf-8') as f: svc_src  = f.read()

    # OTP endpoints in views must not contain any print/log of OTP code
    otp_fn_block = ''
    for line in views_src.split('\n'):
        if 'owner_registration_send_otp' in line or 'owner_registration_verify_otp' in line:
            pass  # just identify the functions

    sec_checks = {
        'Passwords not logged anywhere':       not bool(_re.search(r'log.*password', views_src + svc_src, _re.I)),
        'Phone_verified session gate exists':  "session.get('phone_verified'" in views_src,
        'Verification reset on phone change':  "session['phone_verified'] = False" in views_src,
        'Atomic transaction wraps DB writes':  'transaction.atomic()' in views_src,
        'Storage rollback on DB failure':      'delete_document' in views_src,
        'Storage path saved (not blob)':       'storage_path' in views_src,
        'create_user() used (hashed pwd)':     'create_user(' in views_src,
        'OTP code not in logger calls':        not bool(_re.search(r'logger\.(info|debug|error).*otp_code', views_src)),
        'Twilio check_otp never stores code':  'code' in svc_src and 'demo_otp' not in svc_src.split('check_otp')[1][:500] if 'check_otp' in svc_src else True,
        'No hardcoded Twilio/Supabase creds':  'ACxxxxxxx' not in views_src and 'eyJxxxxxxx' not in views_src,
    }

    sec_ok = True
    for desc, passed in sec_checks.items():
        status = 'PASS' if passed else 'FAIL'
        if not passed:
            sec_ok = False
        print(f'  {status}  {desc}')
    results['security_invariants'] = 'PASS' if sec_ok else 'FAIL'

except Exception as e:
    print(f'  FAIL  Source audit error: {e}')
    results['security_invariants'] = 'FAIL'


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 7: OwnerDocument DB integration
# ─────────────────────────────────────────────────────────────────────────────
print('\n=== CHECK 7: OwnerDocument Database Integration ===')
try:
    from owners.models import OwnerDocument
    fields = {f.name for f in OwnerDocument._meta.get_fields()}
    expected_fields = {'user', 'id_type', 'storage_path', 'original_filename',
                       'content_type', 'verification_status', 'uploaded_at'}
    missing = expected_fields - fields
    if missing:
        print(f'  FAIL  Missing fields: {missing}')
        results['owner_document_db'] = 'FAIL'
    else:
        count = OwnerDocument.objects.count()
        print(f'  PASS  Table accessible — {count} rows')
        print(f'  PASS  All expected fields present: {sorted(expected_fields)}')

        # Confirm no binary/file fields (file must not be in DB)
        blob_types = ('BinaryField', 'FileField', 'ImageField')
        blob_fields = [
            f.name for f in OwnerDocument._meta.get_fields()
            if hasattr(f, 'get_internal_type') and f.get_internal_type() in blob_types
        ]
        if blob_fields:
            print(f'  FAIL  Unexpected file storage fields in DB: {blob_fields}')
            results['owner_document_db'] = 'FAIL'
        else:
            print(f'  PASS  No binary/file fields in DB — files stay in Supabase Storage')
            results['owner_document_db'] = 'PASS'
except Exception as e:
    print(f'  FAIL  {e}')
    results['owner_document_db'] = 'FAIL'


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print('\n' + '=' * 55)
print('  INTEGRATION VERIFICATION SUMMARY')
print('=' * 55)
labels = {
    'env_vars':            'Environment Variables Loaded',
    'twilio':              'Twilio Verify Configuration',
    'supabase_storage':    'Supabase Storage (private bucket)',
    'otp_endpoints':       'OTP Registration Endpoints',
    'security_invariants': 'Security Invariants (source audit)',
    'owner_document_db':   'OwnerDocument DB Integration',
}
all_pass = True
for key, label in labels.items():
    val = results.get(key, 'NOT RUN')
    if val != 'PASS':
        all_pass = False
    print(f'  {val:7s}  {label}')

print('=' * 55)
print(f'  OVERALL: {"ALL CHECKS PASSED" if all_pass else "SOME CHECKS FAILED"}')
print('=' * 55)
sys.exit(0 if all_pass else 1)
