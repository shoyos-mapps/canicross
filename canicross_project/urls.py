"""
URL configuration for canicross_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls

# Importar admin personalizado
from .admin import canicross_admin

urlpatterns = [
    path('admin/', canicross_admin.urls),
    
    # API endpoints
    path('api/v1/', include('api.urls')),
    
    # API documentation
    path('api/docs/', include_docs_urls(title='Canicross API')),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('events/', include('events.urls')),
    path('participants/', include('participants.urls')),
    path('registrations/', include('registrations.urls')),
    path('veterinary/', include('veterinary.urls')),
    path('kits/', include('kits.urls')),
    path('checkin/', include('checkin.urls')),
    path('race-management/', include('race_management.urls')),
    path('results/', include('results.urls')),
    
    # Home page - usar un namespace diferente para evitar conflicto
    path('', include('events.urls', namespace='events_home')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)