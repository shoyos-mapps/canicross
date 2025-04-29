from django.db import models
from django.conf import settings
from django.db.models import Max
from datetime import date

class Participant(models.Model):
    """
    Modelo que representa un participante humano (corredor).
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")
    id_document = models.CharField(max_length=20, help_text="DNI, pasaporte u otro documento de identidad", verbose_name="Documento de identidad", blank=True)
    participant_number = models.PositiveIntegerField(unique=True, verbose_name="Número de participante", editable=False, null=True, blank=True)
    date_of_birth = models.DateField(verbose_name="Fecha de nacimiento", null=True, blank=True)
    GENDER_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Género", blank=True)
    email = models.EmailField(verbose_name="Correo electrónico", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Teléfono", blank=True)
    address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    state_province = models.CharField(max_length=100, blank=True, verbose_name="Provincia/Estado")
    country = models.CharField(max_length=100, blank=True, verbose_name="País")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="Código postal")
    club = models.CharField(max_length=100, blank=True, verbose_name="Club")
    emergency_contact_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre de contacto de emergencia")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono de contacto de emergencia")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    def save(self, *args, **kwargs):
        # Generar número de participante automáticamente si no tiene uno
        if not self.participant_number:
            # Obtener el máximo número de participante existente
            max_number = Participant.objects.aggregate(Max('participant_number'))['participant_number__max']
            # Si no hay participantes, iniciar en 1000, de lo contrario incrementar en 1
            if max_number is None:
                self.participant_number = 1000
            else:
                self.participant_number = max_number + 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        participant_num = f"#{self.participant_number}" if self.participant_number else ""
        return f"{self.first_name} {self.last_name} {participant_num}"
        
    @property
    def full_name(self):
        """Retorna el nombre completo del participante."""
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        
    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        
    get_age.short_description = "Edad"

class Dog(models.Model):
    """
    Modelo que representa un perro participante.
    """
    owner = models.ForeignKey(Participant, related_name='dogs', on_delete=models.CASCADE, verbose_name="Propietario")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    breed = models.CharField(max_length=100, verbose_name="Raza")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    gender = models.CharField(max_length=1, choices=(('M', 'Macho'), ('F', 'Hembra')), verbose_name="Género")
    microchip_number = models.CharField(max_length=100, blank=True, verbose_name="Número de microchip")
    veterinary_book_number = models.CharField(max_length=100, blank=True, verbose_name="Número de cartilla veterinaria")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    def __str__(self):
        return f"{self.name} ({self.breed}) - {self.owner}"
    
    def get_age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        
    class Meta:
        verbose_name = "Perro"
        verbose_name_plural = "Perros"
        
    get_age.short_description = "Edad"