"""
Middleware para Canicross.
Proporciona funcionalidad para interceptar y procesar solicitudes y respuestas.
"""
import time
import json
import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from .logger import log_api_request

class RequestLoggingMiddleware:
    """
    Middleware para registrar todas las solicitudes HTTP.
    
    Registra:
    - Método HTTP
    - Ruta
    - Tiempo de respuesta
    - Código de estado
    - IP del cliente
    - Usuario (si está autenticado)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('api')
    
    def __call__(self, request):
        # Registrar inicio de solicitud
        start_time = time.time()
        
        # Procesar la solicitud
        response = self.get_response(request)
        
        # Calcular duración
        duration = time.time() - start_time
        
        # Registrar solicitud y respuesta
        log_api_request(self.logger, request, response, duration)
        
        return response

class PerformanceMonitoringMiddleware:
    """
    Middleware para monitorizar el rendimiento.
    
    Registra una advertencia para solicitudes que toman demasiado tiempo.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('canicross')
        self.slow_threshold = 2.0  # segundos
    
    def __call__(self, request):
        # Registrar inicio de solicitud
        start_time = time.time()
        
        # Procesar la solicitud
        response = self.get_response(request)
        
        # Calcular duración
        duration = time.time() - start_time
        
        # Registrar advertencia si la solicitud es lenta
        if duration > self.slow_threshold:
            self.logger.warning(
                f"Solicitud lenta: {request.method} {request.path} "
                f"- Duración: {duration:.3f}s"
            )
        
        return response
        
class SessionTimeoutMiddleware:
    """
    Middleware para gestionar el tiempo de espera de sesión.
    Redirige al usuario a la página de eventos si su sesión ha expirado.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('accounts')
    
    def __call__(self, request):
        # Procesar la solicitud primero
        response = self.get_response(request)
        
        # No hacer nada si no hay usuario autenticado o si estamos en las páginas de login/logout
        if not request.user.is_authenticated or request.path.startswith('/accounts/login') or request.path.startswith('/accounts/logout'):
            return response
            
        # Si estamos aquí, la sesión sigue activa en el servidor
        # El tiempo de expiración se maneja en el cliente con JavaScript
        
        return response

class MobileCSRFMiddleware:
    """
    Middleware para manejar problemas de CSRF en dispositivos móviles.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('security')
    
    def __call__(self, request):
        # Procesar la solicitud
        response = self.get_response(request)
        return response
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Comprobar si es un dispositivo móvil (basado en User-Agent)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_agents = ['iphone', 'android', 'mobile', 'ipad', 'tablet']
        is_mobile = any(agent in user_agent for agent in mobile_agents)
        
        # Si es un dispositivo móvil y viene de hikers.mappsco.com, añadir dominio a los orígenes CSRF confiables
        if is_mobile and 'HTTP_HOST' in request.META and 'hikers.mappsco.com' in request.META['HTTP_HOST']:
            from django.conf import settings
            
            # Asegurar que el dominio está en CSRF_TRUSTED_ORIGINS
            if 'https://hikers.mappsco.com' not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.append('https://hikers.mappsco.com')
                self.logger.info("Añadido hikers.mappsco.com a CSRF_TRUSTED_ORIGINS para dispositivo móvil")
                
            # Registrar información para depuración
            self.logger.info(f"Solicitud desde dispositivo móvil: {request.path} - Método: {request.method}")
            if request.method == 'POST':
                self.logger.info(f"CSRF Token en solicitud: {'CSRF_COOKIE' in request.COOKIES}")
                self.logger.info(f"Referrer: {request.META.get('HTTP_REFERER', 'No referrer')}")
                self.logger.info(f"Origin: {request.META.get('HTTP_ORIGIN', 'No origin')}")
        
        return None

class CloudflareProxyMiddleware:
    """
    Middleware para manejar solicitudes a través de proxy de Cloudflare y otros proxies.
    Ajusta los encabezados para obtener la IP real del cliente y garantizar
    que las URLs se generen correctamente.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('canicross')
    
    def __call__(self, request):
        # Verificar si la solicitud viene a través de Cloudflare
        cloudflare_headers = [
            'CF-Connecting-IP',
            'CF-IPCountry',
            'CF-RAY'
        ]
        
        # Comprobar si alguno de los encabezados de Cloudflare está presente
        is_cloudflare = any(header in request.META for header in cloudflare_headers)
        
        # Comprobar si estamos en hikers.mappsco.com
        is_hikers_domain = 'HTTP_HOST' in request.META and 'hikers.mappsco.com' in request.META['HTTP_HOST']
        
        if is_cloudflare:
            # Registrar que estamos procesando una solicitud de Cloudflare
            self.logger.info(f"Solicitud a través de Cloudflare: {request.path}")
            
            # Establecer la dirección IP real si está disponible
            if 'HTTP_CF_CONNECTING_IP' in request.META:
                request.META['REMOTE_ADDR'] = request.META['HTTP_CF_CONNECTING_IP']
            
            # Establecer encabezados para X-Forwarded-Proto para HTTPS
            # Django usará estos encabezados con SECURE_PROXY_SSL_HEADER
            if 'HTTP_CF_VISITOR' in request.META:
                try:
                    cf_visitor = json.loads(request.META['HTTP_CF_VISITOR'])
                    if cf_visitor.get('scheme') == 'https':
                        request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
                except (json.JSONDecodeError, AttributeError):
                    pass
                    
            # Para asegurar que Django use HTTPS en las URLs generadas
            request.META['wsgi.url_scheme'] = 'https'
            
        elif is_hikers_domain:
            # Registrar que estamos procesando una solicitud desde hikers.mappsco.com
            self.logger.info(f"Solicitud a través de hikers.mappsco.com: {request.path}")
            
            # Configurar correctamente X-Forwarded-Proto para que Django use HTTPS
            request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
            
            # Para asegurar que Django use HTTPS en las URLs generadas
            request.META['wsgi.url_scheme'] = 'https'
            
            # Si hay encabezado X-Forwarded-For, usarlo para la IP real
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        
        # Procesar la solicitud
        response = self.get_response(request)
        
        # Asegurar que el dominio hikers.mappsco.com está permitido para CSRF
        if is_hikers_domain:
            response['Access-Control-Allow-Origin'] = 'https://hikers.mappsco.com'
            response['Access-Control-Allow-Credentials'] = 'true'
        
        return response