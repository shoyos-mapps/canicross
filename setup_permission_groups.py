#!/usr/bin/env python
"""
Script para configurar grupos de permisos para diferentes roles de usuario en Canicross.
Crea grupos para veterinarios y jueces con los permisos apropiados.
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from accounts.models import User
from participants.models import Dog, Participant
from events.models import Event, Race, RaceCategory, PenaltyType
from registrations.models import Registration, Document, ParticipantAnnotation
from veterinary.models import VeterinaryCheck, VaccinationRecord, MedicalAlert
from results.models import Result, TimeRecord, Penalty

def create_veterinary_group():
    """Crea o actualiza el grupo de veterinarios con los permisos necesarios."""
    vet_group, created = Group.objects.get_or_create(name='Veterinarios')
    
    # Limpiar permisos existentes si el grupo ya existía
    if not created:
        vet_group.permissions.clear()
        print("Grupo 'Veterinarios' existente encontrado y limpiado.")
    else:
        print("Grupo 'Veterinarios' creado.")
    
    # Añadir permisos para modelos específicos de veterinaria
    vet_models = [
        VeterinaryCheck,
        VaccinationRecord,
        MedicalAlert,
    ]
    
    # Permisos completos para los modelos de veterinaria
    for model in vet_models:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        vet_group.permissions.add(*permissions)
    
    # Permisos de lectura (y en algunos casos actualización) para modelos relacionados
    related_models = {
        # Modelo: (view, change, add, delete)
        Dog: (True, False, False, False),
        Participant: (True, False, False, False),
        Registration: (True, True, False, False),  # Pueden actualizar pero no crear/eliminar
        Document: (True, True, False, False),  # Pueden actualizar pero no crear/eliminar
    }
    
    for model, permissions_flags in related_models.items():
        view, change, add, delete = permissions_flags
        content_type = ContentType.objects.get_for_model(model)
        
        if view:
            perm = Permission.objects.get(content_type=content_type, codename=f"view_{model._meta.model_name}")
            vet_group.permissions.add(perm)
        
        if change:
            perm = Permission.objects.get(content_type=content_type, codename=f"change_{model._meta.model_name}")
            vet_group.permissions.add(perm)
        
        if add:
            perm = Permission.objects.get(content_type=content_type, codename=f"add_{model._meta.model_name}")
            vet_group.permissions.add(perm)
        
        if delete:
            perm = Permission.objects.get(content_type=content_type, codename=f"delete_{model._meta.model_name}")
            vet_group.permissions.add(perm)
    
    # Permiso de vista para eventos y carreras
    for model in [Event, Race]:
        content_type = ContentType.objects.get_for_model(model)
        perm = Permission.objects.get(content_type=content_type, codename=f"view_{model._meta.model_name}")
        vet_group.permissions.add(perm)
    
    print(f"Se han asignado {vet_group.permissions.count()} permisos al grupo 'Veterinarios'.")
    
    # Asignar usuarios existentes del tipo 'veterinary' al grupo
    vet_users = User.objects.filter(user_type='veterinary')
    for user in vet_users:
        user.groups.add(vet_group)
    
    print(f"Se han asignado {vet_users.count()} usuarios al grupo 'Veterinarios'.")
    return vet_group

def create_judge_group():
    """Crea o actualiza el grupo de jueces con los permisos necesarios."""
    judge_group, created = Group.objects.get_or_create(name='Jueces')
    
    # Limpiar permisos existentes si el grupo ya existía
    if not created:
        judge_group.permissions.clear()
        print("Grupo 'Jueces' existente encontrado y limpiado.")
    else:
        print("Grupo 'Jueces' creado.")
    
    # Añadir permisos para modelos específicos de jueces
    judge_models = [
        Result,
        TimeRecord,
        Penalty,
        ParticipantAnnotation,
    ]
    
    # Permisos completos para los modelos de jueces
    for model in judge_models:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        judge_group.permissions.add(*permissions)
    
    # Permisos de lectura para modelos relacionados
    related_models = {
        # Modelo: (view, change, add, delete)
        Dog: (True, False, False, False),
        Participant: (True, False, False, False),
        Registration: (True, True, False, False),  # Pueden actualizar para añadir penalizaciones
        Event: (True, False, False, False),
        Race: (True, False, False, False),
        RaceCategory: (True, False, False, False),
        PenaltyType: (True, False, False, False),
        VeterinaryCheck: (True, False, False, False),  # Solo lectura para saber si un perro está apto
    }
    
    for model, permissions_flags in related_models.items():
        view, change, add, delete = permissions_flags
        content_type = ContentType.objects.get_for_model(model)
        
        if view:
            perm = Permission.objects.get(content_type=content_type, codename=f"view_{model._meta.model_name}")
            judge_group.permissions.add(perm)
        
        if change:
            perm = Permission.objects.get(content_type=content_type, codename=f"change_{model._meta.model_name}")
            judge_group.permissions.add(perm)
        
        if add:
            perm = Permission.objects.get(content_type=content_type, codename=f"add_{model._meta.model_name}")
            judge_group.permissions.add(perm)
        
        if delete:
            perm = Permission.objects.get(content_type=content_type, codename=f"delete_{model._meta.model_name}")
            judge_group.permissions.add(perm)
    
    print(f"Se han asignado {judge_group.permissions.count()} permisos al grupo 'Jueces'.")
    
    # Asignar usuarios existentes del tipo 'judge' al grupo
    judge_users = User.objects.filter(user_type='judge')
    for user in judge_users:
        user.groups.add(judge_group)
    
    print(f"Se han asignado {judge_users.count()} usuarios al grupo 'Jueces'.")
    return judge_group

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
    # Crear un veterinario de ejemplo
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
    
    # Crear un juez de ejemplo
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

def main():
    """Función principal del script."""
    print("Configurando grupos de permisos para Canicross...")
    
    # Crear grupos
    vet_group = create_veterinary_group()
    judge_group = create_judge_group()
    
    # Crear usuarios de ejemplo si se solicita
    if len(sys.argv) > 1 and sys.argv[1] == '--create-users':
        create_sample_users()
        
        # Asignar usuarios a grupos
        vet_user = User.objects.get(username='vet_example')
        vet_user.groups.add(vet_group)
        
        judge_user = User.objects.get(username='judge_example')
        judge_user.groups.add(judge_group)
        
        print("\nUsuarios de ejemplo creados y asignados a sus respectivos grupos.")
    
    # Imprimir resumen de permisos
    print_group_permissions(vet_group)
    print_group_permissions(judge_group)
    
    print("\nConfiguración de permisos completada.")

if __name__ == "__main__":
    main()