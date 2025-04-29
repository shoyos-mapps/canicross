from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Registration, Document, ParticipantAnnotation
from events.models import Event, Race
from accounts.decorators import staff_required, admin_required
from utils.logger import log_function_call

@login_required
def registration_form(request):
    """Vista para el formulario de inscripción."""
    return render(request, 'registrations/registration_form.html')

@login_required
def registration_confirmation(request, registration_id):
    """Vista para la confirmación de inscripción."""
    registration = get_object_or_404(Registration, id=registration_id)
    
    # Verificar que el usuario sea el dueño de la inscripción o un administrador
    if request.user != registration.participant.user and not (request.user.is_admin() or request.user.is_staff_member()):
        raise PermissionDenied("No tienes permiso para ver esta inscripción.")
    
    return render(request, 'registrations/registration_confirmation.html', {
        'registration': registration
    })

@login_required
@staff_required
@log_function_call
def update_payment_status(request, registration_id):
    """
    Vista para actualizar el estado de pago de una inscripción.
    Solo disponible para administradores y personal de staff.
    """
    registration = get_object_or_404(Registration, id=registration_id)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        payment_status = request.POST.get('payment_status')
        payment_amount = request.POST.get('payment_amount')
        payment_method = request.POST.get('payment_method')
        payment_reference = request.POST.get('payment_reference', '')
        notes = request.POST.get('notes', '')
        
        # Actualizar el registro
        registration.payment_status = payment_status
        registration.payment_amount = payment_amount
        registration.payment_method = payment_method
        registration.payment_reference = payment_reference
        
        # Si el estado es "paid", registrar la fecha de pago
        if payment_status == 'paid' and not registration.payment_date:
            registration.payment_date = timezone.now()
            
        # Actualizar notas si se proporcionaron
        if notes:
            registration.notes = notes
            
        registration.save()
        
        messages.success(request, f'Estado de pago actualizado correctamente para {registration.participant}')
        return redirect('registrations:update_payment', registration_id=registration.id)
    
    # Para solicitudes GET, mostrar el formulario
    return render(request, 'registrations/update_payment.html', {
        'registration': registration,
        'payment_status_choices': Registration.PAYMENT_STATUS_CHOICES
    })

@login_required
@staff_required
@log_function_call
def bulk_update_payment_status(request):
    """
    Vista para actualizar el estado de pago de múltiples inscripciones a la vez.
    Solo disponible para administradores y personal de staff.
    """
    # Obtener la carrera (si se especifica)
    race_id = request.GET.get('race_id')
    race = None
    registrations = []
    
    if race_id:
        race = get_object_or_404(Race, id=race_id)
        registrations = Registration.objects.filter(race=race).select_related(
            'participant', 'dog', 'race', 'race_category'
        ).order_by('bib_number')
    
    if request.method == 'POST':
        # Obtener datos del formulario
        selected_registrations = request.POST.getlist('selected_registrations')
        payment_status = request.POST.get('payment_status')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes', '')
        
        # Verificar que se hayan seleccionado inscripciones
        if not selected_registrations:
            messages.error(request, 'Debe seleccionar al menos una inscripción para actualizar.')
            return redirect(request.path_info)
        
        # Para cada inscripción seleccionada
        update_count = 0
        for reg_id in selected_registrations:
            try:
                registration = Registration.objects.get(id=reg_id)
                
                # Obtener el importe específico para esta inscripción
                amount_key = f'amount_{reg_id}'
                payment_amount = request.POST.get(amount_key, '')
                
                # Actualizar el registro
                registration.payment_status = payment_status
                registration.payment_method = payment_method
                
                # Solo actualizar el importe si se proporcionó uno válido
                if payment_amount:
                    registration.payment_amount = payment_amount
                
                # Si el estado es "paid", registrar la fecha de pago
                if payment_status == 'paid' and not registration.payment_date:
                    registration.payment_date = timezone.now()
                
                # Actualizar notas si se proporcionaron
                if notes:
                    if registration.notes:
                        registration.notes += f"\n{notes}"
                    else:
                        registration.notes = notes
                
                registration.save()
                update_count += 1
                
            except Registration.DoesNotExist:
                continue
        
        messages.success(request, f'Se actualizaron {update_count} inscripciones correctamente.')
        
        # Redireccionar a la misma página con los mismos parámetros
        if race_id:
            return redirect(f'{reverse("registrations:bulk_update_payment")}?race_id={race_id}')
        return redirect('registrations:bulk_update_payment')
    
    # Para solicitudes GET, mostrar el formulario
    return render(request, 'registrations/bulk_update_payment.html', {
        'race': race,
        'registrations': registrations,
        'payment_status_choices': Registration.PAYMENT_STATUS_CHOICES
    })

@login_required
@staff_required
def registration_list(request):
    """
    Lista de inscripciones con filtros por evento, carrera, estado de pago, etc.
    Solo disponible para administradores y personal de staff.
    """
    # Inicializar variables para filtros
    selected_event = request.GET.get('event')
    selected_race = request.GET.get('race')
    selected_payment_status = request.GET.get('payment_status')
    query = request.GET.get('q', '')
    
    # Base query con relaciones
    registrations = Registration.objects.select_related(
        'participant', 'dog', 'race', 'race_category'
    ).order_by('race', 'bib_number')
    
    # Aplicar filtros
    if selected_event:
        registrations = registrations.filter(race__event_id=selected_event)
    
    if selected_race:
        registrations = registrations.filter(race_id=selected_race)
    
    if selected_payment_status:
        registrations = registrations.filter(payment_status=selected_payment_status)
    
    if query:
        registrations = registrations.filter(
            Q(participant__first_name__icontains=query) |
            Q(participant__last_name__icontains=query) |
            Q(participant__id_document__icontains=query) |
            Q(dog__name__icontains=query) |
            Q(bib_number__icontains=query)
        )
    
    # Obtener eventos y carreras para los filtros
    events = Event.objects.all().order_by('-start_date')
    races = Race.objects.all()
    
    if selected_event:
        races = races.filter(event_id=selected_event)
    
    races = races.order_by('event', 'date', 'name')
    
    context = {
        'registrations': registrations,
        'events': events,
        'races': races,
        'selected_event': selected_event,
        'selected_race': selected_race,
        'selected_payment_status': selected_payment_status,
        'query': query,
        'payment_status_choices': Registration.PAYMENT_STATUS_CHOICES
    }
    
    return render(request, 'registrations/registration_list.html', context)