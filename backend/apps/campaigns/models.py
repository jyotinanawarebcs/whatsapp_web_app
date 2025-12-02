from django.db import models
from django.contrib.auth import get_user_model

# User = get_user_model()

class Campaign(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign_name = models.CharField(max_length=150)
    name = models.CharField(max_length=150, null=True, blank=True)
    template_id = models.IntegerField(null=True, blank=True)
    caption = models.TextField(null=True, blank=True)
    media_url = models.TextField(null=True, blank=True)
    media_type = models.CharField(max_length=50, null=True, blank=True)
    media_name = models.CharField(max_length=255, null=True, blank=True)
    attachment_url = models.TextField(null=True, blank=True)
    cta_buttons = models.JSONField(default=list)
    status = models.CharField(max_length=20, default='draft')
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    recipients_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.campaign_name

    class Meta:
        app_label = 'campaigns'  # ✅ ADD THIS
        db_table = 'campaigns'

class CampaignContact(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE)
    sequence = models.IntegerField()
    job_id = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.campaign.campaign_name} - {self.contact.name}"

    class Meta:
        app_label = 'campaigns'  # ✅ ADD THIS
        db_table = 'campaign_contacts'
        unique_together = [['campaign', 'contact']]
        indexes = [
            models.Index(fields=['campaign', 'job_id']),
        ]

class MessageTemplate(models.Model):
    TEMPLATE_APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    PROVIDER_VALIDATION_STATUS = [
        ('not_required', 'Not Required'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ]
    
    TEMPLATE_VALIDATION_MODE = [
        ('meta', 'Meta'),
        ('dlt', 'DLT'),
        ('bsp', 'BSP'),
        ('all', 'All'),
    ]

    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=60, null=True, blank=True)
    language = models.CharField(max_length=10, default='en_US')
    body = models.TextField()
    header = models.TextField(null=True, blank=True)
    footer = models.TextField(null=True, blank=True)
    cta_button = models.JSONField(null=True, blank=True)
    attachment_url = models.TextField(null=True, blank=True)
    variables = models.JSONField(null=True, blank=True)
    sample_parameters = models.JSONField(default=list)
    validation_mode = models.CharField(max_length=10, choices=TEMPLATE_VALIDATION_MODE, default='meta')
    bsp_provider = models.CharField(max_length=120, null=True, blank=True)
    meta_template_id = models.CharField(max_length=120, null=True, blank=True)
    dlt_template_id = models.CharField(max_length=120, null=True, blank=True)
    bsp_template_id = models.CharField(max_length=120, null=True, blank=True)
    meta_status = models.CharField(max_length=20, choices=PROVIDER_VALIDATION_STATUS, default='pending')
    meta_rejection_reason = models.TextField(null=True, blank=True)
    dlt_status = models.CharField(max_length=20, choices=PROVIDER_VALIDATION_STATUS, default='not_required')
    dlt_rejection_reason = models.TextField(null=True, blank=True)
    bsp_status = models.CharField(max_length=20, choices=PROVIDER_VALIDATION_STATUS, default='not_required')
    bsp_rejection_reason = models.TextField(null=True, blank=True)
    approval_status = models.CharField(max_length=20, choices=TEMPLATE_APPROVAL_STATUS, default='pending')
    rejection_reason = models.TextField(null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'campaigns'  # ✅ ADD THIS
        db_table = 'message_templates'