from django.apps import AppConfig

class VirtualnumbersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'virtualnumbers'
    label = 'virtualnumbers_unique'  # Unique label de dein
    verbose_name = "Virtual Numbers"
    
    def ready(self):
        # Keep this empty for now
        pass