from django.urls import path
from . import views

app_name = 'veterinary'

urlpatterns = [
    # Panel principal
    path('', views.veterinary_dashboard, name='dashboard'),
    
    # Gestión de registraciones
    path('registrations/', views.registration_list, name='registrations'),
    path('check/<int:registration_id>/', views.veterinary_check, name='check'),
    path('vaccinations/<int:registration_id>/', views.vaccination_record, name='vaccination_record'),
    
    # Gestión de alertas médicas
    path('alerts/', views.alert_list, name='alerts'),
    path('alert/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    path('create-alert/<int:check_id>/', views.create_alert, name='create_alert'),
    
    # Historial médico
    path('dog-history/<int:dog_id>/', views.medical_history, name='medical_history'),
    
    # Revisión de documentos
    path('document/<int:document_id>/', views.document_review, name='document_review'),
]