from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Registration
from events.models import Event, Race, RaceCategory
from utils.logger import get_logger, log_function_call, log_exception

logger = get_logger('registrations')

def registration_form(request):
    # Simple placeholder view
    return render(request, 'registrations/registration_form.html')

@login_required
@log_function_call(logger)
def registration_confirmation(request, registration_id):
    """
    Vista para mostrar la confirmación de inscripción y opciones de pago.
    """
    try:
        # Obtener la inscripción y verificar que pertenece al usuario actual
        registration = get_object_or_404(Registration, id=registration_id)
        
        # Verificar que el usuario es el propietario de la inscripción
        if registration.participant.user != request.user:
            messages.error(request, "No tiene permiso para acceder a esta inscripción.")
            return redirect('events:event_list')
        
        # Obtener datos relacionados
        event = registration.race.event
        
        return render(request, 'registrations/registration_confirmation.html', {
            'registration': registration,
            'event': event,
            'participant': registration.participant,
            'dog': registration.dog,
            'race': registration.race,
            'category': registration.race_category.category,
        })
    except Exception as e:
        log_exception(logger, f"Error al mostrar confirmación de inscripción: {str(e)}")
        messages.error(request, "Hubo un error al procesar su solicitud. Por favor, inténtelo de nuevo.")
        return redirect('events:event_list')
