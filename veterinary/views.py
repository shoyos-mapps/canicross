from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse

from accounts.decorators import veterinary_required
from registrations.models import Registration, Document
from participants.models import Dog
from events.models import Event
from .models import VeterinaryCheck, VaccinationRecord, MedicalAlert

@login_required
@veterinary_required
def veterinary_dashboard(request):
    """
    Panel principal para veterinarios con resumen de revisiones pendientes y completadas.
    """
    # Filtrar eventos activos o próximos
    current_date = timezone.now().date()
    active_events = Event.objects.filter(
        Q(start_date__lte=current_date, end_date__gte=current_date) | 
        Q(start_date__gte=current_date)
    ).order_by('start_date')
    
    # Obtener evento seleccionado o usar el primero disponible
    selected_event_id = request.GET.get('event')
    if selected_event_id:
        selected_event = get_object_or_404(Event, id=selected_event_id)
    elif active_events.exists():
        selected_event = active_events.first()
    else:
        selected_event = None
    
    # Obtener estadísticas y revisiones pendientes
    stats = {
        'pending': 0,
        'approved': 0,
        'rejected': 0,
        'conditional': 0,
        'total': 0
    }
    
    pending_registrations = []
    recent_checks = []
    
    if selected_event:
        # Registros para el evento seleccionado
        registrations = Registration.objects.filter(
            race__event=selected_event
        ).select_related('participant', 'dog', 'race')
        
        # Obtener estadísticas
        stats['total'] = registrations.count()
        
        # Revisiones veterinarias existentes
        veterinary_checks = VeterinaryCheck.objects.filter(
            registration__race__event=selected_event
        )
        
        # Contar por estado
        status_counts = veterinary_checks.values('status').annotate(count=Count('status'))
        for status_count in status_counts:
            status = status_count['status']
            count = status_count['count']
            if status in stats:
                stats[status] = count
        
        # Marcar las que no tienen revisión como pendientes
        stats['pending'] = stats['total'] - (stats['approved'] + stats['rejected'] + stats['conditional'])
        
        # Obtener inscripciones pendientes de revisión
        registrations_with_checks = veterinary_checks.values_list('registration_id', flat=True)
        pending_registrations = registrations.exclude(
            id__in=registrations_with_checks
        ).order_by('race__start_time')[:10]
        
        # Revisiones recientes
        recent_checks = veterinary_checks.select_related(
            'dog', 'registration', 'veterinarian'
        ).order_by('-updated_at')[:5]
    
    # Alertas médicas pendientes
    active_alerts = MedicalAlert.objects.filter(
        status__in=['active', 'monitoring']
    ).select_related('veterinary_check__dog').order_by('-priority', '-created_at')[:5]
    
    context = {
        'active_events': active_events,
        'selected_event': selected_event,
        'stats': stats,
        'pending_registrations': pending_registrations,
        'recent_checks': recent_checks,
        'active_alerts': active_alerts,
    }
    
    return render(request, 'veterinary/dashboard.html', context)

@login_required
@veterinary_required
def registration_list(request):
    """
    Lista de registraciones para revisar, filtrable por evento y estado.
    """
    # Filtrar eventos activos o próximos
    current_date = timezone.now().date()
    active_events = Event.objects.filter(
        Q(start_date__lte=current_date, end_date__gte=current_date) | 
        Q(start_date__gte=current_date)
    ).order_by('start_date')
    
    # Obtener evento seleccionado o usar el primero disponible
    selected_event_id = request.GET.get('event')
    if selected_event_id:
        selected_event = get_object_or_404(Event, id=selected_event_id)
    elif active_events.exists():
        selected_event = active_events.first()
    else:
        selected_event = None
    
    # Filtro por estado de revisión
    check_status = request.GET.get('status', 'pending')
    
    registrations = []
    if selected_event:
        # Consulta base de registraciones para el evento
        registrations_query = Registration.objects.filter(
            race__event=selected_event
        ).select_related('participant', 'dog', 'race')
        
        if check_status == 'pending':
            # Registraciones sin revisión veterinaria
            vet_checks = VeterinaryCheck.objects.filter(
                registration__race__event=selected_event
            ).values_list('registration_id', flat=True)
            
            registrations = registrations_query.exclude(
                id__in=vet_checks
            )
        elif check_status == 'all':
            # Todas las registraciones
            registrations = registrations_query
        else:
            # Registraciones con un estado específico de revisión
            registrations = registrations_query.filter(
                veterinary_check__status=check_status
            )
    
    context = {
        'active_events': active_events,
        'selected_event': selected_event,
        'check_status': check_status,
        'registrations': registrations,
    }
    
    return render(request, 'veterinary/registration_list.html', context)

