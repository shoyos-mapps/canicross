from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import User

# Verificar si el módulo de protección está disponible
try:
    from utils.admin_permissions_enforcer import is_locked, get_saved_permissions
    PROTECTION_ENABLED = True
except ImportError:
    PROTECTION_ENABLED = False

class UserAdmin(BaseUserAdmin):
    """Administrador personalizado para nuestro modelo User."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    def get_readonly_fields(self, request, obj=None):
        """
        Hace que user_type, is_superuser y user_permissions sean de solo lectura 
        si el usuario es un administrador.
        """
        readonly_fields = super().get_readonly_fields(request, obj)
        
        if obj and (obj.user_type == 'admin' or obj.is_superuser):
            return readonly_fields + ('user_type', 'is_superuser', 'user_permissions', 'groups')
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        """
        Protege a los usuarios administradores de cambios en permisos críticos.
        """
        if change and obj.id:  # Si es una modificación a un usuario existente
            original = self.model.objects.get(id=obj.id)
            
            # Proteger el tipo de usuario 'admin' y superuser status
            if original.user_type == 'admin' or original.is_superuser:
                obj.user_type = original.user_type
                obj.is_superuser = original.is_superuser
                obj.is_staff = True  # Los admins siempre son staff
                
                # Asegurar que pertenezca al grupo de Administradores
                try:
                    admin_group = Group.objects.get(name='Administradores')
                    if admin_group not in obj.groups.all():
                        obj.groups.add(admin_group)
                    
                    # Mensaje de información
                    messages.warning(request, 
                        "Los usuarios administradores no pueden ser degradados a roles inferiores " 
                        "por razones de seguridad."
                    )
                except Group.DoesNotExist:
                    pass
        
        super().save_model(request, obj, form, change)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información personal'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')}),
        (_('Tipo y permisos'), {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Nota: El tipo de usuario y permisos de administradores no pueden ser modificados para proteger la integridad del sistema.',
        }),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'user_type'),
        }),
    )

class CustomGroupAdmin(BaseGroupAdmin):
    """Administrador personalizado para grupos con lista de usuarios."""
    
    # Añadimos conteo de usuarios a la lista
    list_display = ('name', 'user_count', 'is_protected')
    
    def user_count(self, obj):
        """Muestra el número de usuarios en el grupo"""
        count = User.objects.filter(groups=obj).count()
        return f"{count} usuario{'s' if count != 1 else ''}"
    
    user_count.short_description = "Nº de usuarios"
    
    def is_protected(self, obj):
        """Indica si el grupo está protegido contra modificaciones"""
        if obj.name == 'Administradores':
            return format_html('<span style="color: #d00; font-weight: bold;">Sí</span>')
        return 'No'
    
    is_protected.short_description = "Protegido"
    
    def users_in_group(self, obj):
        """Muestra los usuarios que pertenecen a este grupo con enlaces."""
        try:
            # Obtener usuarios en el grupo
            users = User.objects.filter(groups=obj).order_by('username')
            
            if not users.exists():
                return format_html("No hay usuarios en este grupo")
            
            # Crear lista HTML
            html_list = "<ul>"
            for user in users:
                html_list += f'<li><a href="/admin/accounts/user/{user.pk}/change/">{user.username}</a>'
                
                # Añadir información básica
                if user.get_full_name():
                    html_list += f' - {user.get_full_name()}'
                
                html_list += f' ({user.user_type})</li>'
                
            html_list += "</ul>"
            
            return format_html(html_list)
            
        except Exception as e:
            # En caso de error, mostrar un mensaje genérico
            return format_html("Error al cargar usuarios: {}", str(e))
    
    users_in_group.short_description = "Usuarios en este grupo"
    
    def get_readonly_fields(self, request, obj=None):
        """
        Hace que el nombre y los permisos sean de solo lectura si es el grupo de administradores.
        """
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.name == 'Administradores':
            return ('name', 'permissions', 'users_in_group')
        return readonly_fields + ('users_in_group',)
    
    def has_delete_permission(self, request, obj=None):
        """Impide eliminar el grupo de administradores"""
        if obj and obj.name == 'Administradores':
            return False
        return super().has_delete_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        """
        Protege al grupo de administradores de cambios en nombre o permisos.
        """
        if change and obj.id:  # Si es una modificación a un grupo existente
            try:
                original = self.model.objects.get(id=obj.id)
                if original.name == 'Administradores':
                    # No permitir cambios en el nombre
                    obj.name = 'Administradores'
                    
                    # Verificar si los permisos están bloqueados
                    if PROTECTION_ENABLED and is_locked():
                        messages.warning(request, 
                            "Los permisos del grupo 'Administradores' están bloqueados por seguridad. "
                            "Cualquier modificación será revertida automáticamente."
                        )
            except self.model.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)
        
        # Después de guardar, verificar si se debe actualizar la configuración
        if change and obj.name == 'Administradores' and PROTECTION_ENABLED and is_locked():
            from lock_admin_permissions import lock_permissions
            # Actualizar la configuración con los permisos actuales
            lock_permissions()
    
    # Usamos campos simplificados en las fieldsets
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Permisos', {
            'fields': ('permissions',),
            'description': 'Nota: Los permisos del grupo Administradores no pueden ser modificados para proteger la integridad del sistema.',
        }),
        ('Miembros', {'fields': ('users_in_group',), 'description': 'Usuarios asignados a este grupo'}),
    )

# Registramos el modelo User para usar con el admin predeterminado (por si acaso)
admin.site.register(User, UserAdmin)

# No registramos Group aquí, ya que lo haremos en canicross_admin
# admin.site.register(Group, CustomGroupAdmin)  # Comentado para evitar error de doble registro
