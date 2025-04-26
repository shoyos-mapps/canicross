from django.contrib import admin
from .models import RaceResult

@admin.register(RaceResult)
class RaceResultAdmin(admin.ModelAdmin):
    list_display = ('registration', 'status', 'base_time', 'official_time', 
                    'overall_rank', 'category_rank')
    list_filter = ('status', 'registration__race__event', 'registration__race')
    search_fields = ('registration__participant__first_name', 
                     'registration__participant__last_name', 
                     'registration__bib_number')
    readonly_fields = ('created_at', 'updated_at')
