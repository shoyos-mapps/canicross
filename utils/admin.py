"""
Implementación de administración para el visor de logs.
"""
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import csv
import json
from datetime import datetime

from .log_viewer import (
    get_log_files, 
    read_log_file, 
    get_error_summary, 
    get_performance_metrics
)

class LogViewerAdmin(admin.ModelAdmin):
    """
    Administrador para visualizar logs de la aplicación.
    """
    # El modelo no es importante aquí, es un admin personalizado
    model = None
    
    def get_urls(self):
        """Define URLs personalizadas para el visor de logs."""
        urls = super().get_urls()
        custom_urls = [
            path('logs/', self.admin_site.admin_view(self.log_viewer_view), name='log-viewer'),
            path('logs/files/', self.admin_site.admin_view(self.log_files_view), name='log-files'),
            path('logs/content/', self.admin_site.admin_view(self.log_content_view), name='log-content'),
            path('logs/summary/', self.admin_site.admin_view(self.log_summary_view), name='log-summary'),
            path('logs/metrics/', self.admin_site.admin_view(self.log_metrics_view), name='log-metrics'),
            path('logs/export/', self.admin_site.admin_view(self.log_export_view), name='log-export'),
        ]
        return custom_urls + urls
    
    def log_viewer_view(self, request):
        """
        Vista principal del visor de logs.
        """
        log_files = get_log_files()
        
        context = {
            'title': 'Visor de Logs',
            'log_files': log_files,
            'opts': self.model._meta,
            'is_production': not settings.DEBUG,
            'client_ip': self.get_client_ip(request),
        }
        
        return TemplateResponse(request, 'admin/log_viewer.html', context)
    
    def log_files_view(self, request):
        """
        Devuelve una lista de archivos de log disponibles.
        """
        return JsonResponse({'files': get_log_files()})
    
    def log_content_view(self, request):
        """
        Muestra el contenido de un archivo de log.
        """
        filename = request.GET.get('file', '')
        num_lines = int(request.GET.get('lines', 1000))
        filter_text = request.GET.get('filter', None)
        level = request.GET.get('level', None)
        
        if not filename:
            return JsonResponse({'error': 'Nombre de archivo no especificado'}, status=400)
        
        lines = read_log_file(filename, num_lines, filter_text, level)
        return JsonResponse({'lines': lines, 'total': len(lines)})
    
    def log_summary_view(self, request):
        """
        Genera un resumen de errores.
        """
        days = int(request.GET.get('days', 7))
        summary = get_error_summary(days)
        return JsonResponse(summary)
    
    def log_metrics_view(self, request):
        """
        Genera métricas de rendimiento.
        """
        days = int(request.GET.get('days', 7))
        metrics = get_performance_metrics(days)
        return JsonResponse(metrics)
    
    def log_export_view(self, request):
        """
        Exporta el contenido de un log a CSV o JSON.
        """
        filename = request.GET.get('file', '')
        format_type = request.GET.get('format', 'csv')
        filter_text = request.GET.get('filter', None)
        level = request.GET.get('level', None)
        
        if not filename:
            return HttpResponse('Nombre de archivo no especificado', status=400)
        
        lines = read_log_file(filename, 100000, filter_text, level)
        
        if format_type == 'json':
            response = HttpResponse(json.dumps({'log': lines}, indent=2), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.json"'
        else:  # csv por defecto
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Línea', 'Contenido'])
            for i, line in enumerate(lines, 1):
                writer.writerow([i, line.strip()])
        
        return response
    
    def get_client_ip(self, request):
        """
        Obtiene la dirección IP del cliente.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip