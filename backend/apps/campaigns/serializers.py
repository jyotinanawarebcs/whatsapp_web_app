from rest_framework import serializers

SUPPORTED_MEDIA_TYPES = ['image', 'video', 'document', 'audio']

class CampaignCtaButtonSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['URL', 'PHONE', 'QUICK_REPLY'])
    title = serializers.CharField(max_length=120)
    payload = serializers.CharField(required=False, allow_blank=True)
    url = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

class CreateCampaignSerializer(serializers.Serializer):
    campaign_name = serializers.CharField(max_length=150)
    name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    template_id = serializers.IntegerField(required=False)
    caption = serializers.CharField(required=False, allow_blank=True)
    media_url = serializers.CharField(required=False, allow_blank=True)
    media_type = serializers.ChoiceField(choices=SUPPORTED_MEDIA_TYPES, required=False)
    media_name = serializers.CharField(required=False, allow_blank=True)
    attachment_url = serializers.CharField(required=False, allow_blank=True)
    media_mime_type = serializers.CharField(required=False, allow_blank=True)
    media_size = serializers.IntegerField(required=False, min_value=0)
    cta_buttons = CampaignCtaButtonSerializer(many=True, required=False)
    status = serializers.CharField(required=False)
    scheduled_start = serializers.DateTimeField(required=False)
    scheduled_end = serializers.DateTimeField(required=False)

class UpdateCampaignSerializer(serializers.Serializer):
    campaign_name = serializers.CharField(required=False, max_length=150)
    name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    template_id = serializers.IntegerField(required=False)
    caption = serializers.CharField(required=False, allow_blank=True)
    media_url = serializers.CharField(required=False, allow_blank=True)
    media_type = serializers.ChoiceField(choices=SUPPORTED_MEDIA_TYPES, required=False)
    media_name = serializers.CharField(required=False, allow_blank=True)
    attachment_url = serializers.CharField(required=False, allow_blank=True)
    media_mime_type = serializers.CharField(required=False, allow_blank=True)
    media_size = serializers.IntegerField(required=False, min_value=0)
    cta_buttons = CampaignCtaButtonSerializer(many=True, required=False)
    status = serializers.CharField(required=False)
    scheduled_start = serializers.DateTimeField(required=False)
    scheduled_end = serializers.DateTimeField(required=False)

class RunCampaignSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField(min_value=1)
    virtual_number_id = serializers.IntegerField(min_value=1, required=False)
    recipients_count = serializers.IntegerField(min_value=1)
    start_immediately = serializers.BooleanField(default=True)
    contact_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False
    )