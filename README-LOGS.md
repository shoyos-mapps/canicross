# Sistema de Logs de Canicross

Este documento describe el sistema de logs implementado en la aplicación Canicross, incluyendo la configuración, uso y herramientas de análisis.

## Estructura de Logs

Los logs se almacenan en el directorio `/logs` en la raíz del proyecto y se organizan por tipo:

- `info.log` - Información general de la aplicación
- `error.log` - Errores y excepciones
- `api.log` - Solicitudes a la API y su rendimiento
- `db.log` - Operaciones de base de datos
- `security.log` - Eventos relacionados con seguridad
- `ocr.log` - Operaciones OCR en el módulo veterinario

Cada archivo de log se rota automáticamente cuando alcanza 10MB, manteniendo hasta 10 versiones históricas.

## Niveles de Log

El sistema utiliza los siguientes niveles, en orden de severidad:

1. **ERROR** - Errores críticos que requieren atención inmediata
2. **WARNING** - Advertencias sobre problemas potenciales
3. **INFO** - Información general sobre el funcionamiento de la aplicación
4. **DEBUG** - Información detallada para depuración (solo activo en desarrollo)

## Cómo Agregar Logs en el Código

### 1. Importar las utilidades de log

```python
from utils.logger import get_logger, log_function_call, log_exception, log_db_operation
```

### 2. Crear un logger para el módulo

```python
logger = get_logger('nombre_del_modulo')
```

### 3. Agregar logs en funciones y vistas

```python
# Log básico
logger.info("Mensaje informativo")
logger.warning("Advertencia importante")
logger.error("Error crítico")

# Con contexto adicional
logger.info(f"Usuario {request.user} ha iniciado el proceso {proceso}")
```

### 4. Capturar excepciones

```python
try:
    # código que puede fallar
except Exception as e:
    log_exception(logger, "Error al procesar datos")
    raise  # Opcional: re-lanzar la excepción
```

### 5. Usar decoradores para funciones

```python
@log_function_call(logger)
def mi_funcion():
    # Esta función será automáticamente logueada
    pass

@log_db_operation(logger)
def guardar_en_db():
    # Esta función de DB será logueada con métricas de rendimiento
    pass
```

## Herramientas de Análisis

### Panel de Administración

El sistema incluye un visor de logs en el panel de administración accesible en:
`/admin/logs/`

Características:
- Visualización de todos los archivos de log
- Filtrado por nivel y texto
- Resumen de errores con gráficos
- Métricas de rendimiento
- Exportación a CSV y JSON

### Analizador de Línea de Comandos

Se incluye un script `log_analyzer.py` en el directorio `utils` para analizar logs desde la terminal:

```bash
# Ver ayuda
python utils/log_analyzer.py -h

# Listar archivos de log disponibles
python utils/log_analyzer.py list

# Buscar patrones en logs
python utils/log_analyzer.py search -p "texto a buscar" -l ERROR

# Ver resumen de errores de los últimos 7 días
python utils/log_analyzer.py errors -d 7

# Ver métricas de rendimiento
python utils/log_analyzer.py metrics -d 30

# Monitorizar logs en tiempo real (como tail -f)
python utils/log_analyzer.py monitor -f api.log -l ERROR
```

## Middleware

El sistema incluye middleware para monitorizar automáticamente las solicitudes:

1. **RequestLoggingMiddleware** - Registra todas las solicitudes HTTP
2. **PerformanceMonitoringMiddleware** - Identifica solicitudes lentas

## Configuración

La configuración de logs se encuentra en `canicross_project/logging_config.py` y puede ser ajustada según las necesidades.

Para cambiar el nivel de log en producción, modifique las variables de entorno:

```
DEBUG=False          # Desactiva los logs de consola en producción
DEBUG_DB=True        # Activa logs detallados de base de datos
```

## Buenas Prácticas

1. **Usar el logger correcto** para cada módulo
2. **Incluir contexto** suficiente en los mensajes de log
3. **No loguear información sensible** como contraseñas o tokens
4. **Usar el nivel adecuado** para cada mensaje
5. **Agrupar logs relacionados** para facilitar el análisis
6. **Revisar regularmente** los logs de errores

## Rotación y Limpieza

Los logs se rotan automáticamente, pero en servidores de producción se recomienda:

1. Configurar un trabajo cron para comprimir logs antiguos
2. Establecer políticas de retención (ej. mover logs de más de 90 días a almacenamiento frío)
3. Monitorizar el espacio en disco del directorio de logs