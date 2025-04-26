#!/usr/bin/env python
"""
Script para configurar grupos de permisos para diferentes roles de usuario en Canicross.
Implementa un modelo de permisos basado en el principio de mínimo privilegio y separación de funciones.
"""
import os
import django
import sys
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from accounts.models import User
from participants.models import Dog, Participant
from events.models import Event, Race, RaceCategory, PenaltyType, Modality, Category
from registrations.models import Registration, Document, ParticipantAnnotation
from veterinary.models import VeterinaryCheck, VaccinationRecord, MedicalAlert
from results.models import Result, TimeRecord, Penalty
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission

def set_model_permissions(group, model, view=False, change=False, add=False, delete=False):
    """
    Configura los permisos de un modelo para un grupo específico.
    
    Args:
        group: Grupo al que asignar los permisos
        model: Modelo para el que configurar permisos
        view, change, add, delete: Booleanos que indican qué permisos otorgar
    """
    content_type = ContentType.objects.get_for_model(model)
    
    if view:
        perm = Permission.objects.get(content_type=content_type, codename=f"view_{model._meta.model_name}")
        group.permissions.add(perm)
    
    if change:
        perm = Permission.objects.get(content_type=content_type, codename=f"change_{model._meta.model_name}")
        group.permissions.add(perm)
    
    if add:
        perm = Permission.objects.get(content_type=content_type, codename=f"add_{model._meta.model_name}")
        group.permissions.add(perm)
    
    if delete:
        perm = Permission.objects.get(content_type=content_type, codename=f"delete_{model._meta.model_name}")
        group.permissions.add(perm)

def create_superadmin_group():
    """
    Crea o actualiza el grupo de Administradores Globales (Super Admin).
    Este rol tiene control total sobre la plataforma.
    """
    superadmin_group, created = Group.objects.get_or_create(name='Administradores')
    
    if not created:
        superadmin_group.permissions.clear()
        print("Grupo 'Administradores' existente encontrado y limpiado.")
    else:
        print("Grupo 'Administradores' creado.")
    
    # Asignar todos los permisos disponibles
    all_permissions = Permission.objects.exclude(content_type__app_label='contenttypes')
    all_permissions = all_permissions.exclude(content_type__app_label='sessions')
    
    superadmin_group.permissions.add(*all_permissions)
    
    print(f"Se han asignado {superadmin_group.permissions.count()} permisos al grupo 'Administradores'.")
    
    # Asignar usuarios de tipo 'admin' al grupo
    admin_users = User.objects.filter(Q(user_type='admin') | Q(is_superuser=True))
    for user in admin_users:
        user.groups.add(superadmin_group)
    
    print(f"Se han asignado {admin_users.count()} usuarios al grupo 'Administradores'.")
    return superadmin_group

def create_organizer_group():
    """
    Crea o actualiza el grupo de Organizadores de Eventos.
    Este rol gestiona eventos específicos y su configuración.
    """
    organizer_group, created = Group.objects.get_or_create(name='Organizadores')
    
    if not created:
        organizer_group.permissions.clear()
        print("Grupo 'Organizadores' existente encontrado y limpiado.")
    else:
        print("Grupo 'Organizadores' creado.")
    
    # Modelos que necesitan permisos completos
    event_models = [
        Event,
        Race,
        Modality,
        Category,
        RaceCategory,
        PenaltyType,
    ]
    
    # Permisos completos para modelos de eventos
    for model in event_models:
        set_model_permissions(organizer_group, model, view=True, change=True, add=True, delete=True)
    
    # Modelos con permisos de lectura y modificación
    management_models = {
        # Modelo: (view, change, add, delete)
        Registration: (True, True, True, True),
        Document: (True, True, True, True),
        ParticipantAnnotation: (True, True, True, True),
        Result: (True, True, True, False),  # Puede ver y modificar resultados, pero no borrarlos
        User: (True, True, False, False),  # Puede ver y modificar usuarios pero no crear/eliminar
    }
    
    for model, permissions_flags in management_models.items():
        view, change, add, delete = permissions_flags
        set_model_permissions(organizer_group, model, view, change, add, delete)
    
    # Permisos de solo lectura
    readonly_models = [
        Dog,
        Participant,
        VeterinaryCheck,
        TimeRecord,
        Penalty,
    ]
    
    for model in readonly_models:
        set_model_permissions(organizer_group, model, view=True)
    
    print(f"Se han asignado {organizer_group.permissions.count()} permisos al grupo 'Organizadores'.")
    
    # Asignar usuarios de tipo 'staff' al grupo (si es que corresponde a este rol)
    staff_users = User.objects.filter(user_type='staff')
    for user in staff_users:
        user.groups.add(organizer_group)
    
    print(f"Se han asignado {staff_users.count()} usuarios al grupo 'Organizadores'.")
    return organizer_group

