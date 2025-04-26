#!/usr/bin/env python
"""
Script para analizar logs de la aplicación Canicross desde la línea de comandos.
Proporciona funciones para buscar y analizar patrones en los logs.

Uso:
    python log_analyzer.py <comando> [opciones]

Comandos:
    search      Buscar patrones en logs
    errors      Mostrar resumen de errores
    metrics     Mostrar métricas de rendimiento
    monitor     Monitorizar logs en tiempo real (similar a tail -f)
"""
import os
import sys
import re
import time
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import gzip
from collections import Counter, defaultdict

# Ruta base del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

# Directorio de logs
LOGS_DIR = os.path.join(base_dir, 'logs')

# Colores para la salida en terminal
COLORS = {
    'RESET': '\033[0m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
}

def colorize_log_line(line):
    """Agrega color a una línea de log según su nivel."""
    if ' ERROR ' in line:
        return f"{COLORS['RED']}{line}{COLORS['RESET']}"
    elif ' WARNING ' in line:
        return f"{COLORS['YELLOW']}{line}{COLORS['RESET']}"
    elif ' INFO ' in line:
        return f"{COLORS['GREEN']}{line}{COLORS['RESET']}"
    elif ' DEBUG ' in line:
        return f"{COLORS['BLUE']}{line}{COLORS['RESET']}"
    else:
        return line

def get_log_files():
    """Obtiene lista de archivos de log disponibles."""
    if not os.path.exists(LOGS_DIR):
        print(f"Error: Directorio de logs no encontrado: {LOGS_DIR}")
        return []
    
    log_files = []
    for file in Path(LOGS_DIR).glob('*.log*'):
        log_files.append(file.name)
    
    return sorted(log_files)

def read_log_file(filename, num_lines=0, filter_text=None, level=None):
    """Lee un archivo de log y aplica filtros."""
    filepath = os.path.join(LOGS_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"Error: Archivo no encontrado: {filepath}")
        return []
    
    # Determinar si es un archivo comprimido
    is_gzip = filepath.endswith('.gz')
    
    # Leer el archivo
    try:
        if is_gzip:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
    except Exception as e:
        print(f"Error leyendo archivo: {str(e)}")
        return []
    
    # Aplicar filtros
    if filter_text:
        lines = [line for line in lines if filter_text.lower() in line.lower()]
    
    if level:
        level_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} ' + level)
        lines = [line for line in lines if level_pattern.search(line)]
    
    # Limitar el número de líneas si se especifica
    if num_lines > 0 and len(lines) > num_lines:
        lines = lines[-num_lines:]
    
    return lines

def search_logs(args):
    """Busca patrones en los archivos de log."""
    if not args.file:
        # Si no se especifica un archivo, buscar en todos
        log_files = get_log_files()
    else:
        log_files = [args.file]
    
    if not log_files:
        print("No se encontraron archivos de log.")
        return
    
    pattern = args.pattern
    if not pattern:
        print("Error: Debe especificar un patrón de búsqueda.")
        return
    
    print(f"Buscando '{pattern}' en {len(log_files)} archivo(s)...")
    
    total_matches = 0
    for log_file in log_files:
        lines = read_log_file(log_file, 0, pattern, args.level)
        if lines:
            print(f"\n{COLORS['PURPLE']}=== {log_file} ({len(lines)} resultados) ==={COLORS['RESET']}")
            total_matches += len(lines)
            for line in lines:
                print(colorize_log_line(line.rstrip()))
    
    print(f"\nTotal: {total_matches} resultados encontrados.")

def show_error_summary(args):
    """Muestra un resumen de errores en los logs."""
    days = args.days
    error_log = 'error.log'
    
    if not os.path.exists(os.path.join(LOGS_DIR, error_log)):
        print(f"Error: Archivo de log de errores no encontrado.")
        return
    
    print(f"Analizando errores de los últimos {days} días...")
    
    # Fecha límite para el análisis
    limit_date = datetime.now() - timedelta(days=days)
    
    # Patrones para identificar errores
    error_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) ERROR')
    
    # Contadores
    error_count = Counter()
    error_by_day = defaultdict(int)
    
    try:
        with open(os.path.join(LOGS_DIR, error_log), 'r', encoding='utf-8') as f:
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
        print(f"Error al analizar el archivo de log: {str(e)}")
        return
    
    # Mostrar resultados
    total_errors = sum(error_by_day.values())
    print(f"\n{COLORS['PURPLE']}=== Resumen de Errores ==={COLORS['RESET']}")
    print(f"Total de errores: {total_errors}")
    
    if total_errors > 0:
        print("\nErrores por día:")
        for day, count in sorted(error_by_day.items()):
            print(f"  {day}: {count}")
        
        print("\nTop 10 errores:")
        for error, count in error_count.most_common(10):
            print(f"  {count} veces: {error}")
    else:
        print("No se encontraron errores en el período especificado.")

