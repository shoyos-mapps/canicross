from django.db import models
from django.utils.text import slugify
from utils.logger import get_logger, log_db_operation, log_exception

logger = get_logger('events')

class Event(models.Model):
    """
    Model representing a Canicross event.
    """
    name = models.CharField(max_length=255, verbose_name="Nombre")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    location = models.CharField(max_length=255, verbose_name="Ubicación")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(verbose_name="Fecha de fin")
    rules = models.TextField(blank=True, verbose_name="Reglamento")
    registration_start = models.DateTimeField(verbose_name="Inicio de inscripciones")
    registration_end = models.DateTimeField(verbose_name="Fin de inscripciones")
    required_documents = models.JSONField(default=list, blank=True, verbose_name="Documentos requeridos")
    required_vaccines = models.JSONField(default=list, blank=True, verbose_name="Vacunas requeridas")
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('registration_open', 'Inscripciones abiertas'),
        ('registration_closed', 'Inscripciones cerradas'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    @log_db_operation(logger)
    def save(self, *args, **kwargs):
        try:
            is_new = self.pk is None
            if not self.slug:
                self.slug = slugify(self.name)
            
            super().save(*args, **kwargs)
            
            if is_new:
                logger.info(f"Evento creado: {self.name} (ID: {self.pk})")
            else:
                logger.info(f"Evento actualizado: {self.name} (ID: {self.pk})")
        except Exception as e:
            log_exception(logger, f"Error al guardar evento: {self.name if hasattr(self, 'name') else 'nuevo'}")
            raise

    def __str__(self):
        return self.name

class Modality(models.Model):
    """
    Modelo que representa una modalidad de competición (p.ej., Canicross, Bikejoring, etc.)
    """
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Modalidad"
        verbose_name_plural = "Modalidades"

class Race(models.Model):
    """
    Modelo que representa una carrera dentro de un evento para una modalidad específica.
    """
    event = models.ForeignKey(Event, related_name='races', on_delete=models.CASCADE, verbose_name="Evento")
    modality = models.ForeignKey(Modality, related_name='races', on_delete=models.CASCADE, verbose_name="Modalidad")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    distance = models.DecimalField(max_digits=5, decimal_places=2, help_text="Distancia en kilómetros", verbose_name="Distancia")
    description = models.TextField(blank=True, verbose_name="Descripción")
    START_TYPE_CHOICES = (
        ('mass', 'Salida en masa'),
        ('waves', 'Salida por oleadas'),
        ('intervals', 'Salida por intervalos'),
    )
    start_type = models.CharField(max_length=10, choices=START_TYPE_CHOICES, default='mass', verbose_name="Tipo de salida")
    participants_per_interval = models.PositiveSmallIntegerField(default=1, verbose_name="Participantes por intervalo")
    interval_seconds = models.PositiveSmallIntegerField(default=30, verbose_name="Segundos entre intervalos")
    max_participants = models.PositiveIntegerField(default=100, verbose_name="Máximo de participantes")
    race_date = models.DateField(verbose_name="Fecha de carrera")
    race_time = models.TimeField(verbose_name="Hora de carrera")
    actual_start_time = models.DateTimeField(null=True, blank=True, verbose_name="Hora real de inicio")
    
    @log_db_operation(logger)
    def save(self, *args, **kwargs):
        try:
            is_new = self.pk is None
            super().save(*args, **kwargs)
            
            if is_new:
                logger.info(f"Carrera creada: {self.name} en evento {self.event.name} (ID: {self.pk})")
            else:
                logger.info(f"Carrera actualizada: {self.name} (ID: {self.pk})")
        except Exception as e:
            log_exception(logger, f"Error al guardar carrera: {self.name if hasattr(self, 'name') else 'nueva'}")
            raise
    
    def __str__(self):
        return f"{self.name} - {self.event.name} ({self.modality.name})"
        
    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
    
class Category(models.Model):
    """
    Modelo que representa una categoría de edad/género para carreras.
    """
    name = models.CharField(max_length=100, verbose_name="Nombre")
    gender = models.CharField(max_length=1, choices=(('M', 'Masculino'), ('F', 'Femenino')), verbose_name="Género")
    min_age = models.PositiveSmallIntegerField(verbose_name="Edad mínima")
    max_age = models.PositiveSmallIntegerField(verbose_name="Edad máxima")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    def __str__(self):
        return f"{self.name} ({self.min_age}-{self.max_age} {self.get_gender_display()})"
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class RaceCategory(models.Model):
    """
    Modelo que vincula carreras con categorías y define precio y cuota.
    """
    race = models.ForeignKey(Race, related_name='race_categories', on_delete=models.CASCADE, verbose_name="Carrera")
    category = models.ForeignKey(Category, related_name='race_categories', on_delete=models.CASCADE, verbose_name="Categoría")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio")
    quota = models.PositiveIntegerField(default=0, help_text="0 significa ilimitado", verbose_name="Cupo")
    
    def __str__(self):
        return f"{self.race.name} - {self.category.name}"
    
    class Meta:
        verbose_name = "Categoría de Carrera"
        verbose_name_plural = "Categorías de Carrera"
        unique_together = ('race', 'category')

class PenaltyType(models.Model):
    """
    Modelo que define tipos de penalizaciones que pueden asignarse durante una carrera.
    """
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    time_penalty = models.DurationField(null=True, blank=True, verbose_name="Penalización de tiempo")
    is_disqualification = models.BooleanField(default=False, verbose_name="Es descalificación")
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Tipo de Penalización"
        verbose_name_plural = "Tipos de Penalización"
