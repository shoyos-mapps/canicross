from django.db import models
from django.conf import settings
from events.models import Event, Race, RaceCategory
from participants.models import Participant, Dog

class Registration(models.Model):
    """
    Modelo que representa una inscripción de un par participante-perro (binomio) para una carrera.
    """
    participant = models.ForeignKey(Participant, related_name='registrations', on_delete=models.CASCADE, verbose_name="Participante")
    dog = models.ForeignKey(Dog, related_name='registrations', on_delete=models.CASCADE, verbose_name="Perro")
    race = models.ForeignKey(Race, related_name='registrations', on_delete=models.CASCADE, verbose_name="Carrera")
    race_category = models.ForeignKey(RaceCategory, related_name='registrations', on_delete=models.CASCADE, verbose_name="Categoría")
    bib_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de dorsal")
    
    # Estado de inscripción
    REGISTRATION_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
    )
    registration_status = models.CharField(max_length=20, choices=REGISTRATION_STATUS_CHOICES, default='pending', verbose_name="Estado de inscripción")
    
    # Estado de pago
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('refunded', 'Reembolsado'),
        ('failed', 'Fallido'),
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Estado de pago")
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Método de pago")
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name="Referencia de pago")
    
    # Estado de vacunas y verificación veterinaria
    AI_VACCINE_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('ok', 'Correcto'),
        ('issue', 'Con incidencia'),
        ('error', 'Error/Requiere revisión'),
    )
    ai_vaccine_status = models.CharField(max_length=20, choices=AI_VACCINE_STATUS_CHOICES, default='pending', verbose_name="Estado de vacunas (IA)")
    
    VET_CHECK_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    )
    vet_check_status = models.CharField(max_length=20, choices=VET_CHECK_STATUS_CHOICES, default='pending', verbose_name="Estado de revisión veterinaria")
    vet_check_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha/hora de revisión veterinaria")
    vet_checker_details = models.TextField(blank=True, verbose_name="Detalles de revisión veterinaria")
    
    # Estado de entrega de kit y check-in
    kit_delivered = models.BooleanField(default=False, verbose_name="Kit entregado")
    kit_delivery_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha/hora de entrega de kit")
    
    checked_in = models.BooleanField(default=False, verbose_name="Check-in realizado")
    checkin_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha/hora de check-in")
    
    # Miscelánea
    notes = models.TextField(blank=True, verbose_name="Notas")
    waiver_accepted = models.BooleanField(default=False, verbose_name="Descargo de responsabilidad aceptado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    def __str__(self):
        return f"{self.participant} - {self.race} - {self.bib_number}"
    
    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = ('race', 'bib_number')
        ordering = ['race', 'bib_number']
    
class Document(models.Model):
    """
    Modelo para documentos subidos.
    """
    registration = models.ForeignKey(Registration, related_name='documents', on_delete=models.CASCADE, verbose_name="Inscripción")
    
    DOCUMENT_TYPE_CHOICES = (
        ('identity', 'Documento de Identidad'),
        ('veterinary_certificate', 'Certificado Veterinario'),
        ('vaccination_record', 'Registro de Vacunación'),
        ('insurance', 'Certificado de Seguro'),
        ('other', 'Otro'),
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, verbose_name="Tipo de documento")
    file = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Archivo")
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    
    # Campos de análisis OCR e IA
    ocr_raw_text = models.TextField(blank=True, verbose_name="Texto extraído por OCR")
    ocr_status = models.CharField(max_length=20, default='pending', verbose_name="Estado OCR")
    ocr_analysis_result = models.JSONField(default=dict, blank=True, verbose_name="Resultado análisis IA")
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de subida")
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.registration.participant}"
        
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

class ParticipantAnnotation(models.Model):
    """
    Modelo para anotaciones/penalizaciones de jueces.
    """
    registration = models.ForeignKey(Registration, related_name='annotations', on_delete=models.CASCADE, verbose_name="Inscripción")
    penalty_type = models.ForeignKey('events.PenaltyType', related_name='annotations', on_delete=models.CASCADE, verbose_name="Tipo de penalización")
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recorded_annotations', on_delete=models.CASCADE, verbose_name="Registrado por")
    
    STATUS_CHOICES = (
        ('recorded', 'Registrada'),
        ('confirmed', 'Confirmada'),
        ('dismissed', 'Desestimada'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recorded', verbose_name="Estado")
    
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='confirmed_annotations', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name="Confirmado por"
    )
    
    notes = models.TextField(blank=True, verbose_name="Notas")
    location = models.CharField(max_length=100, blank=True, help_text="Ubicación en el recorrido donde ocurrió la infracción", verbose_name="Ubicación")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    def __str__(self):
        return f"{self.registration.participant} - {self.penalty_type} - {self.status}"
        
    class Meta:
        verbose_name = "Anotación de Participante"
        verbose_name_plural = "Anotaciones de Participantes"
