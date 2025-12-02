from rest_framework import serializers
from .models import BusinessNumber, VirtualNumber, VirtualNumberStatus, VirtualNumberQuality

# Create Virtual Number Serializer
class CreateVirtualNumberSerializer(serializers.Serializer):
    business_number_id = serializers.IntegerField(required=False)
    waba_id = serializers.CharField(max_length=64)
    phone_number_id = serializers.CharField(max_length=64)
    access_token = serializers.CharField()
    status = serializers.ChoiceField(choices=VirtualNumberStatus.choices, required=False)
    quality_rating = serializers.ChoiceField(choices=VirtualNumberQuality.choices, required=False)
    is_primary = serializers.BooleanField(default=False)

# Manual Switch Serializer
class ManualSwitchSerializer(serializers.Serializer):
    target_id = serializers.IntegerField(required=False)

# Update Business Number Serializer
class UpdateBusinessNumberSerializer(serializers.Serializer):
    business_name = serializers.CharField(max_length=128, required=False, allow_blank=True)
    waba_id = serializers.CharField(max_length=64)
    phone_number_id = serializers.CharField(max_length=64)
    access_token = serializers.CharField()
    auto_switch_enabled = serializers.BooleanField(required=False)

# Update Virtual Number Serializer
class UpdateVirtualNumberSerializer(serializers.Serializer):
    business_number_id = serializers.IntegerField(required=False)
    waba_id = serializers.CharField(max_length=64, required=False)
    phone_number_id = serializers.CharField(max_length=64, required=False)
    access_token = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=VirtualNumberStatus.choices, required=False)
    quality_rating = serializers.ChoiceField(choices=VirtualNumberQuality.choices, required=False)
    is_primary = serializers.BooleanField(required=False)
    message_count_24h = serializers.IntegerField(required=False)
    last_used_at = serializers.DateTimeField(required=False)