@login_required
@veterinary_required
def veterinary_check(request, registration_id):
    """
    Vista para realizar una revisión veterinaria completa.
    """
    registration = get_object_or_404(
        Registration.objects.select_related('participant', 'dog', 'race__event'),
        id=registration_id
    )
    
    # Verificar si ya existe una revisión para esta registración
    try:
        vet_check = VeterinaryCheck.objects.get(registration=registration)
        is_new = False
    except VeterinaryCheck.DoesNotExist:
        # Crear una nueva revisión
        vet_check = VeterinaryCheck(
            registration=registration,
            dog=registration.dog,
            veterinarian=request.user,
            status='in_progress'
        )
        vet_check.save()
        is_new = True
    
    # Documentos de vacunación
    vaccination_docs = Document.objects.filter(
        registration=registration,
        document_type='vaccination_record'
    )
    
    # Procesar el formulario
    if request.method == 'POST':
        with transaction.atomic():
            # Actualizar datos básicos
            vet_check.temperature = request.POST.get('temperature') or None
            vet_check.weight = request.POST.get('weight') or None
            vet_check.heart_rate = request.POST.get('heart_rate') or None
            
            # Evaluación física
            vet_check.physical_condition = request.POST.get('physical_condition') or None
            vet_check.hydration_status = request.POST.get('hydration_status') or None
            
            # Revisión de sistemas
            vet_check.has_injuries = 'has_injuries' in request.POST
            vet_check.injury_details = request.POST.get('injury_details', '')
            
            vet_check.has_respiratory_issues = 'has_respiratory_issues' in request.POST
            vet_check.respiratory_details = request.POST.get('respiratory_details', '')
            
            vet_check.has_musculoskeletal_issues = 'has_musculoskeletal_issues' in request.POST
            vet_check.musculoskeletal_details = request.POST.get('musculoskeletal_details', '')
            
            # Vacunas
            vet_check.vaccines_verified = 'vaccines_verified' in request.POST
            vet_check.vaccines_notes = request.POST.get('vaccines_notes', '')
            
            # Notas y recomendaciones
            vet_check.general_notes = request.POST.get('general_notes', '')
            vet_check.recommendations = request.POST.get('recommendations', '')
            
            # Estado final y timestamp
            vet_check.status = request.POST.get('status')
            vet_check.check_time = timezone.now()
            
            # Guardar revisión
            vet_check.save()
            
            # Actualizar estado en la registración
            registration.vet_check_status = 'approved' if vet_check.status == 'approved' else (
                'rejected' if vet_check.status == 'rejected' else 'pending'
            )
            registration.vet_check_time = vet_check.check_time
            registration.vet_checker_details = vet_check.general_notes
            registration.save()
            
            # Crear alerta médica si es necesario
            if request.POST.get('create_alert') == 'yes':
                alert = MedicalAlert(
                    veterinary_check=vet_check,
                    priority=request.POST.get('alert_priority', 'medium'),
                    description=request.POST.get('alert_description', ''),
                    requires_followup='requires_followup' in request.POST,
                    notify_staff='notify_staff' in request.POST,
                    created_by=request.user
                )
                alert.save()
            
            # Registrar vacunas verificadas
            # (Aquí iría código para procesar los registros de vacunación)
            
            messages.success(request, f"Revisión veterinaria de {registration.dog.name} completada con éxito.")
            
            # Redirección según el botón presionado
            if 'save_next' in request.POST:
                # Buscar la siguiente registración pendiente
                next_registration = Registration.objects.filter(
                    race__event=registration.race.event,
                    vet_check_status='pending'
                ).exclude(id=registration.id).first()
                
                if next_registration:
                    return redirect('veterinary:check', registration_id=next_registration.id)
            
            return redirect('veterinary:dashboard')
    
    context = {
        'registration': registration,
        'vet_check': vet_check,
        'is_new': is_new,
        'vaccination_docs': vaccination_docs,
        'condition_choices': VeterinaryCheck.CONDITION_CHOICES,
        'status_choices': VeterinaryCheck.CHECK_STATUS_CHOICES,
        'priority_choices': MedicalAlert.PRIORITY_CHOICES,
    }
    
    return render(request, 'veterinary/check_form.html', context)

