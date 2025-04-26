from django.contrib import admin
from django.utils.html import format_html
from .models import Result, TimeRecord, Penalty

class TimeRecordInline(admin.TabularInline):
    model = TimeRecord
    extra = 0
    fields = ('checkpoint_number', 'time_seconds', 'get_formatted_time', 'recorded_by')
    readonly_fields = ('get_formatted_time', 'recorded_by')
    
    def get_formatted_time(self, obj):
        return obj.format_time()
    get_formatted_time.short_description = "Tiempo formateado"

class PenaltyInline(admin.TabularInline):
    model = Penalty
    extra = 0
    fields = ('penalty_type', 'description', 'recorded_by', 'recorded_at')
    readonly_fields = ('recorded_by', 'recorded_at')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('get_participant', 'get_event', 'get_race', 'status', 
                   'get_formatted_time', 'position', 'recorded_by')
    list_filter = ('status', 'registration__race__event', 'registration__race')
    search_fields = ('registration__participant__first_name', 
                     'registration__participant__last_name', 
                     'registration__bib_number')
    readonly_fields = ('recorded_by', 'recorded_at', 'verified_by', 'verified_at',
                       'created_at', 'updated_at')
    inlines = [TimeRecordInline, PenaltyInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('registration', 'status', 'official_time_seconds', 'position')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Auditoría', {
            'fields': ('recorded_by', 'recorded_at', 'verified_by', 'verified_at', 
                      'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_participant(self, obj):
        return f"{obj.registration.participant.first_name} {obj.registration.participant.last_name}"
    get_participant.short_description = "Participante"
    
    def get_event(self, obj):
        return obj.registration.race.event.name
    get_event.short_description = "Evento"
    
    def get_race(self, obj):
        return obj.registration.race.name
    get_race.short_description = "Carrera"
    
    def get_formatted_time(self, obj):
        time_str = obj.format_time()
        if obj.status == 'verified':
            return format_html('<span style="color: green;">{}</span>', time_str)
        elif obj.status in ['disqualified', 'dnf', 'dns']:
            return format_html('<span style="color: red;">{} - {}</span>', 
                              time_str, obj.get_status_display())
        return time_str
    get_formatted_time.short_description = "Tiempo"

@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ('get_participant', 'checkpoint_number', 'get_formatted_time', 'recorded_by')
    list_filter = ('result__registration__race', 'checkpoint_number')
    search_fields = ('result__registration__participant__first_name',
                    'result__registration__participant__last_name')
    
    def get_participant(self, obj):
        return f"{obj.result.registration.participant.first_name} {obj.result.registration.participant.last_name}"
    get_participant.short_description = "Participante"
    
    def get_formatted_time(self, obj):
        return obj.format_time()
    get_formatted_time.short_description = "Tiempo"

@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('get_participant', 'penalty_type', 'description', 'recorded_by', 'recorded_at')
    list_filter = ('penalty_type', 'result__registration__race', 'recorded_at')
    search_fields = ('result__registration__participant__first_name',
                    'result__registration__participant__last_name',
                    'description')
    
    def get_participant(self, obj):
        return f"{obj.result.registration.participant.first_name} {obj.result.registration.participant.last_name}"
    get_participant.short_description = "Participante"