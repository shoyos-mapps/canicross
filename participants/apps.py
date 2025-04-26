from django.apps import AppConfig


class ParticipantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'participants'
    
    def ready(self):
        # Importar templatetags para que estén disponibles
        import participants.templatetags.form_tags
