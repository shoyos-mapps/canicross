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
            # Secciones principales (apps)
            'Events': 'Eventos',
            'Participants': 'Participantes',
            'Registrations': 'Inscripciones',
            'Authentication and Authorization': 'Autenticación y Autorización',
            'Accounts': 'Cuentas',
            'Api': 'API',
            'Results': 'Resultados',
            'Checkin': 'Control de Acceso',
            'Kits': 'Equipamiento',
            'Race_Management': 'Gestión de Carreras',
            'Veterinary': 'Control Veterinario',
            'Auth': 'Autenticación',
            
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
            'Results': 'Resultados',
            'Veterinary checks': 'Revisiones Veterinarias',
            'Vaccination records': 'Registros de Vacunación',
            'Medical alerts': 'Alertas Médicas',
            'Race results': 'Resultados de Carreras',
            'Penalties': 'Penalizaciones',
        }
        
        # Aplicar traducciones
        for app in app_list:
            app['name'] = translations.get(app['name'], app['name'])
            for model in app['models']:
                model['name'] = translations.get(model['name'], model['name'])
                
        return app_list
    
    def get_urls(self):
        urls = super().get_urls()
        from utils.admin_reports import get_admin_report_urls
        
        # Obtener las URLs para reportes y envolverlas en admin_view para seguridad
        report_urls = []
        for url_pattern in get_admin_report_urls():
            # Crear un nuevo patrón con admin_view aplicado a la vista
            wrapped_view = self.admin_view(url_pattern.callback)
            report_urls.append(
                path(url_pattern.pattern._route, wrapped_view, name=url_pattern.name)
            )
        
        custom_urls = [
            path('logs/', self.admin_view(self.log_viewer), name='logs'),
            path('payment/list/', self.admin_view(self.payment_list), name='payment_list'),
            path('payment/update/<int:registration_id>/', self.admin_view(self.payment_update), name='payment_update'),
            path('payment/bulk-update/', self.admin_view(self.payment_bulk_update), name='payment_bulk_update'),
            # Agregar las URLs para generación de reportes
            *report_urls,
        ]
        return custom_urls + urls
    
    def log_viewer(self, request):
        """Redirige a la vista de logs."""
        return HttpResponseRedirect(f"/admin/auth/permission/logs/")
    
    def payment_list(self, request):
        """Redirige a la vista de lista de pagos."""
        return HttpResponseRedirect('/registrations/')
    
    def payment_update(self, request, registration_id):
        """Redirige a la vista de actualización de pago."""
        return HttpResponseRedirect(f'/registrations/payment/update/{registration_id}/')
    
    def payment_bulk_update(self, request):
        """Redirige a la vista de actualización masiva de pagos."""
        return HttpResponseRedirect('/registrations/payment/bulk-update/')

# Importar modelos de eventos
from events.models import Event, Modality, Race, Category, RaceCategory, PenaltyType
from events.admin import EventAdmin, ModalityAdmin, RaceAdmin, CategoryAdmin, RaceCategoryAdmin, PenaltyTypeAdmin

# Instanciar sitio admin
canicross_admin = CanicrossAdminSite(name='canicross_admin')

# Configurar LogViewerAdmin 
# Nota: Ya no registramos Group para este propósito, usaremos un modelo temporal distinto
from django.contrib.auth.models import Permission, Group
LogViewerAdmin.model = Permission
canicross_admin.register([Permission], LogViewerAdmin)

# Registrar Grupo con nuestro admin personalizado
from accounts.admin import CustomGroupAdmin
canicross_admin.register(Group, CustomGroupAdmin)

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
# Importar admins veterinarios
from participants.admin_veterinary import ParticipantVeterinaryAdmin, DogVeterinaryAdmin

# Registrar modelos de participantes en admin general
canicross_admin.register(Participant, ParticipantAdmin)
canicross_admin.register(Dog, DogAdmin)

# Crear un sitio admin específico para veterinarios
from django.contrib.admin import AdminSite
veterinary_admin = AdminSite(name='veterinary_admin')
veterinary_admin.site_header = 'Administración de Control Veterinario'
veterinary_admin.site_title = 'Control Veterinario'
veterinary_admin.index_title = 'Panel de Control Veterinario'

# Registrar solo lo necesario para veterinarios
veterinary_admin.register(Participant, ParticipantVeterinaryAdmin)
veterinary_admin.register(Dog, DogVeterinaryAdmin)

# Importar modelos de registraciones
from registrations.models import Registration, Document, ParticipantAnnotation
from registrations.admin import RegistrationAdmin, DocumentAdmin, ParticipantAnnotationAdmin

# Registrar modelos de registraciones
canicross_admin.register(Registration, RegistrationAdmin)
canicross_admin.register(Document, DocumentAdmin)
canicross_admin.register(ParticipantAnnotation, ParticipantAnnotationAdmin)