@login_required
@veterinary_required
def alert_list(request):
    """
    Lista de alertas médicas que requieren atención o seguimiento.
    """
    # Filtrar por estado
    status_filter = request.GET.get('status', 'active')
    
    alerts = MedicalAlert.objects.select_related(
        'veterinary_check__dog', 
        'veterinary_check__registration__participant',
        'created_by'
    )
    
    if status_filter != 'all':
        if status_filter == 'active':
            # En activo incluimos tanto activas como en monitoreo
            alerts = alerts.filter(status__in=['active', 'monitoring'])
        else:
            alerts = alerts.filter(status=status_filter)
    
    # Ordenar por prioridad y fecha
    alerts = alerts.order_by('-priority', '-created_at')
    
    context = {
        'alerts': alerts,
        'status_filter': status_filter,
        'status_choices': MedicalAlert.STATUS_CHOICES,
    }
    
    return render(request, 'veterinary/alert_list.html', context)

@login_required
@veterinary_required
def alert_detail(request, alert_id):
    """
    Detalle de una alerta médica con opciones para actualizar su estado.
    """
    alert = get_object_or_404(
        MedicalAlert.objects.select_related(
            'veterinary_check__dog', 
            'veterinary_check__registration__participant',
            'created_by'
        ),
        id=alert_id
    )
    
    if request.method == 'POST':
        # Actualizar estado de la alerta
        new_status = request.POST.get('status')
        if new_status in dict(MedicalAlert.STATUS_CHOICES):
            alert.status = new_status
            
            # Añadir una nota si se proporciona
            note = request.POST.get('note', '').strip()
            if note:
                if alert.description:
                    alert.description += f"\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M')} - {request.user}] {note}"
                else:
                    alert.description = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')} - {request.user}] {note}"
            
            alert.save()
            messages.success(request, f"Estado de la alerta actualizado a {alert.get_status_display()}.")
            
            return redirect('veterinary:alert_list')
    
    context = {
        'alert': alert,
        'status_choices': MedicalAlert.STATUS_CHOICES,
    }
    
    return render(request, 'veterinary/alert_detail.html', context)

@login_required
@veterinary_required
def medical_history(request, dog_id):
    """
    Historial médico completo de un perro.
    """
    dog = get_object_or_404(Dog.objects.select_related('owner'), id=dog_id)
    
    # Obtener todas las revisiones veterinarias para este perro
    checks = VeterinaryCheck.objects.filter(dog=dog).order_by('-check_time')
    
    # Obtener todas las alertas médicas para este perro
    alerts = MedicalAlert.objects.filter(
        veterinary_check__dog=dog
    ).order_by('-created_at')
    
    context = {
        'dog': dog,
        'checks': checks,
        'alerts': alerts,
    }
    
    return render(request, 'veterinary/medical_history.html', context)

