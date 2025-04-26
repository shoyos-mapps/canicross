from django.contrib import admin
from django.utils.html import format_html
from .models import Event, Modality, Race, Category, RaceCategory, PenaltyType

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start_date', 'end_date', 'status', 'show_urls')
    list_filter = ('status', 'start_date')
    search_fields = ('name', 'location')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('event_urls',)
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'location', 'status')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'registration_start', 'registration_end')
        }),
        ('Requisitos', {
            'fields': ('rules', 'required_documents', 'required_vaccines')
        }),
        ('URLs del Evento', {
            'fields': ('event_urls',),
            'classes': ('collapse',),
        }),
    )
    
    def event_urls(self, obj):
        """Mostrar las URLs del evento en la página de detalles del evento."""
        if not obj.pk:
            return "Las URLs estarán disponibles después de guardar el evento."
            
        detail_url = f"/events/{obj.slug}/"
        races_url = f"/events/{obj.slug}/races/"
        register_url = f"/events/{obj.slug}/register/"
        
        return format_html(
            '<strong>URL del Evento:</strong> <a href="{}" target="_blank">{}</a><br/>'
            '<strong>URL de Carreras:</strong> <a href="{}" target="_blank">{}</a><br/>'
            '<strong>URL de Registro:</strong> <a href="{}" target="_blank">{}</a><br/>'
            '<br/><em>Nota: Estas URLs pueden ser compartidas con los participantes.</em>',
            detail_url, detail_url,
            races_url, races_url,
            register_url, register_url
        )
    event_urls.short_description = "URLs del Evento"
    
    def show_urls(self, obj):
        """Mostrar un enlace para ver el evento en la lista de eventos."""
        return format_html('<a href="/events/{}/register/" target="_blank">URL de Registro</a>', obj.slug)
    show_urls.short_description = "Registro"

@admin.register(Modality)
class ModalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class RaceCategoryInline(admin.TabularInline):
    model = RaceCategory
    extra = 1

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'modality', 'distance', 'race_date', 'start_type')
    list_filter = ('event', 'modality', 'start_type')
    search_fields = ('name',)
    inlines = [RaceCategoryInline]
    readonly_fields = ('race_url',)
    
    def race_url(self, obj):
        """Mostrar la URL de la carrera en la página de detalles."""
        if not obj.pk or not obj.event:
            return "La URL estará disponible después de guardar la carrera."
            
        url = f"/events/{obj.event.slug}/races/{obj.pk}/"
        return format_html(
            '<strong>URL de la Carrera:</strong> <a href="{}" target="_blank">{}</a><br/>'
            '<br/><em>Comparte esta URL para información específica de esta carrera.</em>',
            url, url
        )
    race_url.short_description = "URL de la Carrera"
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('event', 'modality', 'name', 'description', 'distance')
        }),
        ('Configuración de Salida', {
            'fields': ('start_type', 'participants_per_interval', 'interval_seconds', 'max_participants')
        }),
        ('Fechas y Horarios', {
            'fields': ('race_date', 'race_time', 'actual_start_time')
        }),
        ('URL de la Carrera', {
            'fields': ('race_url',),
            'classes': ('collapse',),
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'min_age', 'max_age')
    list_filter = ('gender',)
    search_fields = ('name',)

@admin.register(RaceCategory)
class RaceCategoryAdmin(admin.ModelAdmin):
    list_display = ('race', 'category', 'price', 'quota')
    list_filter = ('race__event', 'race', 'category')

@admin.register(PenaltyType)
class PenaltyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'time_penalty', 'is_disqualification')
    list_filter = ('is_disqualification',)
    search_fields = ('name', 'description')