def create_registration_manager_group():
    """
    Crea o actualiza el grupo de Gestores de Inscripciones.
    Este rol se encarga específicamente del proceso de registro de participantes.
    """
    reg_manager_group, created = Group.objects.get_or_create(name='Gestores_Inscripciones')
    
    if not created:
        reg_manager_group.permissions.clear()
        print("Grupo 'Gestores_Inscripciones' existente encontrado y limpiado.")
    else:
        print("Grupo 'Gestores_Inscripciones' creado.")
    
    # Modelos con acceso completo o parcial
    reg_models = {
        # Modelo: (view, change, add, delete)
        Registration: (True, True, True, False),  # Gestión completa excepto eliminar
        Document: (True, True, True, False),      # Gestión completa excepto eliminar
        Participant: (True, True, False, False),  # Modificar datos, pero no crear/borrar
        Dog: (True, True, False, False),          # Modificar datos, pero no crear/borrar
    }
    
    for model, permissions_flags in reg_models.items():
        view, change, add, delete = permissions_flags
        set_model_permissions(reg_manager_group, model, view, change, add, delete)
    
    # Modelos de solo lectura
    readonly_models = [
        Event, 
        Race, 
        RaceCategory,
        Category,
        Modality
    ]
    
    for model in readonly_models:
        set_model_permissions(reg_manager_group, model, view=True)
    
    print(f"Se han asignado {reg_manager_group.permissions.count()} permisos al grupo 'Gestores_Inscripciones'.")
    return reg_manager_group

def create_veterinary_group():
    """
    Crea o actualiza el grupo de Veterinarios.
    Este rol verifica la aptitud de los perros para competir.
    """
    vet_group, created = Group.objects.get_or_create(name='Veterinarios')
    
    if not created:
        vet_group.permissions.clear()
        print("Grupo 'Veterinarios' existente encontrado y limpiado.")
    else:
        print("Grupo 'Veterinarios' creado.")
    
    # Modelos específicos de veterinaria con acceso completo
    vet_models = [
        VeterinaryCheck,
        VaccinationRecord,
        MedicalAlert,
    ]
    
    for model in vet_models:
        set_model_permissions(vet_group, model, view=True, change=True, add=True, delete=True)
    
    # Modelos que pueden modificar pero no crear/eliminar
    partial_models = {
        Registration: (True, True, False, False),  # Actualizar estado veterinario
        Document: (True, True, False, False),      # Actualizar documentos de vacunación
    }
    
    for model, permissions_flags in partial_models.items():
        view, change, add, delete = permissions_flags
        set_model_permissions(vet_group, model, view, change, add, delete)
    
    # Modelos de solo lectura
    readonly_models = [
        Dog,
        Participant,
        Event,
        Race,
    ]
    
    for model in readonly_models:
        set_model_permissions(vet_group, model, view=True)
    
    print(f"Se han asignado {vet_group.permissions.count()} permisos al grupo 'Veterinarios'.")
    
    # Asignar usuarios existentes del tipo 'veterinary' al grupo
    vet_users = User.objects.filter(user_type='veterinary')
    for user in vet_users:
        user.groups.add(vet_group)
    
    print(f"Se han asignado {vet_users.count()} usuarios al grupo 'Veterinarios'.")
    return vet_group

