#!/usr/bin/env python
"""
Script para bloquear/desbloquear los permisos del grupo de Administradores.
Este script se ejecuta después de configurar los permisos iniciales.
"""
import os
import django
import sys
import json
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.db import transaction

# Definir archivo de configuración para almacenar los permisos bloqueados
CONFIG_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / 'admin_permissions.json'

def get_admin_group():
    """Obtiene el grupo de administradores o devuelve None."""
    try:
        return Group.objects.get(name='Administradores')
    except Group.DoesNotExist:
        return None

def lock_permissions():
    """Guarda y bloquea los permisos actuales del grupo Administradores."""
    admin_group = get_admin_group()
    if not admin_group:
        print("Error: El grupo 'Administradores' no existe")
        return False
    
    # Obtener permisos actuales
    permission_ids = list(admin_group.permissions.values_list('id', flat=True))
    permission_data = []
    
    for perm in Permission.objects.filter(id__in=permission_ids):
        permission_data.append({
            'id': perm.id,
            'name': perm.name,
            'codename': perm.codename,
            'content_type': f"{perm.content_type.app_label}.{perm.content_type.model}"
        })
    
    # Guardar en archivo de configuración
    data = {
        'locked': True,
        'permissions': permission_data
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"🔒 Se han bloqueado {len(permission_data)} permisos para el grupo 'Administradores'")
    print(f"Los permisos se han guardado en {CONFIG_FILE}")
    return True

def unlock_permissions():
    """Desbloquea los permisos del grupo Administradores."""
    if not CONFIG_FILE.exists():
        print("Error: No hay permisos bloqueados previamente")
        return False
    
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)
    
    # Marcar como desbloqueado
    data['locked'] = False
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("🔓 Los permisos del grupo 'Administradores' han sido desbloqueados")
    print("Los permisos pueden ser modificados ahora")
    return True

def check_permissions():
    """Verifica si los permisos actuales coinciden con los guardados."""
    admin_group = get_admin_group()
    if not admin_group:
        print("Error: El grupo 'Administradores' no existe")
        return False
    
    if not CONFIG_FILE.exists():
        print("No hay archivo de configuración de permisos")
        return False
    
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)
    
    locked = data.get('locked', False)
    status = "🔒 Bloqueados" if locked else "🔓 Desbloqueados"
    print(f"Estado de los permisos: {status}")
    
    # Obtener permisos actuales
    current_permissions = set(admin_group.permissions.values_list('id', flat=True))
    saved_permissions = {perm['id'] for perm in data.get('permissions', [])}
    
    # Verificar diferencias
    missing = saved_permissions - current_permissions
    extra = current_permissions - saved_permissions
    
    if missing:
        print(f"⚠️ Faltan {len(missing)} permisos que deberían estar asignados")
    
    if extra:
        print(f"ℹ️ Hay {len(extra)} permisos adicionales asignados")
    
    if not missing and not extra:
        print("✅ Los permisos coinciden exactamente con los guardados")
    
    return True

def restore_permissions():
    """Restaura los permisos guardados al grupo Administradores."""
    admin_group = get_admin_group()
    if not admin_group:
        print("Error: El grupo 'Administradores' no existe")
        return False
    
    if not CONFIG_FILE.exists():
        print("Error: No hay permisos guardados para restaurar")
        return False
    
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)
    
    permission_ids = [perm['id'] for perm in data.get('permissions', [])]
    
    if not permission_ids:
        print("Error: No hay permisos para restaurar")
        return False
    
    # Restaurar permisos
    with transaction.atomic():
        # Limpiar permisos actuales
        admin_group.permissions.clear()
        
        # Asignar permisos guardados
        for perm_id in permission_ids:
            try:
                perm = Permission.objects.get(id=perm_id)
                admin_group.permissions.add(perm)
            except Permission.DoesNotExist:
                print(f"⚠️ No se pudo encontrar el permiso con ID {perm_id}")
    
    print(f"✅ Se han restaurado {len(permission_ids)} permisos al grupo 'Administradores'")
    return True

def show_permissions():
    """Muestra los permisos bloqueados."""
    if not CONFIG_FILE.exists():
        print("No hay permisos bloqueados")
        return False
    
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)
    
    locked = data.get('locked', False)
    status = "bloqueados" if locked else "no bloqueados"
    permissions = data.get('permissions', [])
    
    print(f"Permisos {status} del grupo 'Administradores' ({len(permissions)}):")
    
    # Agrupar por tipo de contenido
    by_content_type = {}
    for perm in permissions:
        content_type = perm['content_type']
        if content_type not in by_content_type:
            by_content_type[content_type] = []
        by_content_type[content_type].append(perm)
    
    # Mostrar permisos agrupados
    for content_type, perms in sorted(by_content_type.items()):
        print(f"\n{content_type.split('.')[-1].capitalize()}:")
        for perm in sorted(perms, key=lambda p: p['codename']):
            print(f"  - {perm['codename']}")
    
    return True

def main():
    """Función principal del script."""
    if len(sys.argv) < 2:
        print("Uso: python lock_admin_permissions.py [lock|unlock|check|restore|show]")
        return False
    
    action = sys.argv[1].lower()
    
    if action == 'lock':
        return lock_permissions()
    elif action == 'unlock':
        return unlock_permissions()
    elif action == 'check':
        return check_permissions()
    elif action == 'restore':
        return restore_permissions()
    elif action == 'show':
        return show_permissions()
    else:
        print(f"Acción no válida: {action}")
        print("Uso: python lock_admin_permissions.py [lock|unlock|check|restore|show]")
        return False

# Cuando se ejecuta como script
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)