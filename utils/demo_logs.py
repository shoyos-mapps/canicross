#!/usr/bin/env python
"""
Script de demostración del sistema de logs de Canicross.
Este script genera entradas de log de ejemplo para demostrar las capacidades del sistema.

Uso:
    python utils/demo_logs.py
"""
import os
import sys
import random
import time
import traceback
from datetime import datetime, timedelta

# Agregar directorio del proyecto al path para importar módulos
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canicross_project.settings')
import django
django.setup()

# Importar utilidades de logging
from utils.logger import get_logger, log_exception, log_function_call, log_db_operation

# Obtener loggers para diferentes módulos
main_logger = get_logger('canicross')
events_logger = get_logger('events')
api_logger = get_logger('api')
db_logger = get_logger('django.db.backends')
security_logger = get_logger('django.security')

# Datos de prueba
ENDPOINTS = [
    'GET /api/v1/events/',
    'GET /api/v1/events/1/',
    'POST /api/v1/registrations/',
    'GET /api/v1/participants/me/',
    'PUT /api/v1/participants/4/',
    'GET /api/v1/races/3/results/',
    'POST /api/v1/veterinary/approve/7/',
    'GET /api/v1/kits/pending/',
    'POST /api/v1/checkin/8/',
    'GET /api/v1/dashboard/',
]

USERS = ['admin', 'juan.perez', 'maria.lopez', 'carlos.rodriguez', 'ana.martinez']

ERROR_MESSAGES = [
    'Error al procesar el documento: formato no compatible',
    'No se pudo conectar con el servicio de OCR',
    'Error de validación: los campos obligatorios están vacíos',
    'Excepción en la base de datos: restricción de clave externa violada',
    'Tiempo de espera agotado al intentar enviar el correo electrónico',
    'Error 500: Excepción no controlada en procesamiento de pago',
    'División por cero en cálculo de resultados',
    'Error al generar PDF de certificado: plantilla no encontrada',
    'Índice fuera de rango al procesar lista de participantes',
    'Error de autenticación: token inválido',
]

def generate_random_ip():
    """Genera una dirección IP aleatoria."""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def generate_random_user_agent():
    """Genera un User-Agent aleatorio."""
    browsers = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    ]
    return random.choice(browsers)

@log_function_call(main_logger)
def generate_info_logs(count=50):
    """Genera logs de información general."""
    main_logger.info(f"Iniciando generación de {count} logs de información")
    
    for i in range(count):
        logger = random.choice([main_logger, events_logger])
        user = random.choice(USERS)
        
        messages = [
            f"Usuario {user} ha iniciado sesión",
            f"Página de eventos visualizada por {user}",
            f"Búsqueda realizada con filtros: categoria=adult, distancia=5km",
            f"Correo electrónico enviado a {user}@example.com",
            f"Inscripción completada para el evento 'Canicross Madrid 2025'",
            f"Documento subido: passport_dog_{random.randint(1000, 9999)}.pdf",
            f"Cambio de contraseña realizado para {user}",
            f"Nuevo comentario añadido en el evento 'Canicross Barcelona 2025'",
            f"Recordatorio de evento enviado a {random.randint(50, 200)} participantes",
            f"Configuración de perfil actualizada por {user}",
        ]
        
        logger.info(random.choice(messages))
        
        # Añadir pequeña pausa aleatoria para simular actividad real
        time.sleep(random.uniform(0.01, 0.05))
    
    main_logger.info(f"Completada generación de {count} logs de información")

@log_function_call(main_logger)
def generate_warning_logs(count=20):
    """Genera logs de advertencia."""
    main_logger.info(f"Iniciando generación de {count} logs de advertencia")
    
    for i in range(count):
        logger = random.choice([main_logger, events_logger, security_logger])
        
        messages = [
            "Intento de acceso con credenciales incorrectas",
            f"Documento sospechoso detectado: ID-{random.randint(1000, 9999)}.jpg",
            "Base de datos cercana a su capacidad máxima (85%)",
            f"Demasiadas solicitudes desde IP {generate_random_ip()}",
            "Solicitud lenta detectada (> 2s) en endpoint de resultados",
            "Certificado SSL expirará en 15 días",
            "Memoria del servidor por encima del 90%",
            "Imagen de perro no cumple con los requisitos mínimos",
            "Error de validación en formulario de inscripción",
            "Caché de aplicación lleno, rendimiento degradado",
        ]
        
        logger.warning(random.choice(messages))
        
        # Añadir pequeña pausa aleatoria
        time.sleep(random.uniform(0.05, 0.1))
    
    main_logger.info(f"Completada generación de {count} logs de advertencia")

