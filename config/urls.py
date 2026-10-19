"""
CONNECT TO BUILD — Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Django admin
    path('django-admin/', admin.site.urls),

    # Landing page
    path('', include('accounts.urls')),

    # App URLs
    path('owner/', include('owners.urls')),
    path('owners/', include('owners.urls')),
    path('worker/', include('workers.urls')),
    path('workers/', include('workers.urls')),
    path('projects/', include('projects.urls')),
    path('payments/', include('payments.urls')),
    path('complaints/', include('complaints.urls')),

    # REST API endpoints
    path('api/auth/', include('accounts.api_urls')),
    path('api/owners/', include('owners.api_urls')),
    path('api/workers/', include('workers.api_urls')),
    path('api/projects/', include('projects.api_urls')),
    path('api/quotations/', include('quotations.api_urls')),
    path('api/payments/', include('payments.api_urls')),
    path('api/complaints/', include('complaints.api_urls')),
    path('api/compliance/', include('compliance.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "CONNECT TO BUILD — Admin"
admin.site.site_title = "CTB Admin"
admin.site.index_title = "Construction Ecosystem Management"
