from rest_framework import serializers
from .models import Automation, AutomationLog

class AutomationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        fields = [
            'name', 'campaign_name', 'automation_type', 'status',
            'schedule_type', 'cron_expression', 'specific_time',
            'message_template',  # Remove date fields for now
            'target_contacts', 'target_groups', 'send_to_all', 'cta_buttons'
        ]
    
    def create(self, validated_data):
        return Automation.objects.create(**validated_data)

class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        exclude = ['start_date', 'end_date', 'specific_date']  # Exclude problematic fields
        read_only_fields = ['messages_sent', 'last_run', 'next_run', 'created_at', 'updated_at']

class AutomationLogSerializer(serializers.ModelSerializer):
    automation_name = serializers.CharField(source='automation.name', read_only=True)
    
    class Meta:
        model = AutomationLog
        fields = '__all__'