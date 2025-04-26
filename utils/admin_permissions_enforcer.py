"""
Utilidad para monitorear y hacer cumplir los permisos del grupo de administradores.
Este módulo verifica periódicamente que los permisos del grupo de administradores
coincidan con los guardados y corrige cualquier diferencia.
"""
import os
import json
import threading
import time
from pathlib import Path
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.core.signals import request_finished
from django.dispatch import receiver
import logging

# Configuración
CONFIG_FILE = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'admin_permissions.json'
ADMIN_GROUP_NAME = 'Administradores'
CHECK_INTERVAL = 300  # Intervalo de verificación en segundos (5 minutos)

# Configurar logger
logger = logging.getLogger('utils.admin_permissions')

class AdminPermissionsEnforcer:
    """Clase que monitorea y hace cumplir los permisos del grupo de administradores."""
    
    def __init__(self):
        self.monitoring_active = False
        self.thread = None
        self.lock = threading.Lock()
        self.saved_permissions = None
        self.is_locked = False
        self.load_permissions()
    
    def load_permissions(self):
        """Carga los permisos guardados desde el archivo de configuración."""
        if not CONFIG_FILE.exists():
            logger.warning("Archivo de configuración de permisos no encontrado: %s", CONFIG_FILE)
            return False
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            
            self.is_locked = data.get('locked', False)
            self.saved_permissions = {perm['id'] for perm in data.get('permissions', [])}
            
            if self.is_locked:
                logger.info("Permisos de administrador cargados y bloqueados: %d permisos", 
                           len(self.saved_permissions))
            else:
                logger.info("Permisos de administrador cargados pero no bloqueados: %d permisos",
                           len(self.saved_permissions))
            
            return True
        except Exception as e:
            logger.error("Error al cargar permisos: %s", str(e))
            return False
    
    def enforce_permissions(self):
        """Verifica y corrige los permisos del grupo de administradores."""
        if not self.is_locked or not self.saved_permissions:
            return
        
        try:
            admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)
            current_permissions = set(admin_group.permissions.values_list('id', flat=True))
            
            # Verificar si faltan permisos o hay extras
            missing = self.saved_permissions - current_permissions
            extra = current_permissions - self.saved_permissions
            
            if missing or extra:
                logger.warning(
                    "Discrepancia en permisos de administrador: faltan %d, sobran %d. Restaurando...",
                    len(missing), len(extra)
                )
                
                with transaction.atomic():
                    # Restaurar permisos sin alterar los demás
                    for perm_id in missing:
                        try:
                            perm = Permission.objects.get(id=perm_id)
                            admin_group.permissions.add(perm)
                            logger.info("Permiso restaurado: %s", perm.codename)
                        except Permission.DoesNotExist:
                            logger.error("No se encontró el permiso con ID %d", perm_id)
                    
                    # No eliminamos permisos extras para permitir la flexibilidad
        
        except Group.DoesNotExist:
            logger.error("Grupo de administradores no encontrado")
        except Exception as e:
            logger.error("Error al verificar permisos: %s", str(e))
    
    def start_monitoring(self):
        """Inicia el monitoreo de permisos en un hilo separado."""
        if not self.is_locked:
            logger.info("Los permisos no están bloqueados, no se iniciará el monitoreo")
            return False
        
        with self.lock:
            if self.monitoring_active:
                logger.info("El monitoreo ya está activo")
                return True
            
            self.monitoring_active = True
            self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.thread.start()
            
            logger.info("Monitoreo de permisos de administrador iniciado")
            return True
    
    def stop_monitoring(self):
        """Detiene el monitoreo de permisos."""
        with self.lock:
            self.monitoring_active = False
            logger.info("Monitoreo de permisos de administrador detenido")
    
    def _monitoring_loop(self):
        """Bucle de monitoreo que se ejecuta en un hilo separado."""
        while self.monitoring_active:
            try:
                self.enforce_permissions()
            except Exception as e:
                logger.error("Error en el monitoreo de permisos: %s", str(e))
            
            # Dormir hasta la próxima verificación
            time.sleep(CHECK_INTERVAL)

# Instancia global del enforcer
_enforcer = AdminPermissionsEnforcer()

@receiver(request_finished)
def check_permissions_after_request(sender, **kwargs):
    """Verifica los permisos después de cada solicitud."""
    if _enforcer.is_locked and _enforcer.saved_permissions:
        try:
            admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)
            current_permissions = set(admin_group.permissions.values_list('id', flat=True))
            
            # Verificar si faltan permisos críticos
            missing = _enforcer.saved_permissions - current_permissions
            
            if missing:
                # Restaurar inmediatamente los permisos faltantes
                for perm_id in missing:
                    try:
                        perm = Permission.objects.get(id=perm_id)
                        admin_group.permissions.add(perm)
                        logger.warning("Permiso restaurado automáticamente: %s", perm.codename)
                    except Permission.DoesNotExist:
                        pass
        except Exception:
            # Ignorar errores, el monitoreo de fondo se encargará
            pass

# Funciones para usar desde otros módulos

def start_monitoring():
    """Inicia el monitoreo de permisos."""
    _enforcer.load_permissions()
    return _enforcer.start_monitoring()

def stop_monitoring():
    """Detiene el monitoreo de permisos."""
    return _enforcer.stop_monitoring()

def is_locked():
    """Comprueba si los permisos están bloqueados."""
    return _enforcer.is_locked

def get_saved_permissions():
    """Devuelve los permisos guardados."""
    return _enforcer.saved_permissions

# Inicializar monitoreo automático
start_monitoring()