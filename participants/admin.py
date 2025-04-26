from django.contrib import admin
from .models import Participant, Dog

class DogInline(admin.TabularInline):
    model = Dog
    extra = 1

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'id_document', 'gender', 'email', 'phone', 'get_age')
    list_filter = ('gender',)
    search_fields = ('first_name', 'last_name', 'id_document', 'email')
    inlines = [DogInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'owner', 'gender', 'microchip_number')
    list_filter = ('breed', 'gender')
    search_fields = ('name', 'microchip_number', 'owner__first_name', 'owner__last_name')
    readonly_fields = ('created_at', 'updated_at')
