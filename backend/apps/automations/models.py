from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Automation(models.Model):
    """
    Model to store automation configurations for WhatsApp messaging.
    """
    # Automation type choices
    AUTOMATION_TYPES = [
        ('birthday', 'Birthday Messages'),
        ('festival', 'Festival Greetings'),
        ('reminder', 'Payment Reminders'),
        ('followup', 'Follow-up Messages'),
        ('custom', 'Custom Campaign'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('draft', 'Draft'),
    ]
    
    # Schedule type choices
    SCHEDULE_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('specific_date', 'Specific Date'),
        ('on_event', 'On Event'),
    ]

    # Basic information
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automations')
    name = models.CharField(max_length=255, help_text="Name of the automation")
    campaign_name = models.CharField(max_length=255, blank=True, help_text="Campaign name")
    automation_type = models.CharField(max_length=20, choices=AUTOMATION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # Schedule configuration
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES)
    cron_expression = models.CharField(max_length=100, blank=True, null=True)
    specific_time = models.TimeField(blank=True, null=True)
    specific_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)

    # Message content
    message_template = models.TextField(help_text="Message template with variables like {{name}}")

    # Target configuration
    target_contacts = models.JSONField(default=list, help_text="List of specific contact IDs to target")
    target_groups = models.JSONField(default=list, help_text="List of group names to target")
    send_to_all = models.BooleanField(default=False, help_text="Send to all contacts")

    # CTA Buttons configuration
    cta_buttons = models.JSONField(
        default=list, 
        help_text="List of CTA buttons (max 3)"
    )

    # Statistics and tracking
    messages_sent = models.PositiveIntegerField(default=0)
    last_run = models.DateTimeField(blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    class Meta:
        app_label = 'automations'  # ✅ ADD THIS LINE
        ordering = ['-created_at']
        verbose_name = 'Automation'
        verbose_name_plural = 'Automations'

class AutomationLog(models.Model):
    """
    Model to store execution logs for each automation run.
    """
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='logs')
    run_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('partial', 'Partial Success'),
        ]
    )
    messages_sent = models.PositiveIntegerField(default=0)
    total_contacts = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.automation.name} - {self.run_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        app_label = 'automations'  # ✅ ADD THIS LINE
        ordering = ['-run_time']
        verbose_name = 'Automation Log'
        verbose_name_plural = 'Automation Logs'