@log_function_call(main_logger)
def generate_error_logs(count=10):
    """Genera logs de error."""
    main_logger.info(f"Iniciando generación de {count} logs de error")
    
    for i in range(count):
        logger = random.choice([main_logger, events_logger, db_logger])
        error_msg = random.choice(ERROR_MESSAGES)
        
        try:
            # Simular una excepción
            if random.random() < 0.3:
                # 30% de las veces, generar una excepción real
                raise Exception(error_msg)
            else:
                # El resto, solo registrar el error
                logger.error(error_msg)
        except Exception as e:
            log_exception(logger, f"Excepción capturada: {str(e)}")
        
        # Añadir pausa más larga para errores
        time.sleep(random.uniform(0.1, 0.2))
    
    main_logger.info(f"Completada generación de {count} logs de error")

@log_function_call(main_logger)
def generate_api_logs(count=100):
    """Genera logs de solicitudes API."""
    main_logger.info(f"Iniciando generación de {count} logs de API")
    
    for i in range(count):
        endpoint = random.choice(ENDPOINTS)
        method = endpoint.split(' ')[0]
        path = endpoint.split(' ')[1]
        user = random.choice(USERS)
        ip = generate_random_ip()
        user_agent = generate_random_user_agent()
        duration = random.uniform(0.05, 3.0)  # Entre 50ms y 3s
        status_code = random.choices([200, 201, 400, 401, 403, 404, 500], 
                                    weights=[70, 10, 5, 5, 3, 5, 2])[0]
        
        # Crear objetos mock para simular request/response
        class MockRequest:
            def __init__(self):
                self.method = method
                self.path = path
                self.user = type('obj', (object,), {
                    'is_authenticated': True,
                    '__str__': lambda self: user
                })
                self.GET = {}
                self.POST = {}
                self.META = {
                    'REMOTE_ADDR': ip,
                    'HTTP_USER_AGENT': user_agent,
                    'HTTP_X_FORWARDED_FOR': None
                }
        
        class MockResponse:
            def __init__(self):
                self.status_code = status_code
        
        # Registrar la solicitud API
        from utils.logger import log_api_request
        log_api_request(api_logger, MockRequest(), MockResponse(), duration)
        
        # Añadir pequeña pausa aleatoria
        time.sleep(random.uniform(0.01, 0.05))
    
    main_logger.info(f"Completada generación de {count} logs de API")

@log_function_call(main_logger)
@log_db_operation(db_logger)
def generate_db_logs(count=30):
    """Genera logs de operaciones de base de datos."""
    main_logger.info(f"Iniciando generación de {count} logs de base de datos")
    
    for i in range(count):
        # Simular una operación de base de datos
        operation = random.choice([
            "SELECT", "INSERT", "UPDATE", "DELETE", "JOIN"
        ])
        table = random.choice([
            "events_event", "events_race", "participants_participant", 
            "participants_dog", "registrations_registration"
        ])
        
        duration = random.uniform(0.01, 1.5)  # Entre 10ms y 1.5s
        
        if operation == "SELECT":
            query = f"SELECT * FROM {table} WHERE id = {random.randint(1, 100)}"
        elif operation == "INSERT":
            query = f"INSERT INTO {table} (name, created_at) VALUES ('Test', NOW())"
        elif operation == "UPDATE":
            query = f"UPDATE {table} SET updated_at = NOW() WHERE id = {random.randint(1, 100)}"
        elif operation == "DELETE":
            query = f"DELETE FROM {table} WHERE id = {random.randint(1, 100)}"
        elif operation == "JOIN":
            query = f"SELECT r.*, e.name FROM {table} r JOIN events_event e ON r.event_id = e.id"
        
        # Registrar query (simulada)
        if duration > 1.0:
            db_logger.warning(f"Slow DB Query ({duration:.3f}s): {query}")
        else:
            db_logger.debug(f"DB Query ({duration:.3f}s): {query}")
        
        # Añadir pequeña pausa aleatoria
        time.sleep(random.uniform(0.05, 0.1))
    
    main_logger.info(f"Completada generación de {count} logs de base de datos")

def main():
    """Función principal para generar todos los logs de demostración."""
    start_time = time.time()
    main_logger.info("=== INICIANDO GENERACIÓN DE LOGS DE DEMOSTRACIÓN ===")
    
    # Generar diferentes tipos de logs
    generate_info_logs(50)
    generate_warning_logs(20)
    generate_error_logs(10)
    generate_api_logs(100)
    generate_db_logs(30)
    
    elapsed_time = time.time() - start_time
    main_logger.info(f"=== FINALIZADA GENERACIÓN DE LOGS DE DEMOSTRACIÓN (Tiempo: {elapsed_time:.2f}s) ===")
    
    print(f"""
Logs de demostración generados correctamente en el directorio 'logs/'.

Para ver los logs, puede usar:
- El panel de administración: http://192.168.193.200:7080/admin/logs/
- El analizador de línea de comandos: python utils/log_analyzer.py list

Logs generados:
- {50} logs de información
- {20} logs de advertencia
- {10} logs de error
- {100} logs de API
- {30} logs de base de datos

Tiempo total: {elapsed_time:.2f} segundos
""")

if __name__ == '__main__':
    main()