def create_judge_group():
    """
    Crea o actualiza el grupo de Jueces.
    Supervisa el cumplimiento del reglamento y registra resultados.
    """
    judge_group, created = Group.objects.get_or_create(name='Jueces')
    
    if not created:
        judge_group.permissions.clear()
        print("Grupo 'Jueces' existente encontrado y limpiado.")
    else:
        print("Grupo 'Jueces' creado.")
    
    # Modelos específicos de resultados con acceso completo
    result_models = [
        Result,
        TimeRecord,
        Penalty,
        ParticipantAnnotation,
    ]
    
    for model in result_models:
        set_model_permissions(judge_group, model, view=True, change=True, add=True, delete=True)
    
    # Modelos con permisos parciales
    partial_models = {
        Registration: (True, True, False, False),  # Actualizar estado pero no crear/eliminar
    }
    
    for model, permissions_flags in partial_models.items():
        view, change, add, delete = permissions_flags
        set_model_permissions(judge_group, model, view, change, add, delete)
    
    # Modelos de solo lectura
    readonly_models = [
        Dog,
        Participant,
        Event,
        Race,
        RaceCategory,
        PenaltyType,
        VeterinaryCheck,  # Para verificar aptitud del perro
    ]
    
    for model in readonly_models:
        set_model_permissions(judge_group, model, view=True)
    
    print(f"Se han asignado {judge_group.permissions.count()} permisos al grupo 'Jueces'.")
    
    # Asignar usuarios existentes del tipo 'judge' al grupo
    judge_users = User.objects.filter(user_type='judge')
    for user in judge_users:
        user.groups.add(judge_group)
    
    print(f"Se han asignado {judge_users.count()} usuarios al grupo 'Jueces'.")
    return judge_group

def create_timekeeper_group():
    """
    Crea o actualiza el grupo de Cronometradores.
    Gestiona específicamente el cronometraje y cálculo de resultados.
    """
    timekeeper_group, created = Group.objects.get_or_create(name='Cronometradores')
    
    if not created:
        timekeeper_group.permissions.clear()
        print("Grupo 'Cronometradores' existente encontrado y limpiado.")
    else:
        print("Grupo 'Cronometradores' creado.")
    
    # Permisos específicos para resultados y tiempos
    result_models = {
        Result: (True, True, True, False),      # Ver, modificar, crear pero no eliminar
        TimeRecord: (True, True, True, True),   # Control completo de tiempos
    }
    
    for model, permissions_flags in result_models.items():
        view, change, add, delete = permissions_flags
        set_model_permissions(timekeeper_group, model, view, change, add, delete)
    
    # Modelos de solo lectura
    readonly_models = [
        Registration,
        Participant,
        Dog,
        Event,
        Race,
        RaceCategory,
        Penalty,  # Ver penalizaciones pero no gestionarlas
        ParticipantAnnotation,  # Ver anotaciones pero no gestionarlas
    ]
    
    for model in readonly_models:
        set_model_permissions(timekeeper_group, model, view=True)
    
    print(f"Se han asignado {timekeeper_group.permissions.count()} permisos al grupo 'Cronometradores'.")
    return timekeeper_group

def create_participant_group():
    """
    Crea o actualiza el grupo de Participantes.
    Usuarios que se inscriben en carreras, con acceso limitado a sus propios datos.
    """
    participant_group, created = Group.objects.get_or_create(name='Participantes')
    
    if not created:
        participant_group.permissions.clear()
        print("Grupo 'Participantes' existente encontrado y limpiado.")
    else:
        print("Grupo 'Participantes' creado.")
    
    # Los participantes solo pueden editar sus propios perfiles y perros
    # El acceso a estos se controla a nivel de vista, no por permisos de modelo
    
    # Modelos que pueden ver y editar (propios)
    own_models = {
        Participant: (True, True, False, False),  # Ver y editar su perfil pero no crear/eliminar otros
        Dog: (True, True, True, True),            # Gestionar sus propios perros
    }
    
    for model, permissions_flags in own_models.items():
        view, change, add, delete = permissions_flags
        set_model_permissions(participant_group, model, view, change, add, delete)
    
    # Modelos que pueden ver pero no modificar
    readonly_models = [
        Event,
        Race,
        RaceCategory,
        Result,  # Ver sus propios resultados
    ]
    
    for model in readonly_models:
        set_model_permissions(participant_group, model, view=True)
    
    # Modelos a los que tienen acceso especial
    special_models = {
        Registration: (True, True, True, False),  # Crear y editar sus inscripciones, no eliminar
        Document: (True, True, True, True),       # Gestionar sus propios documentos
    }
    
    for model, permissions_flags in special_models.items():
        view, change, add, delete = permissions_flags
        set_model_permissions(participant_group, model, view, change, add, delete)
    
    print(f"Se han asignado {participant_group.permissions.count()} permisos al grupo 'Participantes'.")
    
    # Asignar usuarios existentes del tipo 'participant' al grupo
    participant_users = User.objects.filter(user_type='participant')
    for user in participant_users:
        user.groups.add(participant_group)
    
    print(f"Se han asignado {participant_users.count()} usuarios al grupo 'Participantes'.")
    return participant_group

