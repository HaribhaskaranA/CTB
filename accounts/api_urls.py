"""accounts/api_urls.py — REST API routes for auth"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('register/owner/', api_views.APIRegisterOwner.as_view(), name='api_register_owner'),
    path('register/worker/', api_views.APIRegisterWorker.as_view(), name='api_register_worker'),
    path('login/', api_views.APILogin.as_view(), name='api_login'),
    path('verify-otp/', api_views.APIVerifyOTP.as_view(), name='api_verify_otp'),
    path('logout/', api_views.APILogout.as_view(), name='api_logout'),
    path('me/', api_views.APICurrentUser.as_view(), name='api_current_user'),
]
