"""
accounts/api_views.py
REST API views for authentication
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login as auth_login, logout as auth_logout

from .models import User, OTPRecord
from .utils import generate_unique_id, generate_otp, get_state_code_from_name
from .services import get_otp_service
from owners.models import HouseOwnerProfile
from workers.models import WorkerProfile


class APIRegisterOwner(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        errors = {}

        phone = data.get('phone_number', '').strip()
        email = data.get('email', '').strip()

        if not data.get('full_name'):
            errors['full_name'] = 'Full name is required.'
        if not phone:
            errors['phone_number'] = 'Phone number is required.'
        elif User.objects.filter(phone_number=phone).exists():
            errors['phone_number'] = 'Phone number already registered.'
        if not email:
            errors['email'] = 'Email is required.'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered.'
        if not data.get('password'):
            errors['password'] = 'Password is required.'
        if not data.get('state'):
            errors['state'] = 'State is required.'

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        state_code = get_state_code_from_name(data.get('state', ''))
        user_id = generate_unique_id('OWNER', state_code, User)

        user = User.objects.create_user(
            username=user_id,
            password=data['password'],
            email=email,
            role='OWNER',
            phone_number=phone,
            user_id=user_id,
            preferred_language=data.get('preferred_language', 'en'),
        )

        HouseOwnerProfile.objects.create(
            user=user,
            full_name=data.get('full_name', ''),
            area=data.get('area', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            address=data.get('address', ''),
            phone_number=phone,
            email=email,
            identity_type=data.get('identity_type', ''),
            preferred_language=data.get('preferred_language', 'en'),
        )

        return Response({
            'success': True,
            'user_id': user_id,
            'message': f'Registration successful. Your Owner ID is {user_id}',
            'role': 'OWNER',
        }, status=status.HTTP_201_CREATED)


class APIRegisterWorker(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        errors = {}

        phone = data.get('phone_number', '').strip()
        email = data.get('email', '').strip()

        if not data.get('full_name'):
            errors['full_name'] = 'Full name is required.'
        if not phone:
            errors['phone_number'] = 'Phone number is required.'
        elif User.objects.filter(phone_number=phone).exists():
            errors['phone_number'] = 'Phone number already registered.'
        if not email:
            errors['email'] = 'Email is required.'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered.'
        if not data.get('profession'):
            errors['profession'] = 'Profession is required.'
        if not data.get('state'):
            errors['state'] = 'State is required.'

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        state_code = get_state_code_from_name(data.get('state', ''))
        user_id = generate_unique_id('WORKER', state_code, User)

        user = User.objects.create_user(
            username=user_id,
            password=data.get('password', 'Demo@1234'),
            email=email,
            role='WORKER',
            phone_number=phone,
            user_id=user_id,
            preferred_language=data.get('preferred_language', 'en'),
        )

        skills = data.get('skills', [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]
        service_areas = data.get('service_areas', [])
        if isinstance(service_areas, str):
            service_areas = [s.strip() for s in service_areas.split(',') if s.strip()]

        WorkerProfile.objects.create(
            user=user,
            full_name=data.get('full_name', ''),
            profession=data.get('profession', 'OTHER'),
            bio=data.get('bio', ''),
            skills=skills,
            years_experience=int(data.get('years_experience', 0) or 0),
            service_areas=service_areas,
            daily_rate=float(data.get('daily_rate', 0) or 0),
            city=data.get('city', ''),
            state=state_code,
            area=data.get('area', ''),
            phone_number=phone,
            email=email,
            address=data.get('address', ''),
            identity_type=data.get('identity_type', ''),
            preferred_language=data.get('preferred_language', 'en'),
        )

        return Response({
            'success': True,
            'user_id': user_id,
            'message': f'Registration successful. Your Worker ID is {user_id}',
            'role': 'WORKER',
            'verification_status': 'PENDING',
        }, status=status.HTTP_201_CREATED)


class APILogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id', '').strip().upper()
        phone = request.data.get('phone_number', '').strip()
        role = request.data.get('role', '').strip().upper()

        if not user_id or not phone:
            return Response(
                {'error': 'User ID and phone number are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid User ID.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if role and user.role != role:
            return Response(
                {'error': 'Role does not match User ID.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.phone_number != phone:
            return Response(
                {'error': 'Phone number does not match records.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_code = generate_otp()
        OTPRecord.create_for_user(user, otp_code)
        otp_service = get_otp_service()
        result = otp_service.send_otp(user, otp_code)

        request.session['otp_user_id'] = user.pk

        return Response({
            'success': True,
            'message': 'OTP sent.',
            'demo_mode': result.get('demo_mode', True),
            'demo_otp': result.get('demo_otp', ''),  # Only in demo mode
            'user_id': user_id,
        })


class APIVerifyOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp_entered = request.data.get('otp', '').strip()
        user_pk = request.session.get('otp_user_id')

        if not user_pk:
            return Response({'error': 'No active OTP session.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response({'error': 'Invalid session.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_record = OTPRecord.objects.filter(
            user=user, is_used=False
        ).order_by('-created_at').first()

        if not otp_record or otp_record.is_expired():
            return Response({'error': 'OTP expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.verify(otp_entered):
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            user.is_phone_verified = True
            user.save(update_fields=['is_phone_verified'])
            request.session.pop('otp_user_id', None)
            return Response({
                'success': True,
                'role': user.role,
                'user_id': user.user_id,
                'redirect': '/owner/dashboard/' if user.role == 'OWNER' else '/worker/dashboard/',
            })
        else:
            remaining = max(0, 5 - otp_record.attempt_count)
            return Response(
                {'error': f'Incorrect OTP. {remaining} attempts remaining.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class APILogout(APIView):
    def post(self, request):
        auth_logout(request)
        return Response({'success': True, 'message': 'Logged out.'})


class APICurrentUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'user_id': user.user_id,
            'role': user.role,
            'preferred_language': user.preferred_language,
            'is_phone_verified': user.is_phone_verified,
        }
        if user.role == 'OWNER' and hasattr(user, 'owner_profile'):
            p = user.owner_profile
            data['name'] = p.full_name
            data['city'] = p.city
            data['state'] = p.state
        elif user.role == 'WORKER' and hasattr(user, 'worker_profile'):
            p = user.worker_profile
            data['name'] = p.full_name
            data['profession'] = p.profession
            data['verification_status'] = p.verification_status
        return Response(data)
