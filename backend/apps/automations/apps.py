# apps/automations/apps.py
from django.apps import AppConfig

class AutomationsConfig(AppConfig):  # ✓ CORRECT - yeh Automations ke liye hai
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'automations'  # Ya 'apps.automations' depending on your structure
    label = 'automations'