from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .models import Participant, Dog
from .forms import ParticipantForm, DogForm
from registrations.models import Registration
from utils.logger import get_logger, log_function_call, log_exception
from accounts.decorators import admin_required, staff_required

logger = get_logger('participants')

@login_required
@staff_required
def participant_list(request):
    """
    Vista para listar todos los participantes.
    Solo accesible para admins y staff.
    """
    try:
        # Obtener todos los participantes con sus datos relacionados
        participants = Participant.objects.all().prefetch_related(
            'dogs',
            Prefetch('registrations', queryset=Registration.objects.select_related('race', 'race__event', 'dog'))
        ).order_by('participant_number', 'last_name', 'first_name')
        
        return render(request, 'participants/participant_list.html', {
            'participants': participants,
            'title': 'Lista de Participantes'
        })
    except Exception as e:
        log_exception(logger, f"Error al listar participantes: {str(e)}")
        messages.error(request, "Hubo un error al cargar la lista de participantes.")
        return redirect('admin:index')

@login_required
@log_function_call(logger)
def participant_profile(request):
    """
    Vista para mostrar y editar el perfil del participante.
    """
    try:
        # Buscar primero el perfil del participante para el usuario actual
        try:
            participant = Participant.objects.get(user=request.user)
            created = False
        except Participant.DoesNotExist:
            # Si no existe, lo creamos con valores predeterminados
            participant = Participant(
                user=request.user,
                first_name=request.user.first_name if request.user.first_name else "",
                last_name=request.user.last_name if request.user.last_name else "",
                email=request.user.email if request.user.email else "",
                date_of_birth=None,  # Establecer explícitamente a None
                gender='',  # Campo vacío
            )
            participant.save()
            created = True
        
        if request.method == 'POST':
            form = ParticipantForm(request.POST, request.FILES, instance=participant)
            if form.is_valid():
                try:
                    # Imprimir los datos del formulario para DEBUG
                    logger.info(f"DATOS DEL FORMULARIO: {form.data}")
                    logger.info(f"CLEANED_DATA: {form.cleaned_data}")
                    
                    # Guardar los cambios
                    participant = form.save(commit=False)
                    
                    # Obtener la fecha explícitamente
                    dob = form.cleaned_data.get('date_of_birth')
                    logger.info(f"FECHA OBTENIDA: {dob}, TIPO: {type(dob)}")
                    
                    # Forzar la actualización del campo
                    participant.date_of_birth = dob
                    
                    # Guardar definitivamente
                    participant.save()
                    
                    # Verificar después de guardar
                    participant_saved = Participant.objects.get(id=participant.id)
                    logger.info(f"VERIFICACIÓN - Fecha guardada en DB: {participant_saved.date_of_birth}")
                    messages.success(request, "¡Perfil actualizado con éxito!")
                    return redirect('participants:profile')
                except Exception as e:
                    log_exception(logger, f"Error al guardar el perfil: {str(e)}")
                    messages.error(request, f"Error al guardar: {str(e)}")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en {field}: {error}")
        else:
            form = ParticipantForm(instance=participant)
        
        # Obtener perros del participante
        dogs = Dog.objects.filter(owner=participant)
        
        # Obtener inscripciones del participante
        registrations = Registration.objects.filter(participant=participant).select_related('race', 'race__event', 'dog')
        
        return render(request, 'participants/participant_profile.html', {
            'form': form,
            'participant': participant,
            'dogs': dogs,
            'registrations': registrations,
            'is_new': created
        })
    except Exception as e:
        log_exception(logger, f"Error al cargar perfil de participante: {str(e)}")
        messages.error(request, "Hubo un error al cargar su perfil. Por favor, inténtelo de nuevo.")
        return redirect('events:event_list')

@login_required
@log_function_call(logger)
def dog_list(request):
    """
    Vista para listar los perros del participante.
    """
    try:
        # Obtener el participante actual
        participant = get_object_or_404(Participant, user=request.user)
        
        # Obtener perros del participante
        dogs = Dog.objects.filter(owner=participant)
        
        return render(request, 'participants/dog_list.html', {
            'dogs': dogs,
            'participant': participant
        })
    except Participant.DoesNotExist:
        messages.warning(request, "Debe completar su perfil antes de registrar perros.")
        return redirect('participants:profile')
    except Exception as e:
        log_exception(logger, f"Error al listar perros: {str(e)}")
        messages.error(request, "Hubo un error al cargar sus perros. Por favor, inténtelo de nuevo.")
        return redirect('participants:profile')

