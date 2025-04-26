#!/usr/bin/env python
"""
Script que configura los permisos y luego activa la protección.
Este script combina la configuración de permisos con la activación de protección
para evitar problemas de dependencias circulares.
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

from django.core.cache import cache

# Desactivar todas las señales de protección temporalmente
_PROTECTION_ENABLED = False

# Ahora ejecutar la configuración de permisos
from setup_permission_groups import main as setup_permissions

def main():
    """Función principal que configura permisos y activa protección."""
    print("Configurando permisos y activando protección...")
    
    # Primero, ejecutar la configuración de permisos con la protección desactivada
    setup_permissions()
    
    # Ahora, activar la protección manualmente
    from django.contrib.auth.models import Group
    
    try:
        # Guardar los permisos actuales del grupo Administradores
        admin_group = Group.objects.get(name='Administradores')
        permissions = list(admin_group.permissions.values_list('id', flat=True))
        
        # Guardar en caché con tiempo de expiración infinito
        cache.set('admin_group_protected_permissions', permissions, None)
        
        print(f"\nSe han protegido {len(permissions)} permisos para el grupo de Administradores")
        print("La protección de permisos ha sido activada con éxito.")
        print("A partir de ahora, los permisos de administrador no podrán ser modificados.")
    except Group.DoesNotExist:
        print("Error: El grupo de Administradores no existe.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)