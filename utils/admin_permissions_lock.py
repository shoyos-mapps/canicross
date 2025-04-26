"""
Módulo para bloquear y proteger los permisos de administrador.
Impide la modificación o eliminación de permisos críticos para el grupo de Administradores.
"""
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import pre_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.core.cache import cache
import os
import threading

# Nombre del grupo de administradores protegido
ADMIN_GROUP_NAME = 'Administradores'

# Clave de caché para los permisos protegidos
ADMIN_PERMISSIONS_CACHE_KEY = 'admin_group_protected_permissions'

# Variable global para indicar si estamos en modo de configuración inicial
# (Permitirá la modificación durante la ejecución de setup_permission_groups.py)
_protection_enabled = True

# Thread local para hacer el contexto de configuración seguro entre hilos
_thread_local = threading.local()
_thread_local.initial_setup = False

def get_admin_group_permissions():
    """
    Obtiene los permisos del grupo de administradores desde la caché o la base de datos.
    """
    # Intentar obtener de la caché primero
    cached_permissions = cache.get(ADMIN_PERMISSIONS_CACHE_KEY)
    if cached_permissions is not None:
        return cached_permissions
    
    # Si no está en caché, obtener de la base de datos
    try:
        admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)
        permissions = list(admin_group.permissions.values_list('id', flat=True))
        # Guardar en caché por 12 horas
        cache.set(ADMIN_PERMISSIONS_CACHE_KEY, permissions, 60*60*12)
        return permissions
    except Group.DoesNotExist:
        return []

@receiver(pre_save, sender=Group)
def protect_admin_group(sender, instance, **kwargs):
    """
    Impide renombrar el grupo de Administradores.
    """
    # Si la protección está desactivada, permitir la operación
    if not is_protection_active():
        return
        
    try:
        if instance.id:  # Si es una actualización, no creación
            original = Group.objects.get(id=instance.id)
            if original.name == ADMIN_GROUP_NAME and instance.name != ADMIN_GROUP_NAME:
                raise PermissionDenied("El grupo de Administradores no puede ser renombrado.")
    except Group.DoesNotExist:
        pass

@receiver(pre_delete, sender=Group)
def prevent_admin_group_deletion(sender, instance, **kwargs):
    """
    Impide eliminar el grupo de Administradores.
    """
    # Si la protección está desactivada, permitir la operación
    if not is_protection_active():
        return
        
    if instance.name == ADMIN_GROUP_NAME:
        raise PermissionDenied("El grupo de Administradores no puede ser eliminado.")

def disable_protection():
    """
    Desactiva temporalmente la protección de permisos para operaciones administrativas.
    Debe usarse con with_protection_disabled() como context manager.
    """
    _thread_local.initial_setup = True
    
def enable_protection():
    """
    Reactiva la protección de permisos después de operaciones administrativas.
    """
    _thread_local.initial_setup = False

def with_protection_disabled():
    """
    Context manager para desactivar temporalmente la protección de permisos.
    
    Ejemplo:
        with with_protection_disabled():
            # Realizar operaciones que modifican permisos de admin
    """
    class ProtectionDisabler:
        def __enter__(self):
            disable_protection()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            enable_protection()
            
    return ProtectionDisabler()

def is_protection_active():
    """
    Verifica si la protección está activa.
    """
    # Si estamos en configuración inicial o la protección está desactivada
    if getattr(_thread_local, 'initial_setup', False) or not _protection_enabled:
        return False
    return True

@receiver(m2m_changed, sender=Group.permissions.through)
def prevent_admin_permissions_change(sender, instance, action, pk_set, **kwargs):
    """
    Impide modificar los permisos del grupo de Administradores.
    """
    # Si la protección está desactivada, permitir la operación
    if not is_protection_active():
        return
        
    if instance.name == ADMIN_GROUP_NAME and action in ('pre_remove', 'pre_clear'):
        admin_permissions = get_admin_group_permissions()
        
        # Si es pre_remove, verificamos que no se estén eliminando permisos protegidos
        if action == 'pre_remove' and pk_set:
            # Comprobar si se intenta eliminar algún permiso protegido
            for perm_id in pk_set:
                if perm_id in admin_permissions:
                    raise PermissionDenied(
                        "No se pueden eliminar permisos del grupo de Administradores."
                    )

        # Si es pre_clear, nunca permitimos limpiar todos los permisos
        if action == 'pre_clear':
            raise PermissionDenied(
                "No se pueden eliminar todos los permisos del grupo de Administradores."
            )

# Funciones para configuración inicial del sistema

def protect_current_admin_permissions():
    """
    Función para guardar y proteger los permisos actuales del grupo de administradores.
    Esta función debe llamarse justo después de setup_permission_groups.py
    """
    try:
        admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)
        permissions = list(admin_group.permissions.values_list('id', flat=True))
        cache.set(ADMIN_PERMISSIONS_CACHE_KEY, permissions, None)  # No expira
        
        # A partir de ahora, activamos la protección
        enable_protection()
        
        return f"Se han protegido {len(permissions)} permisos para el grupo de Administradores"
    except Group.DoesNotExist:
        return "Error: El grupo de Administradores no existe"