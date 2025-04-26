"""
Configuración personalizada del admin para Canicross.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect

# Admin personalizada para logs
from utils.admin import LogViewerAdmin

class CanicrossAdminSite(admin.AdminSite):
    """
    Sitio de administración personalizado para Canicross.
    """
    site_header = 'Administración de Canicross'
    site_title = 'Canicross Admin'
    index_title = 'Panel de Administración'
    
    # Traducciones de modelos al español
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        
        # Diccionario de traducciones
        translations = {
            # Secciones principales
            'Events': 'Eventos',
            'Participants': 'Participantes',
            'Registrations': 'Inscripciones',
            'Authentication and Authorization': 'Autenticación y Autorización',
            
            # Modelos específicos
            'Events': 'Eventos',
            'Modalities': 'Modalidades',
            'Races': 'Carreras',
            'Categories': 'Categorías',
            'Race categories': 'Categorías de Carrera',
            'Penalty types': 'Tipos de Penalización',
            'Participants': 'Participantes',
            'Dogs': 'Perros',
            'Registrations': 'Inscripciones',
            'Documents': 'Documentos',
            'Participant annotations': 'Anotaciones de Participantes',
            'Users': 'Usuarios',
            'Groups': 'Grupos',
        }
        
        # Aplicar traducciones
        for app in app_list:
            app['name'] = translations.get(app['name'], app['name'])
            for model in app['models']:
                model['name'] = translations.get(model['name'], model['name'])
                
        return app_list
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('logs/', self.admin_view(self.log_viewer), name='logs'),
        ]
        return custom_urls + urls
    
    def log_viewer(self, request):
        """Redirige a la vista de logs."""
        return HttpResponseRedirect(reverse('admin:log-viewer'))

# Importar modelos de eventos
from events.models import Event, Modality, Race, Category, RaceCategory, PenaltyType
from events.admin import EventAdmin, ModalityAdmin, RaceAdmin, CategoryAdmin, RaceCategoryAdmin, PenaltyTypeAdmin

# Instanciar sitio admin
canicross_admin = CanicrossAdminSite(name='canicross_admin')

# Registrar LogViewerAdmin para gestionar logs
# Usamos un modelo temporal para nuestra vista de admin
from django.contrib.auth.models import Group
LogViewerAdmin.model = Group
canicross_admin.register([Group], LogViewerAdmin)

# Registrar modelos de eventos en el admin personalizado
canicross_admin.register(Event, EventAdmin)
canicross_admin.register(Modality, ModalityAdmin)
canicross_admin.register(Race, RaceAdmin)
canicross_admin.register(Category, CategoryAdmin)
canicross_admin.register(RaceCategory, RaceCategoryAdmin)
canicross_admin.register(PenaltyType, PenaltyTypeAdmin)

# Importar modelos de participantes
from participants.models import Participant, Dog
from participants.admin import ParticipantAdmin, DogAdmin

# Registrar modelos de participantes
canicross_admin.register(Participant, ParticipantAdmin)
canicross_admin.register(Dog, DogAdmin)

# Importar modelos de registraciones
from registrations.models import Registration, Document, ParticipantAnnotation
from registrations.admin import RegistrationAdmin, DocumentAdmin, ParticipantAnnotationAdmin

# Registrar modelos de registraciones
canicross_admin.register(Registration, RegistrationAdmin)
canicross_admin.register(Document, DocumentAdmin)
canicross_admin.register(ParticipantAnnotation, ParticipantAnnotationAdmin)

# Registrar auth models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
canicross_admin.register(User, UserAdmin)