def create_volunteer_group():
    """
    Crea o actualiza el grupo de Voluntarios.
    Personal de apoyo con acceso muy limitado y específico.
    """
    volunteer_group, created = Group.objects.get_or_create(name='Voluntarios')
    
    if not created:
        volunteer_group.permissions.clear()
        print("Grupo 'Voluntarios' existente encontrado y limpiado.")
    else:
        print("Grupo 'Voluntarios' creado.")
    
    # Los voluntarios tienen acceso mínimo, principalmente de solo lectura
    readonly_models = [
        Registration,  # Para check-in y entregas
        Participant,
        Dog,
        Event,
        Race,
    ]
    
    for model in readonly_models:
        set_model_permissions(volunteer_group, model, view=True)
    
    # Posibilidad de marcar entregas y check-ins (permisos especiales)
    partial_models = {
        Registration: (True, True, False, False),  # Para actualizar estados de check-in y kit
    }
    
    for model, permissions_flags in partial_models.items():
        view, change, add, delete = permissions_flags
        set_model_permissions(volunteer_group, model, view, change, add, delete)
    
    print(f"Se han asignado {volunteer_group.permissions.count()} permisos al grupo 'Voluntarios'.")
    return volunteer_group

def print_group_permissions(group):
    """Imprime los permisos de un grupo de forma legible."""
    print(f"\nPermisos del grupo '{group.name}':")
    
    # Agrupar permisos por modelo
    model_perms = {}
    for perm in group.permissions.all():
        model = perm.content_type.model
        if model not in model_perms:
            model_perms[model] = []
        model_perms[model].append(perm.codename)
    
    # Imprimir permisos agrupados
    for model, perms in sorted(model_perms.items()):
        print(f"  {model.capitalize()}:")
        for perm in sorted(perms):
            print(f"    - {perm}")

