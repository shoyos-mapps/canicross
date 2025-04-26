"""
Utilidad para visualizar y analizar logs de la aplicación Canicross.
Proporciona funciones para acceder a los logs desde el panel de administración.
"""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import gzip
from collections import Counter, defaultdict
import logging

from django.conf import settings

# Path base de logs
LOGS_DIR = Path(settings.BASE_DIR) / 'logs'

def get_log_files():
    """
    Obtiene la lista de archivos de log disponibles.
    
    Returns:
        list: Lista de archivos de log, incluyendo los archivos rotados.
    """
    if not LOGS_DIR.exists():
        return []
        
    log_files = []
    for file in LOGS_DIR.glob('*.log*'):
        log_files.append(str(file.relative_to(LOGS_DIR)))
    
    return sorted(log_files)

def read_log_file(filename, num_lines=1000, filter_text=None, level=None):
    """
    Lee un archivo de log y devuelve las líneas especificadas.
    
    Args:
        filename (str): Nombre del archivo de log.
        num_lines (int, optional): Número de líneas a leer desde el final. Por defecto 1000.
        filter_text (str, optional): Texto para filtrar las líneas. Por defecto None.
        level (str, optional): Nivel de log para filtrar (ERROR, WARNING, INFO, DEBUG). Por defecto None.
        
    Returns:
        list: Lista de líneas del archivo de log.
    """
    filepath = LOGS_DIR / filename
    
    if not filepath.exists():
        return []
    
    # Detectar si es un archivo comprimido
    is_gzip = str(filepath).endswith('.gz')
    
    # Leer el archivo
    lines = []
    try:
        if is_gzip:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
    except Exception as e:
        return [f"Error leyendo archivo de log: {str(e)}"]
    
    # Aplicar filtros
    if filter_text:
        lines = [line for line in lines if filter_text.lower() in line.lower()]
    
    if level:
        level_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} ' + level)
        lines = [line for line in lines if level_pattern.search(line)]
    
    # Limitar el número de líneas, tomando las últimas
    if len(lines) > num_lines:
        lines = lines[-num_lines:]
    
    return lines

def get_error_summary(days=7):
    """
    Genera un resumen de errores de los últimos días.
    
    Args:
        days (int, optional): Número de días a analizar. Por defecto 7.
        
    Returns:
        dict: Resumen con estadísticas de errores.
    """
    error_log_path = LOGS_DIR / 'error.log'
    if not error_log_path.exists():
        return {"error": "El archivo de log de errores no existe"}
    
    # Fecha límite para el análisis
    limit_date = datetime.now() - timedelta(days=days)
    date_format = r'\d{4}-\d{2}-\d{2}'
    
    # Patrones para identificar errores
    error_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) ERROR')
    
    # Contadores
    error_count = Counter()
    error_by_day = defaultdict(int)
    
    try:
        with open(error_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                error_match = error_pattern.search(line)
                if error_match:
                    error_date_str = error_match.group(1)
                    try:
                        error_date = datetime.strptime(error_date_str.split()[0], '%Y-%m-%d')
                        if error_date >= limit_date:
                            error_day = error_date.strftime('%Y-%m-%d')
                            error_by_day[error_day] += 1
                            
                            # Extraer módulo y mensaje básico para agrupar
                            module_match = re.search(r'ERROR ([a-zA-Z0-9_\.]+)', line)
                            message_match = re.search(r'ERROR [a-zA-Z0-9_\.]+ (.+?)(?:\n|$)', line)
                            
                            if module_match and message_match:
                                module = module_match.group(1)
                                message = message_match.group(1)[:50]  # Truncar mensaje largo
                                error_count[f"{module}: {message}"] += 1
                    except ValueError:
                        pass  # Ignorar líneas con formato inválido
    except Exception as e:
        return {"error": f"Error al analizar el archivo de log: {str(e)}"}
    
    # Organizar los resultados
    summary = {
        "total_errors": sum(error_by_day.values()),
        "days_analyzed": days,
        "errors_by_day": dict(sorted(error_by_day.items())),
        "top_errors": dict(error_count.most_common(10)),
    }
    
    return summary

def get_performance_metrics(days=7):
    """
    Analiza métricas de rendimiento de los últimos días.
    
    Args:
        days (int, optional): Número de días a analizar. Por defecto 7.
        
    Returns:
        dict: Métricas de rendimiento de la aplicación.
    """
    api_log_path = LOGS_DIR / 'api.log'
    if not api_log_path.exists():
        return {"error": "El archivo de log de API no existe"}
    
    # Fecha límite para el análisis
    limit_date = datetime.now() - timedelta(days=days)
    
    # Patrones para identificar solicitudes y duraciones
    duration_pattern = re.compile(r'API Request duración: (\d+\.\d+)s - (\w+) (.+)')
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    
    # Estructuras para almacenar datos
    endpoints = defaultdict(list)
    slow_requests = []
    requests_by_day = defaultdict(int)
    
    try:
        with open(api_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Obtener fecha para filtrar por días
                date_match = date_pattern.search(line)
                if not date_match:
                    continue
                    
                log_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                if log_date < limit_date:
                    continue
                
                # Registrar solicitud por día
                day_key = log_date.strftime('%Y-%m-%d')
                requests_by_day[day_key] += 1
                
                # Analizar duración si es una línea de duración
                duration_match = duration_pattern.search(line)
                if duration_match:
                    duration = float(duration_match.group(1))
                    method = duration_match.group(2)
                    path = duration_match.group(3)
                    
                    # Registrar para estadísticas por endpoint
                    endpoint = f"{method} {path}"
                    endpoints[endpoint].append(duration)
                    
                    # Registrar solicitudes lentas
                    if duration > 1.0:  # Solicitudes que tardan más de 1 segundo
                        slow_requests.append({
                            "endpoint": endpoint,
                            "duration": duration,
                            "date": day_key
                        })
    except Exception as e:
        return {"error": f"Error al analizar el archivo de log: {str(e)}"}
    
    # Calcular estadísticas por endpoint
    endpoint_stats = {}
    for endpoint, durations in endpoints.items():
        if len(durations) > 0:
            endpoint_stats[endpoint] = {
                "count": len(durations),
                "avg_duration": sum(durations) / len(durations),
                "max_duration": max(durations),
                "min_duration": min(durations)
            }
    
    # Ordenar slow_requests por duración
    slow_requests.sort(key=lambda x: x["duration"], reverse=True)
    
    # Organizar resultados
    metrics = {
        "total_requests": sum(requests_by_day.values()),
        "requests_by_day": dict(sorted(requests_by_day.items())),
        "endpoint_stats": dict(sorted(endpoint_stats.items(), 
                                     key=lambda x: x[1]["avg_duration"], 
                                     reverse=True)[:10]),
        "slow_requests": slow_requests[:20],  # Top 20 solicitudes más lentas
    }
    
    return metrics