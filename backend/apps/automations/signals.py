from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Automation

@receiver(post_save, sender=Automation)
def create_log(sender, instance, created, **kwargs):
    if created:
        print("Automation Created:", instance.id)