@login_required
@log_function_call(logger)
def dog_add(request):
    """
    Vista para añadir un nuevo perro.
    """
    try:
        # Obtener el participante actual
        participant = get_object_or_404(Participant, user=request.user)
        
        if request.method == 'POST':
            form = DogForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Guardar primero para obtener la instancia
                    dog = form.save(commit=False)
                    dog.owner = participant
                    
                    # Manejar explícitamente la fecha
                    dob = form.cleaned_data.get('date_of_birth')
                    logger.info(f"PERRO - Fecha obtenida: {dob}")
                    dog.date_of_birth = dob
                    
                    # Guardar
                    dog.save()
                    
                    messages.success(request, f"¡{dog.name} registrado con éxito!")
                    return redirect('participants:dog_list')
                except Exception as e:
                    log_exception(logger, f"Error al guardar perro: {str(e)}")
                    messages.error(request, f"Error: {str(e)}")
        else:
            form = DogForm()
        
        return render(request, 'participants/dog_form.html', {
            'form': form,
            'action': 'add'
        })
    except Participant.DoesNotExist:
        messages.warning(request, "Debe completar su perfil antes de registrar perros.")
        return redirect('participants:profile')
    except Exception as e:
        log_exception(logger, f"Error al añadir perro: {str(e)}")
        messages.error(request, "Hubo un error al registrar su perro. Por favor, inténtelo de nuevo.")
        return redirect('participants:dog_list')

@login_required
@log_function_call(logger)
def dog_detail(request, dog_id):
    """
    Vista para ver detalles de un perro.
    """
    try:
        # Obtener el participante actual
        participant = get_object_or_404(Participant, user=request.user)
        
        # Obtener el perro y verificar que pertenece al participante
        dog = get_object_or_404(Dog, id=dog_id, owner=participant)
        
        return render(request, 'participants/dog_detail.html', {
            'dog': dog,
            'participant': participant
        })
    except (Participant.DoesNotExist, Dog.DoesNotExist):
        messages.warning(request, "No se encontró el perro solicitado.")
        return redirect('participants:dog_list')
    except Exception as e:
        log_exception(logger, f"Error al mostrar detalles del perro: {str(e)}")
        messages.error(request, "Hubo un error al cargar los detalles. Por favor, inténtelo de nuevo.")
        return redirect('participants:dog_list')

@login_required
@log_function_call(logger)
def dog_edit(request, dog_id):
    """
    Vista para editar un perro existente.
    """
    try:
        # Obtener el participante actual
        participant = get_object_or_404(Participant, user=request.user)
        
        # Obtener el perro y verificar que pertenece al participante
        dog = get_object_or_404(Dog, id=dog_id, owner=participant)
        
        if request.method == 'POST':
            form = DogForm(request.POST, request.FILES, instance=dog)
            if form.is_valid():
                try:
                    # Guardar primero para obtener la instancia
                    updated_dog = form.save(commit=False)
                    
                    # Manejar explícitamente la fecha
                    dob = form.cleaned_data.get('date_of_birth')
                    logger.info(f"PERRO EDIT - Fecha obtenida: {dob}")
                    updated_dog.date_of_birth = dob
                    
                    # Guardar
                    updated_dog.save()
                    
                    messages.success(request, f"¡{dog.name} actualizado con éxito!")
                    return redirect('participants:dog_detail', dog_id=dog.id)
                except Exception as e:
                    log_exception(logger, f"Error al actualizar perro: {str(e)}")
                    messages.error(request, f"Error: {str(e)}")
        else:
            form = DogForm(instance=dog)
        
        return render(request, 'participants/dog_form.html', {
            'form': form,
            'dog': dog,
            'action': 'edit'
        })
    except (Participant.DoesNotExist, Dog.DoesNotExist):
        messages.warning(request, "No se encontró el perro solicitado.")
        return redirect('participants:dog_list')
    except Exception as e:
        log_exception(logger, f"Error al editar perro: {str(e)}")
        messages.error(request, "Hubo un error al actualizar su perro. Por favor, inténtelo de nuevo.")
        return redirect('participants:dog_list')