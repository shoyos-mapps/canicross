from django.db import models
from django.conf import settings
from participants.models import Dog
from registrations.models import Registration

class VeterinaryCheck(models.Model):
    """
    Modelo para registrar revisiones veterinarias realizadas a perros.
    """
    registration = models.OneToOneField(
        Registration, 
        on_delete=models.CASCADE,
        related_name='veterinary_check',
        verbose_name="Inscripción"
    )
    dog = models.ForeignKey(
        Dog, 
        on_delete=models.CASCADE,
        related_name='veterinary_checks',
        verbose_name="Perro"
    )
    veterinarian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_checks',
        verbose_name="Veterinario"
    )
    
    # Resultados de revisión
    CHECK_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('in_progress', 'En revisión'),
        ('approved', 'Aprobado'),
        ('conditional', 'Aprobado con condiciones'),
        ('rejected', 'Rechazado'),
    )
    status = models.CharField(
        max_length=20, 
        choices=CHECK_STATUS_CHOICES, 
        default='pending',
        verbose_name="Estado"
    )
    
    temperature = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        null=True, 
        blank=True,
        verbose_name="Temperatura (°C)"
    )
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Peso (kg)"
    )
    heart_rate = models.PositiveSmallIntegerField(
        null=True, 
        blank=True,
        verbose_name="Ritmo cardíaco (lpm)"
    )
    
    # Evaluaciones específicas
    CONDITION_CHOICES = (
        (1, 'Deficiente'),
        (2, 'Regular'),
        (3, 'Bueno'),
        (4, 'Muy bueno'),
        (5, 'Excelente'),
    )
    
    physical_condition = models.PositiveSmallIntegerField(
        choices=CONDITION_CHOICES,
        null=True, 
        blank=True,
        verbose_name="Condición física"
    )
    
    hydration_status = models.PositiveSmallIntegerField(
        choices=CONDITION_CHOICES,
        null=True, 
        blank=True,
        verbose_name="Estado de hidratación"
    )
    
    # Verificaciones específicas
    has_injuries = models.BooleanField(
        default=False,
        verbose_name="Presenta heridas o lesiones"
    )
    injury_details = models.TextField(
        blank=True,
        verbose_name="Detalle de lesiones"
    )
    
    has_respiratory_issues = models.BooleanField(
        default=False,
        verbose_name="Problemas respiratorios"
    )
    respiratory_details = models.TextField(
        blank=True,
        verbose_name="Detalles respiratorios"
    )
    
    has_musculoskeletal_issues = models.BooleanField(
        default=False,
        verbose_name="Problemas musculoesqueléticos"
    )
    musculoskeletal_details = models.TextField(
        blank=True,
        verbose_name="Detalles musculoesqueléticos"
    )
    
    # Verificación de vacunas
    vaccines_verified = models.BooleanField(
        default=False,
        verbose_name="Vacunas verificadas"
    )
    vaccines_notes = models.TextField(
        blank=True,
        verbose_name="Notas sobre vacunas"
    )
    
    # Comentarios generales y decisión
    general_notes = models.TextField(
        blank=True,
        verbose_name="Notas generales"
    )
    recommendations = models.TextField(
        blank=True,
        verbose_name="Recomendaciones"
    )
    
    # Timestamps
    check_time = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Fecha/hora de revisión"
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
        return f"Revisión de {self.dog.name} - {self.status}"
    
    class Meta:
        verbose_name = "Revisión Veterinaria"
        verbose_name_plural = "Revisiones Veterinarias"
        ordering = ['-updated_at']

class VaccinationRecord(models.Model):
    """
    Modelo para registrar las vacunas verificadas de un perro.
    """
    veterinary_check = models.ForeignKey(
        VeterinaryCheck,
        on_delete=models.CASCADE,
        related_name='vaccination_records',
        verbose_name="Revisión veterinaria"
    )
    
    vaccine_name = models.CharField(
        max_length=100,
        verbose_name="Nombre de la vacuna"
    )
    
    administration_date = models.DateField(
        verbose_name="Fecha de administración"
    )
    
    expiry_date = models.DateField(
        verbose_name="Fecha de expiración",
        null=True,
        blank=True
    )
    
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de lote"
    )
    
    verified = models.BooleanField(
        default=True,
        verbose_name="Verificada"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Notas"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    def __str__(self):
        return f"{self.vaccine_name} - {self.administration_date}"
    
    class Meta:
        verbose_name = "Registro de Vacunación"
        verbose_name_plural = "Registros de Vacunación"
        ordering = ['-administration_date']

class MedicalAlert(models.Model):
    """
    Modelo para alertas médicas que requieren seguimiento durante el evento.
    """
    veterinary_check = models.ForeignKey(
        VeterinaryCheck,
        on_delete=models.CASCADE,
        related_name='medical_alerts',
        verbose_name="Revisión veterinaria"
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Prioridad"
    )
    
    description = models.TextField(
        verbose_name="Descripción"
    )
    
    requires_followup = models.BooleanField(
        default=False,
        verbose_name="Requiere seguimiento"
    )
    
    notify_staff = models.BooleanField(
        default=False,
        verbose_name="Notificar al staff"
    )
    
    STATUS_CHOICES = (
        ('active', 'Activa'),
        ('monitoring', 'En monitoreo'),
        ('resolved', 'Resuelta'),
        ('dismissed', 'Descartada'),
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Estado"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_alerts',
        verbose_name="Creada por"
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
        return f"Alerta {self.get_priority_display()} - {self.veterinary_check.dog.name}"
    
    class Meta:
        verbose_name = "Alerta Médica"
        verbose_name_plural = "Alertas Médicas"
        ordering = ['-priority', '-created_at']
