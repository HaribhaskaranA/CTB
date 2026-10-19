from django.urls import path
from .api_views import OwnerMeView

urlpatterns = [
    path('me/', OwnerMeView.as_view(), name='api_owner_me'),
]
