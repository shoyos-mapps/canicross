from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, F
from django.db import transaction
from django.http import JsonResponse

from accounts.decorators import judge_required
from events.models import Event, Race, PenaltyType
from registrations.models import Registration, ParticipantAnnotation
from participants.models import Participant, Dog
from .models import Result, TimeRecord, Penalty

# Vistas públicas para ver resultados
def results_list(request):
    """Vista pública para listar resultados de todos los eventos."""
    events = Event.objects.filter(status__in=['in_progress', 'completed'])
    return render(request, 'results/results_list.html', {'events': events})

def event_results(request, event_slug):
    """Vista pública para ver resultados de un evento específico."""
    event = get_object_or_404(Event, slug=event_slug)
    races = Race.objects.filter(event=event)
    return render(request, 'results/event_results.html', {'event': event, 'races': races})

def race_results(request, race_id):
    """Vista pública para ver resultados de una carrera específica."""
    race = get_object_or_404(Race, id=race_id)
    results = Result.objects.filter(
        registration__race=race,
        status__in=['verified', 'pending']
    ).order_by('position', 'official_time_seconds')
    
    return render(request, 'results/race_results.html', {'race': race, 'results': results})

# Vistas para jueces (protegidas)
@login_required
@judge_required
def judge_dashboard(request):
    """
    Panel principal para jueces con resumen de carreras y resultados.
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
    
    # Estadísticas y carreras
    stats = {
        'total_races': 0,
        'total_participants': 0,
        'results_recorded': 0,
        'results_pending': 0,
        'penalties_recorded': 0
    }
    
    # Próximas carreras
    upcoming_races = []
    
    if selected_event:
        # Obtener carreras del evento
        races = Race.objects.filter(event=selected_event).order_by('race_date', 'race_time')
        
        # Contar participantes
        total_participants = Registration.objects.filter(
            race__event=selected_event
        ).count()
        
        # Contar resultados
        results_recorded = Result.objects.filter(
            registration__race__event=selected_event
        ).count()
        
        # Contar penalizaciones
        penalties_recorded = Penalty.objects.filter(
            result__registration__race__event=selected_event
        ).count()
        
        # Actualizar estadísticas
        stats['total_races'] = races.count()
        stats['total_participants'] = total_participants
        stats['results_recorded'] = results_recorded
        stats['results_pending'] = total_participants - results_recorded
        stats['penalties_recorded'] = penalties_recorded
        
        # Próximas carreras
        today = timezone.now().date()
        now = timezone.now().time()
        
        # Carreras de hoy que aún no han comenzado
        today_races = races.filter(race_date=today, race_time__gte=now)
        
        # Carreras de días futuros
        future_races = races.filter(race_date__gt=today)
        
        # Combinamos y limitamos a 5
        upcoming_races = list(today_races) + list(future_races)
        upcoming_races = upcoming_races[:5]
    
    context = {
        'active_events': active_events,
        'selected_event': selected_event,
        'stats': stats,
        'upcoming_races': upcoming_races,
    }
    
    return render(request, 'results/judge_dashboard.html', context)

@login_required
@judge_required
def race_list(request):
    """
    Lista de carreras del evento seleccionado para registrar resultados.
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
    
    races = []
    if selected_event:
        races = Race.objects.filter(event=selected_event).order_by('race_date', 'race_time')
        
        # Añadir estadísticas a cada carrera
        for race in races:
            # Total de participantes
            race.total_participants = Registration.objects.filter(race=race).count()
            
            # Resultados registrados
            race.results_recorded = Result.objects.filter(registration__race=race).count()
            
            # Porcentaje completado
            if race.total_participants > 0:
                race.completion_percentage = (race.results_recorded / race.total_participants) * 100
            else:
                race.completion_percentage = 0
    
    context = {
        'active_events': active_events,
        'selected_event': selected_event,
        'races': races,
    }
    
    return render(request, 'results/race_list.html', context)

