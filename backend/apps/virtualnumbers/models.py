from django.db import models
from django.contrib.auth import get_user_model

# User = get_user_model()

# Enums define karein
class VirtualNumberStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    SUSPENDED = 'suspended', 'Suspended'

class VirtualNumberQuality(models.TextChoices):
    UNKNOWN = 'unknown',
from django.contrib.auth import get_user_model

# User = get_user_model()

# Enums define karein
class VirtualNumberStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    SUSPENDED = 'suspended', 'Suspended'

class VirtualNumberQuality(models.TextChoices):
    UNKNOWN = 'unknown', 'Unknown'
    HIGH = 'high', 'High'
    MEDIUM = 'medium', 'Medium'
    LOW = 'low', 'Low'

# BusinessNumber Model
class BusinessNumber(models.Model):
    business_name = models.CharField(max_length=128, null=True, blank=True)
    waba_id = models.CharField(max_length=64)
    phone_number_id = models.CharField(max_length=64, unique=True)
    display_phone_number = models.CharField(max_length=32, null=True, blank=True)
    access_token = models.TextField()
    auto_switch_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'virtualnumbers'  # ✅ ADD THIS LINE
        db_table = 'business_numbers'

    def __str__(self):
        return f"{self.business_name or 'Unknown'} - {self.display_phone_number}"

# VirtualNumber Model
class VirtualNumber(models.Model):
    business_number = models.ForeignKey(
        BusinessNumber, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='virtual_numbers'
    )
    waba_id = models.CharField(max_length=64)
    phone_number_id = models.CharField(max_length=64, unique=True)
    access_token = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=VirtualNumberStatus.choices, 
        default=VirtualNumberStatus.ACTIVE
    )
    quality_rating = models.CharField(
        max_length=20,
        choices=VirtualNumberQuality.choices,
        default=VirtualNumberQuality.UNKNOWN
    )
    is_primary = models.BooleanField(default=False)
    message_count_24h = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'virtualnumbers'  # ✅ ADD THIS LINE
        db_table = 'virtual_numbers'
        indexes = [
            models.Index(fields=['is_primary']),
        ]

    def __str__(self):
        return f"Virtual Number {self.phone_number_id} - {self.status}" 'Unknown'
    HIGH = 'high', 'High'
    MEDIUM = 'medium', 'Medium'
    LOW = 'low', 'Low'

# BusinessNumber Model
class BusinessNumber(models.Model):
    business_name = models.CharField(max_length=128, null=True, blank=True)
    waba_id = models.CharField(max_length=64)
    phone_number_id = models.CharField(max_length=64, unique=True)
    display_phone_number = models.CharField(max_length=32, null=True, blank=True)
    access_token = models.TextField()
    auto_switch_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_numbers'

    def __str__(self):
        return f"{self.business_name or 'Unknown'} - {self.display_phone_number}"

# VirtualNumber Model
class VirtualNumber(models.Model):
    business_number = models.ForeignKey(
        BusinessNumber, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='virtual_numbers'
    )
    waba_id = models.CharField(max_length=64)
    phone_number_id = models.CharField(max_length=64, unique=True)
    access_token = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=VirtualNumberStatus.choices, 
        default=VirtualNumberStatus.ACTIVE
    )
    quality_rating = models.CharField(
        max_length=20,
        choices=VirtualNumberQuality.choices,
        default=VirtualNumberQuality.UNKNOWN
    )
    is_primary = models.BooleanField(default=False)
    message_count_24h = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'virtual_numbers'
        indexes = [
            models.Index(fields=['is_primary']),
        ]

    def __str__(self):
        return f"Virtual Number {self.phone_number_id} - {self.status}"