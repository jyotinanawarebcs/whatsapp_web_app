from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ACCOUNT_TYPE_CHOICES = (
        ('Promotional', 'Promotional'),
    )
    service = models.CharField(max_length=100, default="WhatsApp PROMOTIONAL Message")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default="Promotional")
    credit = models.IntegerField(default=0)
    validity = models.IntegerField(default=365)
   