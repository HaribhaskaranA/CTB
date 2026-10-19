from django.urls import path
from . import views
from .views import owner_registration_send_otp, owner_registration_verify_otp
from workers.views import WorkerTrackStatusView

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing'),
    path('register/owner/', views.RegisterOwnerView.as_view(), name='register_owner'),
    path('register/owner/send-otp/', owner_registration_send_otp, name='register_owner_send_otp'),
    path('register/owner/verify-otp/', owner_registration_verify_otp, name='register_owner_verify_otp'),
    path('register/worker/', views.RegisterWorkerView.as_view(), name='register_worker'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-otp/', views.OTPVerifyView.as_view(), name='verify_otp'),
    path('otp-verify/', views.OTPVerifyView.as_view(), name='otp_verify'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.RoleDashboardRedirectView.as_view(), name='role_dashboard'),
    path('track-status/', WorkerTrackStatusView.as_view(), name='track_status'),
]
