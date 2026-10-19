"""
accounts/utils.py
ID generation and OTP utilities for CONNECT TO BUILD
"""
import random
import string
from django.utils import timezone
from datetime import timedelta


def generate_unique_id(role: str, state_code: str, model_class) -> str:
    """
    Generate a unique user ID.
    Format: HO-TN-XXXXX (Owner) or WK-TN-XXXXX (Worker)

    Args:
        role: 'OWNER' or 'WORKER'
        state_code: 2-letter state code e.g. 'TN'
        model_class: The User model class to check uniqueness against
    """
    prefix = 'HO' if role == 'OWNER' else 'WK'
    state = state_code.upper()[:2]
    chars = string.ascii_uppercase + string.digits

    for _ in range(100):  # Try up to 100 times to get unique ID
        code = ''.join(random.choices(chars, k=5))
        user_id = f"{prefix}-{state}-{code}"
        if not model_class.objects.filter(user_id=user_id).exists():
            return user_id

    # Fallback: use 8-char code
    code = ''.join(random.choices(chars, k=8))
    return f"{prefix}-{state}-{code}"


def generate_tracking_id(state_code: str, model_class=None) -> str:
    """
    Generate a unique application tracking ID for worker verification.
    Format: TRK-TN-XXXXX

    Args:
        state_code: 2-letter state code e.g. 'TN'
        model_class: The WorkerProfile model class to check uniqueness against
    """
    state = (state_code or 'IN').upper()[:2]
    chars = string.ascii_uppercase + string.digits

    for _ in range(100):
        code = ''.join(random.choices(chars, k=5))
        tracking_id = f"TRK-{state}-{code}"
        if model_class is not None:
            if not model_class.objects.filter(tracking_id=tracking_id).exists():
                return tracking_id
        else:
            return tracking_id

    code = ''.join(random.choices(chars, k=8))
    return f"TRK-{state}-{code}"


def generate_project_id(state_code: str, model_class) -> str:
    """
    Generate a unique project ID.
    Format: PRJ-TN-2024-XXXXX
    """
    from django.utils import timezone
    year = timezone.now().year
    state = state_code.upper()[:2]
    chars = string.ascii_uppercase + string.digits

    for _ in range(100):
        code = ''.join(random.choices(chars, k=5))
        project_id = f"PRJ-{state}-{year}-{code}"
        if not model_class.objects.filter(project_id=project_id).exists():
            return project_id

    code = ''.join(random.choices(chars, k=8))
    return f"PRJ-{state}-{year}-{code}"


def generate_otp() -> str:
    """Generate a 6-digit numeric OTP."""
    return str(random.randint(100000, 999999))


def get_state_code_from_name(state_name: str) -> str:
    """
    Convert state name to 2-letter code for ID generation.
    Returns 'IN' as fallback if state not found.
    """
    state_map = {
        'andaman and nicobar islands': 'AN', 'andhra pradesh': 'AP',
        'arunachal pradesh': 'AR', 'assam': 'AS', 'bihar': 'BR',
        'chandigarh': 'CH', 'chhattisgarh': 'CG', 'delhi': 'DL',
        'goa': 'GA', 'gujarat': 'GJ', 'haryana': 'HR',
        'himachal pradesh': 'HP', 'jammu and kashmir': 'JK',
        'jharkhand': 'JH', 'karnataka': 'KA', 'kerala': 'KL',
        'ladakh': 'LA', 'madhya pradesh': 'MP', 'maharashtra': 'MH',
        'manipur': 'MN', 'meghalaya': 'ML', 'mizoram': 'MZ',
        'nagaland': 'NL', 'odisha': 'OR', 'puducherry': 'PY',
        'punjab': 'PB', 'rajasthan': 'RJ', 'sikkim': 'SK',
        'tamil nadu': 'TN', 'telangana': 'TS', 'tripura': 'TR',
        'uttar pradesh': 'UP', 'uttarakhand': 'UK', 'west bengal': 'WB',
    }
    return state_map.get(state_name.lower().strip(), 'IN')
