"""
Decoradores para la aplicación accounts.
Proporciona decoradores para controlar el acceso a las vistas basado en tipos de usuario.
"""
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from functools import wraps

def user_type_required(user_type):
    """
    Decorador que verifica si el usuario tiene un tipo específico.
    
    Args:
        user_type (str): Tipo de usuario requerido ('admin', 'staff', 'judge', 'veterinary', 'participant')
    
    Returns:
        function: Decorador que redirige a la página de inicio de sesión si el usuario no tiene el tipo requerido
    """
    def check_user_type(user):
        """Verifica el tipo de usuario"""
        if user.is_anonymous:
            return False
            
        if user_type == 'admin':
            return user.is_admin()
        elif user_type == 'staff':
            return user.is_staff_member()
        elif user_type == 'judge':
            return user.is_judge()
        elif user_type == 'veterinary':
            return user.is_veterinary()
        elif user_type == 'participant':
            return user.is_participant()
        else:
            # Si se proporciona un tipo no válido, devolvemos False por seguridad
            return False
    
    # Usamos user_passes_test para manejar la redirección al login
    return user_passes_test(check_user_type, login_url='accounts:login')

def admin_required(view_func):
    """Decorator para vistas que requieren acceso de administrador."""
    return user_type_required('admin')(view_func)

def staff_required(view_func):
    """Decorator para vistas que requieren acceso de staff."""
    return user_type_required('staff')(view_func)

def judge_required(view_func):
    """Decorator para vistas que requieren acceso de juez."""
    return user_type_required('judge')(view_func)

def veterinary_required(view_func):
    """Decorator para vistas que requieren acceso de veterinario."""
    return user_type_required('veterinary')(view_func)

def participant_required(view_func):
    """Decorator para vistas que requieren acceso de participante."""
    return user_type_required('participant')(view_func)

def access_forbidden_on_login(view_func):
    """
    Decorador que redirige a una sección específica según el tipo de usuario.
    Útil para evitar que usuarios ya logueados accedan a páginas como login o registro.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Ya has iniciado sesión.")
            if request.user.is_admin():
                return redirect('admin:index')
            elif request.user.is_veterinary():
                return redirect('veterinary:dashboard')
            elif request.user.is_judge():
                return redirect('results:dashboard')  # Ajustar según la URL correcta
            elif request.user.is_staff_member():
                return redirect('events:event_list')  # O a un dashboard de staff si existe
            else:
                return redirect('events:event_list')  # Participantes van al listado de eventos
        return view_func(request, *args, **kwargs)
    return _wrapped_view