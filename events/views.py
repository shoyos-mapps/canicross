from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Event, Race, RaceCategory
from participants.models import Participant, Dog
from registrations.models import Registration
from utils.logger import get_logger, log_function_call, log_exception
from utils.emails import send_registration_confirmation

logger = get_logger('events')

@log_function_call(logger)
def event_list(request):
    try:
        logger.info(f"Accediendo a lista de eventos por usuario: {request.user}")
        
        # Obtener eventos publicados con prefetch_related para cargar las carreras relacionadas
        events = Event.objects.filter(status__in=['published', 'registration_open', 'in_progress']).prefetch_related('races')
        
        logger.debug(f"Se encontraron {events.count()} eventos publicados")
        return render(request, 'events/event_list.html', {'events': events})
    except Exception as e:
        log_exception(logger, "Error al obtener lista de eventos")
        raise

@log_function_call(logger)
def event_detail(request, slug):
    try:
        logger.info(f"Accediendo a detalle de evento: {slug} por usuario: {request.user}")
        event = get_object_or_404(Event, slug=slug)
        logger.debug(f"Evento encontrado: {event.name}")
        return render(request, 'events/event_detail.html', {'event': event})
    except Event.DoesNotExist:
        logger.warning(f"Evento no encontrado: {slug}")
        raise
    except Exception as e:
        log_exception(logger, f"Error al obtener detalle del evento: {slug}")
        raise

@log_function_call(logger)
def race_list(request, slug):
    try:
        logger.info(f"Accediendo a lista de carreras para evento: {slug}")
        event = get_object_or_404(Event, slug=slug)
        races = Race.objects.filter(event=event)
        logger.debug(f"Se encontraron {races.count()} carreras para el evento: {event.name}")
        return render(request, 'events/race_list.html', {'event': event, 'races': races})
    except Event.DoesNotExist:
        logger.warning(f"Evento no encontrado: {slug}")
        raise
    except Exception as e:
        log_exception(logger, f"Error al obtener lista de carreras para el evento: {slug}")
        raise

@log_function_call(logger)
def race_detail(request, slug, race_id):
    try:
        logger.info(f"Accediendo a detalle de carrera: {race_id} en evento: {slug}")
        event = get_object_or_404(Event, slug=slug)
        race = get_object_or_404(Race, id=race_id, event=event)
        logger.debug(f"Carrera encontrada: {race.name} en evento: {event.name}")
        return render(request, 'events/race_detail.html', {'event': event, 'race': race})
    except (Event.DoesNotExist, Race.DoesNotExist) as e:
        logger.warning(f"Recurso no encontrado. Evento: {slug}, Carrera: {race_id}")
        raise
    except Exception as e:
        log_exception(logger, f"Error al obtener detalle de carrera: {race_id} en evento: {slug}")
        raise

@log_function_call(logger)
def event_register(request, slug):
    """
    Vista para el registro en un evento.
    Muestra el formulario de registro y procesa la inscripción.
    """
    try:
        logger.info(f"Accediendo a registro de evento: {slug} por usuario: {request.user}")
        event = get_object_or_404(Event, slug=slug)
        
        # Verificar si el evento está abierto para inscripciones
        if event.status != 'registration_open':
            messages.warning(request, f"Las inscripciones para {event.name} no están abiertas actualmente.")
            return redirect('events:event_detail', slug=event.slug)
        
        # Obtener todas las carreras disponibles para este evento
        races = Race.objects.filter(event=event)
        race_categories = RaceCategory.objects.filter(race__event=event)
        
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            # Renderizar la plantilla con needs_login=True sin agregar mensaje duplicado
            return render(request, 'events/event_register.html', {
                'event': event,
                'races': races,
                'race_categories': race_categories,
                'needs_login': True
            })
        
        # Si es una solicitud POST, procesar el formulario de inscripción
        if request.method == 'POST':
            # Aquí iría la lógica para procesar el formulario de inscripción
            # (esto es solo un ejemplo simplificado)
            race_id = request.POST.get('race')
            race_category_id = request.POST.get('race_category')
            dog_id = request.POST.get('dog')
            
            if race_id and race_category_id and dog_id:
                try:
                    race = Race.objects.get(id=race_id, event=event)
                    race_category = RaceCategory.objects.get(id=race_category_id, race=race)
                    dog = Dog.objects.get(id=dog_id, owner__user=request.user)
                    
                    # Obtener el participante (asumiendo que existe uno asociado al usuario)
                    participant = Participant.objects.get(user=request.user)
                    
                    # Crear la inscripción
                    registration = Registration.objects.create(
                        participant=participant,
                        dog=dog,
                        race=race,
                        race_category=race_category,
                        registration_status='pending',
                        payment_status='pending',
                        waiver_accepted=True if request.POST.get('waiver_accepted') else False
                    )
                    
                    # Enviar correo de confirmación
                    email_sent = send_registration_confirmation(registration)
                    if email_sent:
                        logger.info(f"Correo de confirmación enviado para inscripción {registration.id}")
                        messages.success(request, "¡Inscripción completada con éxito! Hemos enviado un correo con los detalles. Por favor, complete el pago para confirmar su plaza.")
                    else:
                        logger.warning(f"No se pudo enviar correo de confirmación para inscripción {registration.id}")
                        messages.success(request, "¡Inscripción completada con éxito! Por favor, complete el pago para confirmar su plaza.")
                    
                    logger.info(f"Inscripción creada: Participante {participant.id}, perro {dog.id}, carrera {race.id}")
                    
                    # Redirigir a la página de pago o confirmación
                    return redirect('registrations:confirmation', registration_id=registration.id)
                except Exception as e:
                    log_exception(logger, f"Error al procesar inscripción: {str(e)}")
                    messages.error(request, "Hubo un error al procesar su inscripción. Por favor, inténtelo de nuevo.")
            else:
                messages.error(request, "Por favor, complete todos los campos requeridos.")
        
        # Obtener perros del participante actual
        try:
            participant = Participant.objects.get(user=request.user)
            dogs = Dog.objects.filter(owner=participant)
        except Participant.DoesNotExist:
            dogs = []
            messages.warning(request, "Debe completar su perfil de participante antes de inscribirse.")
        
        return render(request, 'events/event_register.html', {
            'event': event,
            'races': races,
            'race_categories': race_categories,
            'dogs': dogs,
        })
        
    except Event.DoesNotExist:
        logger.warning(f"Evento no encontrado: {slug}")
        raise
    except Exception as e:
        log_exception(logger, f"Error en la página de registro del evento: {slug}")
        raise