@login_required
@judge_required
def participant_list(request, race_id):
    """
    Lista de participantes de una carrera para registrar resultados.
    """
    race = get_object_or_404(Race.objects.select_related('event'), id=race_id)
    
    # Filtrar por estado de resultado
    result_status = request.GET.get('status', 'pending')
    
    # Consulta base
    registrations = Registration.objects.filter(race=race).select_related(
        'participant', 'dog', 'race_category'
    ).order_by('bib_number')
    
    # Filtrar según el estado solicitado
    if result_status == 'pending':
        # Participantes sin resultados
        result_ids = Result.objects.filter(registration__race=race).values_list('registration_id', flat=True)
        registrations = registrations.exclude(id__in=result_ids)
    elif result_status == 'recorded':
        # Participantes con resultados
        result_ids = Result.objects.filter(registration__race=race).values_list('registration_id', flat=True)
        registrations = registrations.filter(id__in=result_ids)
    # 'all' muestra todos los participantes
    
    # Añadir información de resultados a cada registro
    for reg in registrations:
        try:
            reg.result = Result.objects.get(registration=reg)
            reg.has_result = True
            reg.penalties = Penalty.objects.filter(result=reg.result).count()
        except Result.DoesNotExist:
            reg.has_result = False
            reg.penalties = 0
    
    context = {
        'race': race,
        'registrations': registrations,
        'result_status': result_status,
    }
    
    return render(request, 'results/participant_list.html', context)

@login_required
@judge_required
def record_result(request, registration_id):
    """
    Formulario para registrar o editar el resultado de un participante.
    """
    registration = get_object_or_404(
        Registration.objects.select_related('participant', 'dog', 'race', 'race__event'),
        id=registration_id
    )
    
    # Verificar si ya existe un resultado
    try:
        result = Result.objects.get(registration=registration)
        is_new = False
    except Result.DoesNotExist:
        result = Result(
            registration=registration,
            recorded_by=request.user
        )
        is_new = True
    
    # Obtener los tiempos registrados
    time_records = TimeRecord.objects.filter(result=result).order_by('checkpoint_number')
    
    # Obtener las penalizaciones
    penalties = Penalty.objects.filter(result=result).select_related('penalty_type')
    
    # Obtener tipos de penalizaciones disponibles
    penalty_types = PenaltyType.objects.all()
    
    if request.method == 'POST':
        if 'save_result' in request.POST:
            with transaction.atomic():
                # Actualizar estado del resultado
                result.status = request.POST.get('status')
                
                # Tiempo oficial (formato HH:MM:SS)
                official_time = request.POST.get('official_time')
                if official_time:
                    time_parts = official_time.split(':')
                    if len(time_parts) == 3:
                        hours, minutes, seconds = map(int, time_parts)
                        result.official_time_seconds = hours * 3600 + minutes * 60 + seconds
                
                # Actualizar posición si se proporciona
                position = request.POST.get('position')
                if position and position.isdigit():
                    result.position = int(position)
                
                # Notas
                result.notes = request.POST.get('notes', '')
                
                # Guardar el resultado
                if is_new:
                    result.recorded_by = request.user
                    result.recorded_at = timezone.now()
                
                result.save()
                
                messages.success(request, "Resultado guardado correctamente")
                
                # Redireccionar según el botón presionado
                if 'save_and_continue' in request.POST:
                    return redirect('results:participant_list', race_id=registration.race.id)
                else:
                    return redirect('results:record_result', registration_id=registration.id)
        
        elif 'add_time' in request.POST:
            # Añadir un nuevo tiempo de paso
            checkpoint = request.POST.get('checkpoint_number')
            time_value = request.POST.get('time_value')
            
            if checkpoint and checkpoint.isdigit() and time_value:
                # Guardar resultado primero si es nuevo
                if is_new:
                    result.recorded_by = request.user
                    result.recorded_at = timezone.now()
                    result.save()
                    is_new = False
                
                # Convertir tiempo (formato HH:MM:SS) a segundos
                time_parts = time_value.split(':')
                seconds = 0
                if len(time_parts) == 3:
                    hours, minutes, secs = map(int, time_parts)
                    seconds = hours * 3600 + minutes * 60 + secs
                elif len(time_parts) == 2:
                    minutes, secs = map(int, time_parts)
                    seconds = minutes * 60 + secs
                
                # Crear o actualizar el tiempo
                TimeRecord.objects.update_or_create(
                    result=result,
                    checkpoint_number=int(checkpoint),
                    defaults={
                        'time_seconds': seconds,
                        'recorded_by': request.user
                    }
                )
                
                messages.success(request, "Tiempo de paso registrado correctamente")
                return redirect('results:record_result', registration_id=registration.id)
        
        elif 'add_penalty' in request.POST:
            # Añadir una nueva penalización
            penalty_type_id = request.POST.get('penalty_type')
            description = request.POST.get('penalty_description')
            
            if penalty_type_id and penalty_type_id.isdigit():
                # Guardar resultado primero si es nuevo
                if is_new:
                    result.recorded_by = request.user
                    result.recorded_at = timezone.now()
                    result.save()
                    is_new = False
                
                # Crear la penalización
                penalty_type = get_object_or_404(PenaltyType, id=penalty_type_id)
                Penalty.objects.create(
                    result=result,
                    penalty_type=penalty_type,
                    description=description,
                    recorded_by=request.user
                )
                
                messages.success(request, "Penalización añadida correctamente")
                return redirect('results:record_result', registration_id=registration.id)
    
    # Convertir tiempo en segundos a formato HH:MM:SS para mostrar en el formulario
    if result.official_time_seconds:
        hours = result.official_time_seconds // 3600
        minutes = (result.official_time_seconds % 3600) // 60
        seconds = result.official_time_seconds % 60
        result.formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    context = {
        'registration': registration,
        'result': result,
        'is_new': is_new,
        'time_records': time_records,
        'penalties': penalties,
        'penalty_types': penalty_types,
    }
    
    return render(request, 'results/record_result.html', context)

