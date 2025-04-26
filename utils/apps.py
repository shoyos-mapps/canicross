"""
Configuración de la aplicación de utilidades.
"""
from django.apps import AppConfig

class UtilsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utils'
    
    def ready(self):
        """
        Importar las señales y métodos de protección de permisos al iniciar la aplicación.
        """
        import utils.admin_permissions_lock