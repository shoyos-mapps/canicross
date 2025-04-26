from django.contrib import admin
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
    list_display = ('participant', 'dog', 'race', 'bib_number', 'registration_status', 'payment_status', 
                    'ai_vaccine_status', 'vet_check_status', 'kit_delivered', 'checked_in')
    list_filter = ('registration_status', 'payment_status', 'ai_vaccine_status', 'vet_check_status', 
                   'kit_delivered', 'checked_in', 'race__event', 'race')
    search_fields = ('participant__first_name', 'participant__last_name', 'participant__id_document', 'bib_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DocumentInline, ParticipantAnnotationInline]

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