@login_required
@judge_required
def delete_penalty(request, penalty_id):
    """
    Eliminar una penalización.
    """
    penalty = get_object_or_404(Penalty, id=penalty_id)
    registration_id = penalty.result.registration.id
    
    if request.method == 'POST':
        penalty.delete()
        messages.success(request, "Penalización eliminada correctamente")
    
    return redirect('results:record_result', registration_id=registration_id)

@login_required
@judge_required
def delete_time_record(request, time_record_id):
    """
    Eliminar un registro de tiempo.
    """
    time_record = get_object_or_404(TimeRecord, id=time_record_id)
    registration_id = time_record.result.registration.id
    
    if request.method == 'POST':
        time_record.delete()
        messages.success(request, "Tiempo de paso eliminado correctamente")
    
    return redirect('results:record_result', registration_id=registration_id)

@login_required
@judge_required
def add_annotation(request, registration_id):
    """
    Añadir una anotación o incidencia a un participante.
    """
    registration = get_object_or_404(
        Registration.objects.select_related('participant', 'dog', 'race'),
        id=registration_id
    )
    
    # Obtener tipos de penalizaciones disponibles
    penalty_types = PenaltyType.objects.all()
    
    if request.method == 'POST':
        penalty_type_id = request.POST.get('penalty_type')
        notes = request.POST.get('notes')
        location = request.POST.get('location', '')
        
        if penalty_type_id and penalty_type_id.isdigit() and notes:
            penalty_type = get_object_or_404(PenaltyType, id=penalty_type_id)
            
            annotation = ParticipantAnnotation.objects.create(
                registration=registration,
                penalty_type=penalty_type,
                notes=notes,
                location=location,
                recorded_by=request.user,
                status='recorded'
            )
            
            messages.success(request, "Anotación registrada correctamente")
            
            # Si el tipo de penalización tiene tiempo de penalización,
            # redirigir a la página de resultados para añadirla
            if penalty_type.time_penalty > 0:
                return redirect('results:record_result', registration_id=registration.id)
            
            # Si es descalificación, actualizar el resultado si existe
            if penalty_type.is_disqualification:
                try:
                    result = Result.objects.get(registration=registration)
                    result.status = 'disqualified'
                    result.save()
                    messages.info(request, "El participante ha sido descalificado")
                except Result.DoesNotExist:
                    # Crear un nuevo resultado con estado descalificado
                    Result.objects.create(
                        registration=registration,
                        status='disqualified',
                        recorded_by=request.user,
                        recorded_at=timezone.now()
                    )
                    messages.info(request, "Se ha creado un resultado con estado descalificado")
            
            return redirect('results:participant_list', race_id=registration.race.id)
    
    context = {
        'registration': registration,
        'penalty_types': penalty_types,
    }
    
    return render(request, 'results/add_annotation.html', context)