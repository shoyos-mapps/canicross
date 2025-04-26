from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.http import urlencode
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
from utils.logger import get_logger, log_function_call, log_exception

logger = get_logger('accounts')

@log_function_call(logger)
def login_view(request):
    """
    Vista para la página de inicio de sesión.
    Permite iniciar sesión con correo electrónico.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Autenticar al usuario usando el email como nombre de usuario
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Iniciar sesión
            login(request, user)
            logger.info(f"Usuario {email} ha iniciado sesión correctamente")
            
            # Redireccionar al perfil del usuario
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                # Redireccionar al perfil del usuario
                return redirect('participants:profile')
        else:
            # Mostrar error
            logger.warning(f"Intento de inicio de sesión fallido para el usuario: {email}")
            messages.error(request, "Correo electrónico o contraseña incorrectos.")
    
    return render(request, 'accounts/login.html')

@log_function_call(logger)
def profile_view(request):
    """
    Vista para la página de perfil de usuario.
    Redirecciona al perfil de participante.
    """
    return redirect('participants:profile')
    
@log_function_call(logger)
def logout_view(request):
    """
    Vista personalizada para cerrar la sesión del usuario.
    Redirige a la página de eventos o a la URL especificada en next.
    """
    # Obtener información del usuario antes de cerrar la sesión
    username = request.user.username if request.user.is_authenticated else "Usuario"
    
    # Cerrar la sesión
    logout(request)
    
    # Registrar el logout
    logger.info(f"Usuario {username} ha cerrado sesión correctamente")
    
    # Redirigir a la URL especificada o a la página de eventos
    next_url = request.GET.get('next', '/events/')
    return redirect(next_url)

@log_function_call(logger)
def register_view(request):
    """
    Vista para la página de registro de nuevos usuarios.
    Usa el correo electrónico como nombre de usuario.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Verificar que las contraseñas coinciden
        if password != password_confirm:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'accounts/register.html')
            
        try:
            # Crear un nuevo usuario
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Verificar que el email no existe
            if User.objects.filter(email=email).exists():
                messages.error(request, "El correo electrónico ya está registrado.")
                return render(request, 'accounts/register.html')
                
            # Verificar que el email no existe como nombre de usuario
            if User.objects.filter(username=email).exists():
                messages.error(request, "El correo electrónico ya está registrado como nombre de usuario.")
                return render(request, 'accounts/register.html')
                
            # Crear el usuario usando el email como nombre de usuario
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            
            # Iniciar sesión
            login(request, user)
            
            logger.info(f"Nuevo usuario registrado: {email}")
            messages.success(request, "¡Registro completado con éxito! Ahora complete su perfil.")
            
            # Redireccionar al perfil para completar la información
            return redirect('participants:profile')
            
        except Exception as e:
            log_exception(logger, f"Error al registrar usuario: {str(e)}")
            messages.error(request, "Hubo un error al procesar su registro. Por favor, inténtelo de nuevo.")
    
    return render(request, 'accounts/register.html')

@require_POST
@login_required
def extend_session(request):
    """
    Vista para extender la sesión del usuario.
    """
    try:
        # La sesión se extiende automáticamente debido a SESSION_SAVE_EVERY_REQUEST = True
        request.session.modified = True
        
        # Registrar la extensión de sesión
        logger.info(f"Sesión extendida para el usuario: {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Session extended successfully',
            'timeout_minutes': getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30)
        })
    except Exception as e:
        log_exception(logger, f"Error al extender la sesión: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)