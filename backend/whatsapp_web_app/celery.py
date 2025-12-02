"""
Celery configuration for whatsapp_web_app project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_web_app.settings')

# Create Celery app instance
app = Celery('whatsapp_web_app')

# Configure Celery using settings from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    # Check for due automations every minute
    'check-due-automations-every-minute': {
        'task': 'automations.tasks.check_due_automations',
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task to verify Celery is working properly.
    """
    print(f'Request: {self.request!r}')