from django.db import models
from django.conf import settings
from registrations.models import Registration
from events.models import PenaltyType

class Result(models.Model):
    """
    Modelo que representa los resultados de un participante en una carrera.
    """
    registration = models.OneToOneField(
        Registration, 
        on_delete=models.CASCADE, 
        related_name='result',
        verbose_name="Inscripción"
    )
    
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('pending', 'Pendiente de revisión'),
        ('verified', 'Verificado'),
        ('disqualified', 'Descalificado'),
        ('dnf', 'No Finalizó'),
        ('dns', 'No Inició'),
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="Estado"
    )
    
    # Tiempo oficial en segundos (más fácil para cálculos)
    official_time_seconds = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Tiempo oficial (segundos)"
    )
    
    # Posición en la clasificación
    position = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Posición"
    )
    
    # Campos de auditoría
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='recorded_results',
        verbose_name="Registrado por"
    )
    
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_results',
        verbose_name="Verificado por"
    )
    
    verified_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Fecha de verificación"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Notas"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    def __str__(self):
        return f"{self.registration.participant} - {self.registration.dog} - {self.format_time()}"
    
    def format_time(self):
        """Formatea el tiempo en segundos a formato HH:MM:SS."""
        if self.official_time_seconds is None:
            return "Sin tiempo"
        
        hours = self.official_time_seconds // 3600
        minutes = (self.official_time_seconds % 3600) // 60
        seconds = self.official_time_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    class Meta:
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"
        ordering = ['registration__race', 'position', 'official_time_seconds']

class TimeRecord(models.Model):
    """
    Modelo para registrar tiempos de paso en diferentes puntos de control.
    """
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name='time_records',
        verbose_name="Resultado"
    )
    
    checkpoint_number = models.PositiveIntegerField(
        verbose_name="Número de punto de control"
    )
    
    time_seconds = models.PositiveIntegerField(
        verbose_name="Tiempo (segundos)"
    )
    
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )
    
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    def __str__(self):
        return f"CP{self.checkpoint_number} - {self.format_time()}"
    
    def format_time(self):
        """Formatea el tiempo en segundos a formato HH:MM:SS."""
        hours = self.time_seconds // 3600
        minutes = (self.time_seconds % 3600) // 60
        seconds = self.time_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    class Meta:
        verbose_name = "Registro de Tiempo"
        verbose_name_plural = "Registros de Tiempo"
        ordering = ['result', 'checkpoint_number']
        unique_together = ['result', 'checkpoint_number']

class Penalty(models.Model):
    """
    Modelo para registrar penalizaciones aplicadas a un resultado.
    """
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name='penalties',
        verbose_name="Resultado"
    )
    
    penalty_type = models.ForeignKey(
        PenaltyType,
        on_delete=models.CASCADE,
        verbose_name="Tipo de penalización"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )
    
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    def __str__(self):
        return f"{self.penalty_type.name} - {self.result.registration.participant}"
    
    class Meta:
        verbose_name = "Penalización"
        verbose_name_plural = "Penalizaciones"
        ordering = ['result', 'recorded_at']