def show_performance_metrics(args):
    """Muestra métricas de rendimiento basadas en los logs."""
    days = args.days
    api_log = 'api.log'
    
    if not os.path.exists(os.path.join(LOGS_DIR, api_log)):
        print(f"Error: Archivo de log de API no encontrado.")
        return
    
    print(f"Analizando métricas de los últimos {days} días...")
    
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
        with open(os.path.join(LOGS_DIR, api_log), 'r', encoding='utf-8') as f:
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
        print(f"Error al analizar el archivo de log: {str(e)}")
        return
    
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
    
    # Mostrar resultados
    total_requests = sum(requests_by_day.values())
    print(f"\n{COLORS['PURPLE']}=== Métricas de Rendimiento ==={COLORS['RESET']}")
    print(f"Total de solicitudes: {total_requests}")
    
    if total_requests > 0:
        print("\nSolicitudes por día:")
        for day, count in sorted(requests_by_day.items()):
            print(f"  {day}: {count}")
        
        print("\nTop 10 endpoints más lentos (promedio):")
        sorted_endpoints = sorted(endpoint_stats.items(), key=lambda x: x[1]["avg_duration"], reverse=True)[:10]
        for endpoint, stats in sorted_endpoints:
            print(f"  {endpoint}")
            print(f"    Solicitudes: {stats['count']}")
            print(f"    Tiempo promedio: {stats['avg_duration']:.3f}s")
            print(f"    Tiempo máximo: {stats['max_duration']:.3f}s")
        
        print("\nTop 10 solicitudes más lentas:")
        for req in slow_requests[:10]:
            print(f"  {req['endpoint']} - {req['duration']:.3f}s ({req['date']})")
    else:
        print("No se encontraron solicitudes en el período especificado.")

def monitor_logs(args):
    """Monitoriza logs en tiempo real, similar a tail -f."""
    log_file = args.file
    if not log_file:
        print("Error: Debe especificar un archivo de log a monitorizar.")
        return
    
    filepath = os.path.join(LOGS_DIR, log_file)
    if not os.path.exists(filepath):
        print(f"Error: Archivo no encontrado: {filepath}")
        return
    
    print(f"Monitorizando {log_file}... (Presiona Ctrl+C para detener)")
    
    # Opciones de filtrado
    level = args.level
    filter_text = args.pattern
    
    # Posición inicial del archivo
    current_size = os.path.getsize(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Primero mostramos las últimas líneas
            f.seek(max(0, current_size - 2000))  # Mostrar aproximadamente las últimas líneas
            
            # Descartar línea parcial si seek nos deja en medio de una línea
            if current_size > 2000:
                f.readline()
            
            # Mostrar últimas líneas aplicando filtros
            last_lines = f.readlines()
            for line in last_lines:
                if (not filter_text or filter_text.lower() in line.lower()) and \
                   (not level or f" {level} " in line):
                    print(colorize_log_line(line.rstrip()))
            
            # Monitorizar nuevas líneas
            while True:
                line = f.readline()
                if line:
                    if (not filter_text or filter_text.lower() in line.lower()) and \
                       (not level or f" {level} " in line):
                        print(colorize_log_line(line.rstrip()))
                else:
                    time.sleep(0.1)  # Esperar un poco antes de verificar nuevas líneas
                    
                    # Comprobar si el archivo se ha rotado
                    if not os.path.exists(filepath):
                        print(f"Archivo {log_file} ya no existe. Terminando monitorización.")
                        break
    except KeyboardInterrupt:
        print("\nMonitorización detenida.")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Función principal del script."""
    # Crear parser principal
    parser = argparse.ArgumentParser(description='Analizador de logs de Canicross')
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando 'search'
    search_parser = subparsers.add_parser('search', help='Buscar patrones en logs')
    search_parser.add_argument('-f', '--file', help='Archivo de log específico')
    search_parser.add_argument('-p', '--pattern', help='Patrón de texto a buscar')
    search_parser.add_argument('-l', '--level', choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'], 
                            help='Nivel de log a filtrar')
    
    # Comando 'errors'
    errors_parser = subparsers.add_parser('errors', help='Mostrar resumen de errores')
    errors_parser.add_argument('-d', '--days', type=int, default=7, 
                             help='Número de días a analizar (default: 7)')
    
    # Comando 'metrics'
    metrics_parser = subparsers.add_parser('metrics', help='Mostrar métricas de rendimiento')
    metrics_parser.add_argument('-d', '--days', type=int, default=7, 
                              help='Número de días a analizar (default: 7)')
    
    # Comando 'monitor'
    monitor_parser = subparsers.add_parser('monitor', help='Monitorizar logs en tiempo real')
    monitor_parser.add_argument('-f', '--file', required=True, help='Archivo de log a monitorizar')
    monitor_parser.add_argument('-p', '--pattern', help='Patrón de texto a filtrar')
    monitor_parser.add_argument('-l', '--level', choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'], 
                              help='Nivel de log a filtrar')
    
    # Comando 'list' para listar archivos disponibles
    list_parser = subparsers.add_parser('list', help='Listar archivos de log disponibles')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar comando apropiado
    if args.command == 'search':
        search_logs(args)
    elif args.command == 'errors':
        show_error_summary(args)
    elif args.command == 'metrics':
        show_performance_metrics(args)
    elif args.command == 'monitor':
        monitor_logs(args)
    elif args.command == 'list':
        files = get_log_files()
        if files:
            print("Archivos de log disponibles:")
            for file in files:
                print(f"  {file}")
        else:
            print("No se encontraron archivos de log.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()