from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Max
from django.core.exceptions import NoReverseMatch

from .models import Participant, Dog
from veterinary.models import VeterinaryCheck

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('participant_number', 'first_name', 'last_name', 'email', 'phone', 'city', 'dogs_count', 'registrations_count', 'payment_status')
    list_filter = ('city', 'country', 'user__is_active')
    search_fields = ('first_name', 'last_name', 'id_document', 'email', 'phone', 'participant_number')
    readonly_fields = ('created_at', 'updated_at', 'user', 'payment_status', 'participant_number')
    
    fieldsets = (
        ('Información personal', {
            'fields': ('user', 'participant_number', 'first_name', 'last_name', 'id_document', 'date_of_birth', 'gender')
        }),
        ('Contacto', {
            'fields': ('email', 'phone', 'address', 'city', 'state_province', 'postal_code', 'country')
        }),
        ('Emergencia', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'),
            'classes': ('collapse',),
        }),
        ('Otra información', {
            'fields': ('created_at', 'updated_at', 'additional_info'),
            'classes': ('collapse',),
        }),
    )
    
    def dogs_count(self, obj):
        """Muestra el número de perros del participante con enlace."""
        count = obj.dogs.count()
        if count:
            try:
                url = reverse('admin:participants_dog_changelist') + f'?owner__id__exact={obj.id}'
                return format_html('<a href="{}">{} {}</a>', 
                                  url, count, 'perro' if count == 1 else 'perros')
            except NoReverseMatch:
                return f"{count} {'perro' if count == 1 else 'perros'}"
        return '0 perros'
    
    dogs_count.short_description = 'Perros'
    
    def registrations_count(self, obj):
        """Muestra el número de inscripciones del participante con enlace."""
        count = obj.registrations.count()
        if count:
            try:
                url = reverse('admin:canicross_admin_registrations_registration_changelist') + f'?participant__id__exact={obj.id}'
                return format_html('<a href="{}">{} {}</a>', 
                                 url, count, 'inscripción' if count == 1 else 'inscripciones')
            except NoReverseMatch:
                # Intentar con formato alternativo (namespace:model_changelist)
                try:
                    url = reverse('admin:registrations_registration_changelist') + f'?participant__id__exact={obj.id}'
                    return format_html('<a href="{}">{} {}</a>', 
                                     url, count, 'inscripción' if count == 1 else 'inscripciones')
                except NoReverseMatch:
                    # Si no se puede resolver la URL, mostrar solo el número sin enlace
                    return f"{count} {'inscripción' if count == 1 else 'inscripciones'}"
        return '0 inscripciones'
    
    registrations_count.short_description = 'Inscripciones'
    
    def payment_status(self, obj):
        """Muestra un resumen del estado de pago de las inscripciones del participante."""
        # Contar inscripciones por estado de pago
        registrations = obj.registrations.all()
        if not registrations.exists():
            return '-'
        
        paid = registrations.filter(payment_status='paid').count()
        pending = registrations.filter(payment_status='pending').count()
        total = registrations.count()
        
        if paid == total:
            return format_html('<span style="color: green; font-weight: bold;">✓ Todas pagadas ({}/{})</span>', paid, total)
        elif paid > 0:
            return format_html('<span style="color: orange; font-weight: bold;">⚠ Pagos parciales ({}/{})</span>', paid, total)
        else:
            return format_html('<span style="color: red; font-weight: bold;">✕ Ninguna pagada (0/{})</span>', total)
    
    payment_status.short_description = "Estado de pagos"
    
    def get_queryset(self, request):
        """Optimiza las consultas para evitar N+1 queries."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user').prefetch_related(
            'dogs', 'registrations'
        ).annotate(
            dogs_count=Count('dogs', distinct=True),
            registrations_count=Count('registrations', distinct=True)
        )
        return queryset

@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_display', 'chip_display', 'breed', 'gender', 'vet_status', 'registrations_count', 'payment_status')
    list_filter = ('gender', 'owner__city', 'breed')
    search_fields = ('name', 'microchip_number', 'owner__first_name', 'owner__last_name', 'owner__id_document', 'owner__participant_number')
    readonly_fields = ('created_at', 'updated_at', 'vet_status', 'payment_status')
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'owner', 'microchip_number', 'date_of_birth')
        }),
        ('Características', {
            'fields': ('breed', 'gender', 'weight', 'height')
        }),
        ('Salud y veterinario', {
            'fields': ('vet_status', 'special_needs', 'health_issues', 'medications')
        }),
        ('Estado de pagos', {
            'fields': ('payment_status',)
        }),
        ('Otra información', {
            'fields': ('created_at', 'updated_at', 'additional_info'),
            'classes': ('collapse',),
        }),
    )
    
    def owner_display(self, obj):
        """Muestra el nombre del propietario con enlace."""
        if obj.owner:
            try:
                url = reverse('admin:participants_participant_change', args=[obj.owner.id])
                participant_num = f"#{obj.owner.participant_number}" if obj.owner.participant_number else ""
                return format_html('<a href="{}">{} {}</a>', url, obj.owner.full_name, participant_num)
            except NoReverseMatch:
                return f"{obj.owner.full_name} #{obj.owner.participant_number}" if obj.owner.participant_number else obj.owner.full_name
        return '-'
    
    owner_display.short_description = 'Propietario'
    
    def chip_display(self, obj):
        """Muestra el número de microchip formateado."""
        if obj.microchip_number:
            formatted = obj.microchip_number[:3] + '...' + obj.microchip_number[-4:] if len(obj.microchip_number) > 10 else obj.microchip_number
            return format_html('<span title="{}">{}</span>', obj.microchip_number, formatted)
        return '-'
    
    chip_display.short_description = 'Microchip'
    
    def vet_status(self, obj):
        """Muestra el estado veterinario del perro con formato visual."""
        vet_check = VeterinaryCheck.objects.filter(dog=obj).order_by('-check_time').first()
        
        if vet_check:
            if vet_check.status == 'approved':
                return format_html('<span style="color: green; font-weight: bold;">✓ Aprobado</span>')
            elif vet_check.status == 'rejected':
                return format_html('<span style="color: red; font-weight: bold;">✗ Rechazado</span>')
            elif vet_check.status == 'conditional':
                return format_html('<span style="color: orange; font-weight: bold;">⚠ Condicional</span>')
            else:
                return format_html('<span style="color: blue; font-weight: bold;">⌛ {}</span>', 
                                  vet_check.get_status_display())
        return format_html('<span style="color: gray;">Sin revisión</span>')
    
    vet_status.short_description = "Estado veterinario"
    
    def registrations_count(self, obj):
        """Muestra el número de inscripciones del perro con enlace."""
        count = obj.registrations.count()
        if count:
            try:
                url = reverse('admin:canicross_admin_registrations_registration_changelist') + f'?dog__id__exact={obj.id}'
                return format_html('<a href="{}">{} {}</a>', 
                                  url, count, 'inscripción' if count == 1 else 'inscripciones')
            except NoReverseMatch:
                try:
                    url = reverse('admin:registrations_registration_changelist') + f'?dog__id__exact={obj.id}'
                    return format_html('<a href="{}">{} {}</a>', 
                                     url, count, 'inscripción' if count == 1 else 'inscripciones')
                except NoReverseMatch:
                    return f"{count} {'inscripción' if count == 1 else 'inscripciones'}"
        return '0 inscripciones'
    
    registrations_count.short_description = 'Inscripciones'
    
    def payment_status(self, obj):
        """Muestra un resumen del estado de pago de las inscripciones del perro."""
        # Contar inscripciones por estado de pago
        registrations = obj.registrations.all()
        if not registrations.exists():
            return '-'
        
        paid = registrations.filter(payment_status='paid').count()
        pending = registrations.filter(payment_status='pending').count()
        total = registrations.count()
        
        if paid == total:
            return format_html('<span style="color: green; font-weight: bold;">✓ Pagadas ({}/{})</span>', paid, total)
        elif paid > 0:
            return format_html('<span style="color: orange; font-weight: bold;">⚠ Pagos parciales ({}/{})</span>', paid, total)
        else:
            return format_html('<span style="color: red; font-weight: bold;">✕ No pagadas (0/{})</span>', total)
    
    payment_status.short_description = "Estado de pagos"
    
    def get_queryset(self, request):
        """Optimiza las consultas para evitar N+1 queries."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('owner').prefetch_related(
            'registrations', 'veterinary_checks'
        ).annotate(
            registrations_count=Count('registrations', distinct=True)
        )
        return queryset