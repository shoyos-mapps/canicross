"""
Utilidades para el registro de logs en Canicross.
Proporciona funciones de ayuda para registrar logs en toda la aplicación.
"""
import logging
import traceback
import json
import os
from functools import wraps
import time

def get_logger(module_name):
    """
    Obtiene un logger para un módulo específico.
    
    Args:
        module_name (str): Nombre del módulo para el logger.
        
    Returns:
        Logger: Instancia de logger configurada.
    """
    return logging.getLogger(module_name)

def log_exception(logger, message="Se ha producido una excepción", exc_info=None):
    """
    Registra una excepción con detalles completos.
    
    Args:
        logger (Logger): Logger para registrar la excepción.
        message (str): Mensaje descriptivo.
        exc_info (Exception, optional): Información de la excepción. Si es None, se obtiene del traceback actual.
    """
    stack_trace = traceback.format_exc()
    logger.error(f"{message}: {stack_trace}")

def log_api_request(logger, request, response=None, duration=None):
    """
    Registra detalles de una solicitud API.
    
    Args:
        logger (Logger): Logger para registrar la información.
        request (HttpRequest): Objeto de solicitud HTTP.
        response (HttpResponse, optional): Objeto de respuesta HTTP.
        duration (float, optional): Duración de la solicitud en segundos.
    """
    log_data = {
        'method': request.method,
        'path': request.path,
        'user': str(request.user) if request.user.is_authenticated else 'anonymous',
        'ip': get_client_ip(request),
    }
    
    # Añadir datos de consulta si existen
    if request.GET:
        log_data['query_params'] = dict(request.GET)
    
    # Añadir datos de formulario si existen y no son sensibles
    if request.POST and is_safe_to_log(request.path):
        log_data['form_data'] = dict(request.POST)
    
    # Añadir detalles de respuesta si existe
    if response:
        log_data['status_code'] = response.status_code
        
        # Log respuestas de error con más detalle
        if response.status_code >= 400:
            logger.warning(f"Error API {response.status_code}: {json.dumps(log_data)}")
        else:
            logger.info(f"API Request: {json.dumps(log_data)}")
    else:
        logger.info(f"API Request: {json.dumps(log_data)}")
    
    # Registrar duración si se proporciona
    if duration:
        logger.info(f"API Request duración: {duration:.3f}s - {request.method} {request.path}")

def get_client_ip(request):
    """
    Obtiene la dirección IP del cliente.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        
    Returns:
        str: Dirección IP del cliente.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def is_safe_to_log(path):
    """
    Determina si una ruta es segura para registrar datos de formulario.
    Evita registrar datos de rutas con información sensible.
    
    Args:
        path (str): Ruta URL.
        
    Returns:
        bool: True si es seguro registrar, False en caso contrario.
    """
    sensitive_paths = [
        '/accounts/login',
        '/accounts/register',
        '/api/v1/auth',
    ]
    
    for sensitive_path in sensitive_paths:
        if sensitive_path in path:
            return False
    return True

def log_function_call(logger):
    """
    Decorador para registrar llamadas a funciones.
    
    Args:
        logger (Logger): Logger para registrar la información.
    
    Returns:
        function: Función decorada.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            logger.debug(f"Iniciando {func_name}()")
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                
                logger.debug(f"Finalizado {func_name}() - Duración: {duration:.3f}s")
                return result
            except Exception as e:
                logger.error(f"Error en {func_name}(): {str(e)}")
                log_exception(logger, f"Excepción en {func_name}()")
                raise
        
        return wrapper
    
    return decorator

def log_db_operation(logger):
    """
    Decorador para registrar operaciones de base de datos.
    
    Args:
        logger (Logger): Logger para registrar la información.
    
    Returns:
        function: Función decorada.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            logger.debug(f"DB Operation - Starting {func_name}()")
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                
                if duration > 1.0:  # Log operaciones lentas
                    logger.warning(f"DB Operation Slow - {func_name}() - Duration: {duration:.3f}s")
                else:
                    logger.debug(f"DB Operation - Completed {func_name}() - Duration: {duration:.3f}s")
                    
                return result
            except Exception as e:
                logger.error(f"DB Operation Error - {func_name}(): {str(e)}")
                log_exception(logger, f"DB Exception in {func_name}()")
                raise
        
        return wrapper
    
    return decorator