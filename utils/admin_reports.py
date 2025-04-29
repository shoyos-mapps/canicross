"""
Utilidades para la generación de reportes administrativos en Canicross.
"""
import csv
from django.http import HttpResponse
from django.contrib import admin
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages

from participants.models import Participant, Dog
from veterinary.models import VeterinaryCheck
from registrations.models import Registration
from events.models import Event, Race

class ReportGeneratorView(TemplateView):
    """Vista base para la generación de reportes administrativos."""
    template_name = 'admin/reports/report_generator.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generador de Reportes'
        context['events'] = Event.objects.all().order_by('-start_date')
        return context
    
    def post(self, request, *args, **kwargs):
        report_type = request.POST.get('report_type')
        
        if report_type == 'participants_dogs':
            return self.generate_participants_dogs_report(request)
        elif report_type == 'veterinary_status':
            return self.generate_veterinary_status_report(request)
        elif report_type == 'event_registrations':
            return self.generate_event_registrations_report(request)
        elif report_type == 'payments':
            return self.generate_payments_report(request)
        else:
            messages.error(request, "Tipo de reporte no válido")
            return self.get(request, *args, **kwargs)
    
    def generate_participants_dogs_report(self, request):
        """Genera un reporte CSV con información de participantes y sus perros."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="participantes_perros_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Participante', 'Nombre', 'Apellidos', 'Documento', 'Email', 'Teléfono', 
            'Dirección', 'Ciudad', 'País', 'Contacto Emergencia', 'Teléfono Emergencia',
            'ID Perro', 'Nombre Perro', 'Raza', 'Microchip', 'Fecha Nacimiento', 'Sexo',
            'Estado Veterinario', 'Notas Veterinarias'
        ])
        
        # Obtener participantes, optimizando consultas
        participants = Participant.objects.all().prefetch_related('dogs', 'dogs__veterinary_checks')
        
        for participant in participants:
            # Si el participante no tiene perros, incluirlo con campos de perro vacíos
            if not participant.dogs.exists():
                writer.writerow([
                    participant.id, participant.first_name, participant.last_name, 
                    participant.id_document, participant.email, participant.phone,
                    participant.address, participant.city, participant.country,
                    participant.emergency_contact_name, participant.emergency_contact_phone,
                    '', '', '', '', '', '', '', ''
                ])
            else:
                # Para cada perro del participante
                for dog in participant.dogs.all():
                    # Obtener la revisión veterinaria más reciente
                    vet_check = VeterinaryCheck.objects.filter(dog=dog).order_by('-check_time').first()
                    
                    # Determinar estado veterinario y notas
                    vet_status = ''
                    vet_notes = ''
                    if vet_check:
                        vet_status = dict(VeterinaryCheck.CHECK_STATUS_CHOICES).get(vet_check.status, 'Sin revisión')
                        vet_notes = vet_check.general_notes
                    
                    writer.writerow([
                        participant.id, participant.first_name, participant.last_name, 
                        participant.id_document, participant.email, participant.phone,
                        participant.address, participant.city, participant.country,
                        participant.emergency_contact_name, participant.emergency_contact_phone,
                        dog.id, dog.name, dog.breed, dog.microchip_number, 
                        dog.date_of_birth, dict(Dog._meta.get_field('gender').choices).get(dog.gender, ''),
                        vet_status, vet_notes
                    ])
        
        return response
    
    def generate_veterinary_status_report(self, request):
        """Genera un reporte CSV con el estado veterinario de todos los perros."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="estado_veterinario_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Perro', 'Nombre Perro', 'Raza', 'Microchip', 
            'Propietario', 'Documento Propietario', 'Email Propietario',
            'Estado Veterinario', 'Fecha Revisión', 'Veterinario', 'Notas'
        ])
        
        # Filtrar por estado si se proporciona
        vet_status = request.POST.get('vet_status', '')
        
        # Obtener perros con sus propietarios
        dogs = Dog.objects.all().select_related('owner', 'owner__user')
        
        for dog in dogs:
            # Obtener la revisión veterinaria más reciente
            vet_check = VeterinaryCheck.objects.filter(dog=dog).order_by('-check_time').first()
            
            # Determinar estado veterinario
            status_display = 'Sin revisión'
            check_date = ''
            vet_name = ''
            notes = ''
            
            if vet_check:
                status_display = dict(VeterinaryCheck.CHECK_STATUS_CHOICES).get(vet_check.status, 'Sin revisión')
                check_date = vet_check.check_time.strftime('%d/%m/%Y %H:%M') if vet_check.check_time else ''
                vet_name = vet_check.veterinarian.get_full_name() if vet_check.veterinarian else ''
                notes = vet_check.general_notes
            
            # Filtrar por estado si se especificó
            if vet_status and vet_check:
                if vet_check.status != vet_status:
                    continue
            elif vet_status == 'no_check' and vet_check:
                continue
            elif vet_status and vet_status != 'no_check' and not vet_check:
                continue
                
            writer.writerow([
                dog.id, dog.name, dog.breed, dog.microchip_number,
                f"{dog.owner.first_name} {dog.owner.last_name}", dog.owner.id_document, dog.owner.email,
                status_display, check_date, vet_name, notes
            ])
        
        return response
    
    def generate_event_registrations_report(self, request):
        """Genera un reporte CSV con las inscripciones a un evento específico."""
        event_id = request.POST.get('event_id')
        
        try:
            event = Event.objects.get(id=event_id)
        except (Event.DoesNotExist, ValueError):
            messages.error(request, "Evento no válido")
            return self.get(request)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="inscripciones_{event.name.replace(" ", "_")}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Inscripción', 'Número Dorsal', 'Carrera', 'Categoría',
            'Participante', 'Documento', 'Email', 'Teléfono', 
            'Perro', 'Raza', 'Microchip', 
            'Estado Veterinario', 'Notas Veterinarias', 'Estado Inscripción',
            'Estado Pago', 'Importe Pagado', 'Fecha Pago', 'Método Pago', 'Referencia'
        ])
        
        # Obtener inscripciones para el evento
        registrations = Registration.objects.filter(
            race__event=event
        ).select_related(
            'participant', 'dog', 'race', 'race_category'
        ).prefetch_related(
            'dog__veterinary_checks'
        )
        
        for reg in registrations:
            # Obtener la revisión veterinaria más reciente para el perro
            vet_check = VeterinaryCheck.objects.filter(dog=reg.dog).order_by('-check_time').first()
            
            # Determinar estado veterinario
            vet_status = 'Sin revisión'
            vet_notes = ''
            
            if vet_check:
                vet_status = dict(VeterinaryCheck.CHECK_STATUS_CHOICES).get(vet_check.status, 'Sin revisión')
                vet_notes = vet_check.general_notes
            
            # Verificar que el campo status existe (puede ser registration_status en algunos casos)
            status_display = ''
            if hasattr(reg, 'status'):
                status_display = dict(Registration.REGISTRATION_STATUS_CHOICES).get(reg.status, '')
            elif hasattr(reg, 'registration_status'):
                status_display = dict(Registration.REGISTRATION_STATUS_CHOICES).get(reg.registration_status, '')
            
            # Datos de pago
            payment_status = dict(Registration.PAYMENT_STATUS_CHOICES).get(reg.payment_status, 'Pendiente')
            payment_amount = str(reg.payment_amount) if reg.payment_amount else '-'
            payment_date = reg.payment_date.strftime('%d/%m/%Y %H:%M') if reg.payment_date else '-'
            payment_method = reg.payment_method or '-'
            payment_reference = reg.payment_reference or '-'
                
            writer.writerow([
                reg.id, reg.bib_number, reg.race.name, reg.race_category.category.name,
                f"{reg.participant.first_name} {reg.participant.last_name}", reg.participant.id_document, reg.participant.email, reg.participant.phone,
                reg.dog.name, reg.dog.breed, reg.dog.microchip_number,
                vet_status, vet_notes, status_display,
                payment_status, payment_amount, payment_date, payment_method, payment_reference
            ])
        
        return response
        
    def generate_payments_report(self, request):
        """Genera un reporte CSV con el estado de pagos de inscripciones."""
        event_id = request.POST.get('event_id')
        payment_status = request.POST.get('payment_status', '')
        
        # Filtrar por evento si se proporciona
        registrations_query = Registration.objects.all()
        
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                registrations_query = registrations_query.filter(race__event=event)
                filename = f"pagos_{event.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            except (Event.DoesNotExist, ValueError):
                messages.error(request, "Evento no válido")
                return self.get(request)
        else:
            filename = f"pagos_todos_eventos_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        # Filtrar por estado de pago si se proporciona
        if payment_status:
            registrations_query = registrations_query.filter(payment_status=payment_status)
        
        # Optimizar consultas
        registrations = registrations_query.select_related(
            'participant', 'dog', 'race', 'race_category', 'participant__user'
        ).order_by('race__event', 'race', 'bib_number')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Inscripción', 'Evento', 'Carrera', 'Fecha Carrera', 'Categoría',
            'Número Dorsal', 'Participante', 'Documento', 'Email',
            'Estado Pago', 'Importe Pagado', 'Fecha Pago', 'Método Pago', 'Referencia',
            'Estado Inscripción', 'Perro'
        ])
        
        for reg in registrations:
            # Formatear datos de pago
            payment_status = dict(Registration.PAYMENT_STATUS_CHOICES).get(reg.payment_status, 'Pendiente')
            payment_amount = str(reg.payment_amount) if reg.payment_amount else '-'
            payment_date = reg.payment_date.strftime('%d/%m/%Y %H:%M') if reg.payment_date else '-'
            payment_method = reg.payment_method or '-'
            payment_reference = reg.payment_reference or '-'
            
            # Formatear fecha de carrera
            race_date = reg.race.date.strftime('%d/%m/%Y') if reg.race.date else '-'
            
            # Estado de inscripción
            registration_status = dict(Registration.REGISTRATION_STATUS_CHOICES).get(reg.registration_status, '-')
            
            writer.writerow([
                reg.id, reg.race.event.name, reg.race.name, race_date, reg.race_category.category.name,
                reg.bib_number, reg.participant.full_name, reg.participant.id_document, reg.participant.email,
                payment_status, payment_amount, payment_date, payment_method, payment_reference,
                registration_status, reg.dog.name
            ])
        
        return response

def get_admin_report_urls():
    """Devuelve las URLs para integrar en el sitio de administración."""
    reports_view = ReportGeneratorView.as_view()
    return [
        path('reports/', reports_view, name='admin_reports'),
        path('reports/participants/', reports_view, {'report_type': 'participants_dogs'}, name='reports_participants'),
        path('reports/veterinary/', reports_view, {'report_type': 'veterinary_status'}, name='reports_veterinary'),
        path('reports/events/', reports_view, {'report_type': 'event_registrations'}, name='reports_events'),
        path('reports/payments/', reports_view, {'report_type': 'payments'}, name='reports_payments'),
    ]