def create_sample_users():
    """Crea usuarios de ejemplo para probar los grupos de permisos."""
    # Administrador
    admin_user, created = User.objects.get_or_create(
        username='admin_example',
        defaults={
            'email': 'admin@example.com', 
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': False
        }
    )
    
    if created:
        admin_user.set_password('password123')
        admin_user.save()
        print(f"Usuario administrador creado: {admin_user.username}")
    else:
        print(f"Usuario administrador ya existe: {admin_user.username}")
    
    # Organizador
    organizer_user, created = User.objects.get_or_create(
        username='organizer_example',
        defaults={
            'email': 'organizer@example.com', 
            'first_name': 'Organizador',
            'last_name': 'Eventos',
            'user_type': 'staff',
            'is_staff': True
        }
    )
    
    if created:
        organizer_user.set_password('password123')
        organizer_user.save()
        print(f"Usuario organizador creado: {organizer_user.username}")
    else:
        print(f"Usuario organizador ya existe: {organizer_user.username}")
    
    # Gestor de inscripciones
    reg_manager_user, created = User.objects.get_or_create(
        username='regmanager_example',
        defaults={
            'email': 'regmanager@example.com', 
            'first_name': 'Gestor',
            'last_name': 'Inscripciones',
            'user_type': 'staff',
            'is_staff': True
        }
    )
    
    if created:
        reg_manager_user.set_password('password123')
        reg_manager_user.save()
        print(f"Usuario gestor de inscripciones creado: {reg_manager_user.username}")
    else:
        print(f"Usuario gestor ya existe: {reg_manager_user.username}")
    
    # Veterinario
    vet_user, created = User.objects.get_or_create(
        username='vet_example',
        defaults={
            'email': 'vet@example.com', 
            'first_name': 'Veterinario',
            'last_name': 'Ejemplo',
            'user_type': 'veterinary',
            'is_staff': True
        }
    )
    
    if created:
        vet_user.set_password('password123')
        vet_user.save()
        print(f"Usuario veterinario creado: {vet_user.username}")
    else:
        print(f"Usuario veterinario ya existe: {vet_user.username}")
    
    # Juez
    judge_user, created = User.objects.get_or_create(
        username='judge_example',
        defaults={
            'email': 'judge@example.com', 
            'first_name': 'Juez',
            'last_name': 'Ejemplo',
            'user_type': 'judge',
            'is_staff': True
        }
    )
    
    if created:
        judge_user.set_password('password123')
        judge_user.save()
        print(f"Usuario juez creado: {judge_user.username}")
    else:
        print(f"Usuario juez ya existe: {judge_user.username}")
    
    # Cronometrador
    timekeeper_user, created = User.objects.get_or_create(
        username='timekeeper_example',
        defaults={
            'email': 'timekeeper@example.com', 
            'first_name': 'Cronometrador',
            'last_name': 'Ejemplo',
            'user_type': 'staff',
            'is_staff': True
        }
    )
    
    if created:
        timekeeper_user.set_password('password123')
        timekeeper_user.save()
        print(f"Usuario cronometrador creado: {timekeeper_user.username}")
    else:
        print(f"Usuario cronometrador ya existe: {timekeeper_user.username}")
    
    # Participante
    participant_user, created = User.objects.get_or_create(
        username='participant_example',
        defaults={
            'email': 'participant@example.com', 
            'first_name': 'Participante',
            'last_name': 'Ejemplo',
            'user_type': 'participant',
        }
    )
    
    if created:
        participant_user.set_password('password123')
        participant_user.save()
        print(f"Usuario participante creado: {participant_user.username}")
    else:
        print(f"Usuario participante ya existe: {participant_user.username}")
    
    # Voluntario
    volunteer_user, created = User.objects.get_or_create(
        username='volunteer_example',
        defaults={
            'email': 'volunteer@example.com', 
            'first_name': 'Voluntario',
            'last_name': 'Ejemplo',
            'user_type': 'staff',
        }
    )
    
    if created:
        volunteer_user.set_password('password123')
        volunteer_user.save()
        print(f"Usuario voluntario creado: {volunteer_user.username}")
    else:
        print(f"Usuario voluntario ya existe: {volunteer_user.username}")

def main():
    """Función principal del script."""
    print("Configurando grupos de permisos para Canicross...")
    print(f"Fecha y hora de configuración: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Crear todos los grupos con sus permisos
    superadmin_group = create_superadmin_group()
    organizer_group = create_organizer_group()
    reg_manager_group = create_registration_manager_group()
    vet_group = create_veterinary_group()
    judge_group = create_judge_group()
    timekeeper_group = create_timekeeper_group()
    participant_group = create_participant_group()
    volunteer_group = create_volunteer_group()
    
    # Crear usuarios de ejemplo si se solicita
    if len(sys.argv) > 1 and sys.argv[1] == '--create-users':
        create_sample_users()
        
        # Asignar usuarios a grupos
        User.objects.get(username='admin_example').groups.add(superadmin_group)
        User.objects.get(username='organizer_example').groups.add(organizer_group)
        User.objects.get(username='regmanager_example').groups.add(reg_manager_group)
        User.objects.get(username='vet_example').groups.add(vet_group)
        User.objects.get(username='judge_example').groups.add(judge_group)
        User.objects.get(username='timekeeper_example').groups.add(timekeeper_group)
        User.objects.get(username='participant_example').groups.add(participant_group)
        User.objects.get(username='volunteer_example').groups.add(volunteer_group)
        
        print("\nUsuarios de ejemplo creados y asignados a sus respectivos grupos.")
    
    # Imprimir resumen de permisos
    print_group_permissions(superadmin_group)
    print_group_permissions(organizer_group)
    print_group_permissions(reg_manager_group)
    print_group_permissions(vet_group)
    print_group_permissions(judge_group)
    print_group_permissions(timekeeper_group)
    print_group_permissions(participant_group)
    print_group_permissions(volunteer_group)
    
    print("\nConfiguración de permisos completada correctamente.")

if __name__ == "__main__":
    main()