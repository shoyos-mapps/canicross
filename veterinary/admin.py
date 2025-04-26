from django.contrib import admin
from django.utils.html import format_html
from .models import VeterinaryCheck, VaccinationRecord, MedicalAlert

class VaccinationRecordInline(admin.TabularInline):
    model = VaccinationRecord
    extra = 1
    fields = ('vaccine_name', 'administration_date', 'expiry_date', 'batch_number', 'verified', 'notes')

class MedicalAlertInline(admin.TabularInline):
    model = MedicalAlert
    extra = 0
    fields = ('priority', 'description', 'status', 'requires_followup', 'notify_staff')

@admin.register(VeterinaryCheck)
class VeterinaryCheckAdmin(admin.ModelAdmin):
    list_display = ('dog', 'registration', 'get_event_name', 'status', 'check_time', 'vaccination_status', 'veterinarian')
    list_filter = ('status', 'vaccines_verified', 'has_injuries', 'has_respiratory_issues', 'has_musculoskeletal_issues')
    search_fields = ('dog__name', 'registration__bib_number', 'registration__participant__first_name', 'registration__participant__last_name')
    inlines = [VaccinationRecordInline, MedicalAlertInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('registration', 'dog', 'veterinarian', 'status', 'check_time')
        }),
        ('Signos Vitales', {
            'fields': ('temperature', 'weight', 'heart_rate')
        }),
        ('Evaluación Física', {
            'fields': ('physical_condition', 'hydration_status')
        }),
        ('Revisión de Sistemas', {
            'fields': (
                'has_injuries', 'injury_details',
                'has_respiratory_issues', 'respiratory_details',
                'has_musculoskeletal_issues', 'musculoskeletal_details',
            )
        }),
        ('Vacunación', {
            'fields': ('vaccines_verified', 'vaccines_notes')
        }),
        ('Evaluación y Recomendaciones', {
            'fields': ('general_notes', 'recommendations')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_event_name(self, obj):
        return obj.registration.race.event.name
    get_event_name.short_description = 'Evento'
    
    def vaccination_status(self, obj):
        if obj.vaccines_verified:
            return format_html('<span style="color: green;">✓ Verificado</span>')
        return format_html('<span style="color: orange;">⚠ Pendiente</span>')
    vaccination_status.short_description = 'Vacunas'

@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ('vaccine_name', 'administration_date', 'expiry_date', 'get_dog_name', 'verified')
    list_filter = ('verified', 'administration_date')
    search_fields = ('vaccine_name', 'veterinary_check__dog__name')
    
    def get_dog_name(self, obj):
        return obj.veterinary_check.dog.name
    get_dog_name.short_description = 'Perro'

@admin.register(MedicalAlert)
class MedicalAlertAdmin(admin.ModelAdmin):
    list_display = ('get_dog_name', 'priority', 'status', 'description_short', 'requires_followup', 'created_by', 'created_at')
    list_filter = ('priority', 'status', 'requires_followup', 'created_at')
    search_fields = ('description', 'veterinary_check__dog__name')
    
    def get_dog_name(self, obj):
        return obj.veterinary_check.dog.name
    get_dog_name.short_description = 'Perro'
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Descripción'