@login_required
@veterinary_required
def vaccination_record(request, registration_id):
    """
    Gestión de registros de vacunación para una inscripción.
    """
    registration = get_object_or_404(
        Registration.objects.select_related('dog', 'participant'),
        id=registration_id
    )
    
    # Obtener o crear la revisión veterinaria
    vet_check, created = VeterinaryCheck.objects.get_or_create(
        registration=registration,
        defaults={
            'dog': registration.dog,
            'veterinarian': request.user,
            'status': 'in_progress'
        }
    )
    
    # Obtener registros de vacunación existentes
    vaccination_records = VaccinationRecord.objects.filter(
        veterinary_check=vet_check
    ).order_by('-administration_date')
    
    if request.method == 'POST':
        if 'add_vaccine' in request.POST:
            # Añadir una nueva vacuna
            vaccine_name = request.POST.get('vaccine_name')
            administration_date = request.POST.get('administration_date')
            
            if vaccine_name and administration_date:
                VaccinationRecord.objects.create(
                    veterinary_check=vet_check,
                    vaccine_name=vaccine_name,
                    administration_date=administration_date,
                    expiry_date=request.POST.get('expiry_date') or None,
                    batch_number=request.POST.get('batch_number', ''),
                    verified=True,
                    notes=request.POST.get('notes', '')
                )
                
                messages.success(request, f"Vacuna {vaccine_name} añadida correctamente.")
                return redirect('veterinary:vaccination_record', registration_id=registration.id)
        
        elif 'delete_vaccine' in request.POST:
            # Eliminar una vacuna existente
            vaccine_id = request.POST.get('vaccine_id')
            try:
                vaccine = VaccinationRecord.objects.get(id=vaccine_id, veterinary_check=vet_check)
                vaccine_name = vaccine.vaccine_name
                vaccine.delete()
                messages.success(request, f"Vacuna {vaccine_name} eliminada correctamente.")
            except VaccinationRecord.DoesNotExist:
                messages.error(request, "La vacuna solicitada no existe.")
            
            return redirect('veterinary:vaccination_record', registration_id=registration.id)
    
    context = {
        'registration': registration,
        'vet_check': vet_check,
        'vaccination_records': vaccination_records,
    }
    
    return render(request, 'veterinary/vaccination_record.html', context)

@login_required
@veterinary_required
def create_alert(request, check_id):
    """
    Crear una nueva alerta médica desde una revisión veterinaria.
    """
    vet_check = get_object_or_404(VeterinaryCheck, id=check_id)
    
    if request.method == 'POST':
        priority = request.POST.get('priority')
        description = request.POST.get('description')
        
        if priority and description:
            alert = MedicalAlert.objects.create(
                veterinary_check=vet_check,
                priority=priority,
                description=description,
                requires_followup='requires_followup' in request.POST,
                notify_staff='notify_staff' in request.POST,
                created_by=request.user
            )
            
            messages.success(request, f"Alerta médica creada para {vet_check.dog.name}.")
            
            # Redirigir según el botón presionado
            if 'save_view' in request.POST:
                return redirect('veterinary:alert_detail', alert_id=alert.id)
                
            return redirect('veterinary:medical_history', dog_id=vet_check.dog.id)
    
    context = {
        'vet_check': vet_check,
        'priority_choices': MedicalAlert.PRIORITY_CHOICES,
    }
    
    return render(request, 'veterinary/create_alert.html', context)

@login_required
@veterinary_required
def document_review(request, document_id):
    """
    Revisar un documento específico (como un certificado de vacunación).
    """
    document = get_object_or_404(
        Document.objects.select_related('registration__dog', 'registration__participant'),
        id=document_id
    )
    
    # Buscar la revisión veterinaria asociada
    try:
        vet_check = VeterinaryCheck.objects.get(registration=document.registration)
    except VeterinaryCheck.DoesNotExist:
        vet_check = None
    
    context = {
        'document': document,
        'vet_check': vet_check,
    }
    
    return render(request, 'veterinary/document_review.html', context)
