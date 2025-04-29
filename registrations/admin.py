from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Registration, Document, ParticipantAnnotation

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    readonly_fields = ('ocr_raw_text', 'ocr_status', 'ocr_analysis_result', 'uploaded_at')

class ParticipantAnnotationInline(admin.TabularInline):
    model = ParticipantAnnotation
    extra = 1
    readonly_fields = ('recorded_at', 'updated_at')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('participant', 'dog', 'race', 'bib_number', 'registration_status', 
                    'payment_status_colored', 'payment_amount', 'payment_date_formatted', 
                    'ai_vaccine_status', 'vet_check_status', 'kit_delivered', 'checked_in')
    list_filter = ('registration_status', 'payment_status', 'payment_method', 'ai_vaccine_status', 
                   'vet_check_status', 'kit_delivered', 'checked_in', 'race__event', 'race')
    search_fields = ('participant__first_name', 'participant__last_name', 
                     'participant__id_document', 'bib_number', 'payment_reference')
    
    # Agrupar campos en fieldsets para mejor organización
    fieldsets = (
        ('Información básica', {
            'fields': ('participant', 'dog', 'race', 'race_category', 'bib_number', 'registration_status')
        }),
        ('Información de pago', {
            'fields': ('payment_status', 'payment_amount', 'payment_date', 'payment_method', 'payment_reference'),
            'classes': ('wide',)
        }),
        ('Estado de verificación', {
            'fields': ('ai_vaccine_status', 'vet_check_status', 'vet_check_time', 'vet_checker_details'),
        }),
        ('Check-in y entrega de kit', {
            'fields': ('kit_delivered', 'kit_delivery_time', 'checked_in', 'checkin_time'),
        }),
        ('Miscelánea', {
            'fields': ('notes', 'waiver_accepted', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DocumentInline, ParticipantAnnotationInline]
    
    def payment_status_colored(self, obj):
        """Muestra el estado de pago con colores para mejor visualización"""
        if obj.payment_status == 'paid':
            return format_html('<span style="color: green; font-weight: bold;">✓ {}</span>', 
                              obj.get_payment_status_display())
        elif obj.payment_status == 'pending':
            return format_html('<span style="color: orange; font-weight: bold;">⌛ {}</span>', 
                              obj.get_payment_status_display())
        elif obj.payment_status == 'refunded':
            return format_html('<span style="color: blue; font-weight: bold;">↩ {}</span>', 
                              obj.get_payment_status_display())
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ {}</span>', 
                              obj.get_payment_status_display())
    
    payment_status_colored.short_description = "Estado de pago"
    payment_status_colored.admin_order_field = 'payment_status'
    
    def payment_date_formatted(self, obj):
        """Formatea la fecha de pago de forma más legible"""
        if obj.payment_date:
            return obj.payment_date.strftime("%d/%m/%Y %H:%M")
        return "-"
    
    payment_date_formatted.short_description = "Fecha de pago"
    payment_date_formatted.admin_order_field = 'payment_date'
    
    def get_readonly_fields(self, request, obj=None):
        """Control which fields are read-only based on user permissions"""
        readonly_fields = list(self.readonly_fields)
        
        # If not admin, staff, or volunteer, make payment fields read-only
        if not (request.user.is_admin() or request.user.is_staff_member()):
            readonly_fields.extend(['payment_status', 'payment_amount', 'payment_date', 
                                  'payment_method', 'payment_reference'])
        
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Guardar fecha de pago automáticamente si el estado cambia a 'paid'"""
        # Si el estado de pago cambió a 'paid' y no hay fecha de pago, añadirla
        if 'payment_status' in form.changed_data and obj.payment_status == 'paid' and not obj.payment_date:
            obj.payment_date = timezone.now()
        
        super().save_model(request, obj, form, change)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'registration', 'ocr_status', 'uploaded_at')
    list_filter = ('document_type', 'ocr_status', 'registration__race__event')
    search_fields = ('registration__participant__first_name', 'registration__participant__last_name')
    readonly_fields = ('ocr_raw_text', 'ocr_status', 'ocr_analysis_result', 'uploaded_at')

@admin.register(ParticipantAnnotation)
class ParticipantAnnotationAdmin(admin.ModelAdmin):
    list_display = ('registration', 'penalty_type', 'status', 'recorded_by', 'confirmed_by', 'recorded_at')
    list_filter = ('status', 'penalty_type', 'registration__race__event')
    search_fields = ('registration__participant__first_name', 'registration__participant__last_name', 
                     'registration__bib_number', 'notes')
    readonly_fields = ('recorded_at', 'updated_at')