from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
 
class WhatsAppCloudNumber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    waba_id = models.CharField(max_length=50, null=True, blank=True)
    access_token = models.TextField()
    
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_number or self.phone_number_id

class MessageLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cloud_number = models.ForeignKey(WhatsAppCloudNumber, on_delete=models.CASCADE)
    receiver = models.CharField(max_length=20)
    template_name = models.CharField(max_length=150)

    message_id = models.CharField(max_length=150, blank=True, null=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)

    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receiver}  {self.template_name}"

# import uuid
# from django.conf import settings
# from django.db import models
# from django.contrib.auth.models import AbstractUser

# # class NumberRoutingMode(models.TextChoices):
# #     VIRTUAL = "virtual", "Virtual"
# #     DIRECT = "direct", "Direct"


# class TemplateApprovalStatus(models.TextChoices):    
#     PENDING = "pending", "Pending"
#     APPROVED = "approved", "Approved"
#     REJECTED = "rejected", "Rejected"


# class ProviderValidationStatus(models.TextChoices):
#     NOT_REQUIRED = "not_required", "Not Required"
#     PENDING = "pending", "Pending"
#     IN_PROGRESS = "in_progress", "In Progress"
#     APPROVED = "approved", "Approved"
#     REJECTED = "rejected", "Rejected"
#     FAILED = "failed", "Failed"


# class TemplateValidationMode(models.TextChoices):
#     META = "meta", "Meta"
#     DLT = "dlt", "DLT"
#     BSP = "bsp", "BSP"
#     ALL = "all", "All"



# # class CampaignJobStatus(models.TextChoices):
# #     QUEUED = "queued", "Queued"
# #     IN_PROGRESS = "in_progress", "In Progress"
# #     COMPLETED = "completed", "Completed"
# #     FAILED = "failed", "Failed"
# #     CANCELLED = "cancelled", "Cancelled"


# # class SentMessageStatus(models.TextChoices):
# #     PENDING = "pending", "Pending"
# #     SENT = "sent", "Sent"
# #     FAILED = "failed", "Failed"

# from datetime import date, timedelta
# class CustomUser(AbstractUser):
#     ACCOUNT_TYPE_CHOICES = (
#         ('Promotional', 'Promotional'),
#     )
#     service = models.CharField(max_length=100, default="WhatsApp PROMOTIONAL Message")
#     account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default="Promotional")
#     credit = models.IntegerField(default=0)
#     validity = models.DateField(default=date.today)

from django.db import models
from django.conf import settings

class Campaign(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )

    campaign_name = models.CharField(max_length=150)
    template_name = models.CharField(max_length=150, blank=True, null=True)

    caption = models.TextField(blank=True, null=True)

    media_url = models.URLField(blank=True, null=True)
    media_type = models.CharField(max_length=50, blank=True, null=True)
    media_name = models.CharField(max_length=255, blank=True, null=True)

    attachment_url = models.URLField(blank=True, null=True)

    cta_buttons = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=20,
        default="draft",
        choices=STATUS_CHOICES
    )

    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)

    recipients_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)

    last_run_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return self.campaign_name




# class CampaignRecipient(models.Model):
#     campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="recipients")
#     phone_number = models.CharField(max_length=20)
#     name = models.CharField(max_length=150, blank=True, null=True)
#     status = models.CharField(max_length=20, default="pending")  
#     message_id = models.CharField(max_length=200, blank=True, null=True)

#     sent_at = models.DateTimeField(blank=True, null=True)
#     delivered_at = models.DateTimeField(blank=True, null=True)
#     read_at = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.phone_number}  {self.campaign.campaign_name}"




# # class BusinessNumber(models.Model):
# #     business_name = models.CharField(max_length=128, blank=True, null=True)
# #     waba_id = models.CharField(max_length=64, blank=True, null=True)
# #     phone_number_id = models.CharField(max_length=64, unique=True)
# #     display_phone_number = models.CharField(max_length=32, blank=True, null=True)
# #     access_token = models.TextField(blank=True, null=True)
# #     auto_switch_enabled = models.BooleanField(default=True)

# #     routing_mode = models.CharField(
# #         max_length=20, choices=NumberRoutingMode.choices, default=NumberRoutingMode.VIRTUAL
# #     )

# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     def __str__(self):
# #         return self.business_name or self.phone_number_id


# # class VirtualNumber(models.Model):
# #     business_number = models.ForeignKey(
# #         BusinessNumber, on_delete=models.CASCADE, related_name="virtual_numbers"
# #     )
# #     number = models.CharField(max_length=32, unique=True)  # The virtual phone number itself
# #     display_name = models.CharField(max_length=128, blank=True, null=True)

# #     is_active = models.BooleanField(default=True)
# #     assigned_user = models.ForeignKey(
# #         settings.AUTH_USER_MODEL,
# #         on_delete=models.SET_NULL,
# #         blank=True,
# #         null=True,
# #         related_name="virtual_numbers",
# #     )

# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     routing_priority = models.PositiveIntegerField(default=0)
# #     description = models.TextField(blank=True, null=True)

# #     class Meta:
# #         ordering = ("routing_priority", "number")

# #     def __str__(self):
# #         return self.number




# class MessageTemplate(models.Model):
#     name = models.CharField(max_length=150, unique=True)
#     category = models.CharField(max_length=60, blank=True, null=True)
#     language = models.CharField(max_length=10, default="en_US")
#     body = models.TextField()
#     header = models.TextField(blank=True, null=True)
#     footer = models.TextField(blank=True, null=True)

#     cta_button = models.JSONField(blank=True, null=True)
#     attachment_url = models.TextField(blank=True, null=True)
#     variables = models.JSONField(blank=True, null=True)
#     sample_parameters = models.JSONField(default=list, blank=True)

#     validation_mode = models.CharField(
#         max_length=10, choices=TemplateValidationMode.choices, default=TemplateValidationMode.META
#     )

#     bsp_provider = models.CharField(max_length=120, blank=True, null=True)
#     meta_template_id = models.CharField(max_length=120, blank=True, null=True)
#     dlt_template_id = models.CharField(max_length=120, blank=True, null=True)
#     bsp_template_id = models.CharField(max_length=120, blank=True, null=True)

#     meta_status = models.CharField(
#         max_length=20, choices=ProviderValidationStatus.choices, default=ProviderValidationStatus.PENDING
#     )
#     meta_rejection_reason = models.TextField(blank=True, null=True)

#     dlt_status = models.CharField(
#         max_length=20, choices=ProviderValidationStatus.choices, default=ProviderValidationStatus.NOT_REQUIRED
#     )
#     dlt_rejection_reason = models.TextField(blank=True, null=True)

#     bsp_status = models.CharField(
#         max_length=20, choices=ProviderValidationStatus.choices, default=ProviderValidationStatus.NOT_REQUIRED
#     )
#     bsp_rejection_reason = models.TextField(blank=True, null=True)

#     approval_status = models.CharField(
#         max_length=20, choices=TemplateApprovalStatus.choices, default=TemplateApprovalStatus.PENDING
#     )
#     rejection_reason = models.TextField(blank=True, null=True)

#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         related_name="created_templates",
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ("created_at",)

#     def __str__(self):
#         return self.name




# # class WebhookLog(models.Model):
# #     event_type = models.CharField(max_length=128, blank=True, null=True)
# #     payload = models.JSONField(blank=True, null=True)
# #     status_code = models.IntegerField(blank=True, null=True)
# #     received_at = models.DateTimeField(auto_now_add=True)

# #     def __str__(self):
# #         return f"WebhookLog {self.id}  {self.event_type or 'No Event'}"


# # # 
# # # CampaignJob
# # # 
# # class CampaignJob(models.Model):
# #     campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE, related_name="campaign_jobs")

# #     # Prefer FK to user; keep a legacy integer (user_id) only if you have external systems depending on it.
# #     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaign_jobs")

# #     # Virtual / business number relations
# #     virtual_number = models.ForeignKey(
# #         VirtualNumber, on_delete=models.SET_NULL, blank=True, null=True, related_name="campaign_jobs"
# #     )
# #     virtual_number_label = models.CharField(max_length=255, blank=True, null=True)

# #     business_number = models.ForeignKey(
# #         BusinessNumber, on_delete=models.SET_NULL, blank=True, null=True, related_name="campaign_jobs"
# #     )
# #     # some systems stored a short label; keep a separate char field for humanreadable name
# #     business_number_label = models.CharField(max_length=255, blank=True, null=True)

# #     caption = models.TextField(blank=True, null=True)
# #     media_url = models.TextField(blank=True, null=True)
# #     media_type = models.CharField(max_length=50, blank=True, null=True)
# #     media_name = models.CharField(max_length=255, blank=True, null=True)

# #     cta = models.JSONField(blank=True, null=True, default=list)

# #     job_id = models.CharField(max_length=128)
# #     batch_index = models.IntegerField()
# #     total_batches = models.IntegerField()
# #     size = models.IntegerField()

# #     status = models.CharField(max_length=32, choices=CampaignJobStatus.choices)

# #     attempt = models.IntegerField(default=0)
# #     error = models.TextField(blank=True, null=True)

# #     queued_at = models.DateTimeField(auto_now_add=True)
# #     started_at = models.DateTimeField(blank=True, null=True)
# #     finished_at = models.DateTimeField(blank=True, null=True)

# #     class Meta:
# #         indexes = [
# #             models.Index(fields=["job_id"]),
# #             models.Index(fields=["status"]),
# #         ]
# #         ordering = ("queued_at",)

# #     def __str__(self):
# #         return f"{self.job_id} ({self.status})"

# # class SentMessage(models.Model):
# #     campaign = models.ForeignKey(
# #         "Campaign", on_delete=models.CASCADE, related_name="sent_messages"
# #     )

# #     campaign_job = models.ForeignKey(
# #         CampaignJob, on_delete=models.CASCADE, related_name="sent_messages"
# #     )

# #     contact = models.ForeignKey(
# #         "Contact", on_delete=models.SET_NULL, blank=True, null=True, related_name="sent_messages"
# #     )

# #     to_phone = models.CharField(max_length=32)

# #     virtual_number = models.ForeignKey(
# #         VirtualNumber, on_delete=models.SET_NULL, blank=True, null=True, related_name="sent_messages"
# #     )

# #     business_number = models.ForeignKey(
# #         BusinessNumber, on_delete=models.SET_NULL, blank=True, null=True, related_name="sent_messages"
# #     )

# #     caption = models.TextField(blank=True, null=True)
# #     media_url = models.TextField(blank=True, null=True)
# #     media_type = models.CharField(max_length=50, blank=True, null=True)
# #     media_name = models.CharField(max_length=255, blank=True, null=True)

# #     cta = models.JSONField(blank=True, null=True, default=list)

# #     status = models.CharField(max_length=32, choices=SentMessageStatus.choices)

# #     error_code = models.CharField(max_length=64, blank=True, null=True)
# #     error_message = models.TextField(blank=True, null=True)

# #     attempt_count = models.IntegerField(default=0)

# #     queued_at = models.DateTimeField(auto_now_add=True)
# #     sent_at = models.DateTimeField(blank=True, null=True)
# #     delivered_at = models.DateTimeField(blank=True, null=True)
# #     read_at = models.DateTimeField(blank=True, null=True)
# #     last_error_at = models.DateTimeField(blank=True, null=True)

# #     metadata = models.JSONField(default=dict)

# #     updated_at = models.DateTimeField(auto_now=True)

# #     class Meta:
# #         indexes = [
# #             models.Index(fields=["to_phone"]),
# #             models.Index(fields=["status"]),
# #         ]
# #         ordering = ("queued_at",)

# #     def __str__(self):
# #         return f"SentMessage #{self.id} ({self.status}) ΓåÆ {self.to_phone}"


# # class WhatsAppAccount(models.Model):
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# #     user_identifier = models.CharField(max_length=255, blank=True, null=True)
# #     waba_id = models.CharField(max_length=255, blank=True, null=True)
# #     phone_number_id = models.CharField(max_length=255)
# #     phone_number = models.CharField(max_length=32, blank=True, null=True)
# #     access_token = models.TextField(blank=True, null=True)
# #     status = models.CharField(max_length=32, default="active")
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     def __str__(self):
# #         return f"{self.phone_number or self.phone_number_id}"

# # class WhatsAppAccount(models.Model):
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# #     user = models.ForeignKey(
# #         settings.AUTH_USER_MODEL, 
# #         on_delete=models.SET_NULL, 
# #         null=True, blank=True, 
# #         related_name="whatsapp_accounts"
# #     )
# #     phone_number_id = models.CharField(max_length=50, unique=True)
# #     phone_number = models.CharField(max_length=32, blank=True, null=True)
# #     access_token = models.TextField()
# #     status = models.CharField(max_length=32, default="active")
# #     created_at = models.DateTimeField(auto_now_add=True)
    
# #     updated_at = models.DateTimeField(auto_now=True)

# #     def __str__(self):
# #         return self.phone_number or self.phone_number_id




# class Contact(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='contacts'
#     )
#     name = models.CharField(max_length=255)
#     phone = models.CharField(max_length=20)
#     aadhar = models.CharField(max_length=20, null=True, blank=True)
#     father_name = models.CharField(max_length=255, null=True, blank=True)
#     gender = models.CharField(max_length=20, null=True, blank=True)
#     email_id = models.EmailField(max_length=255, null=True, blank=True)
#     city = models.CharField(max_length=100, null=True, blank=True)
#     state = models.CharField(max_length=100, null=True, blank=True)
#     nationality = models.CharField(max_length=50, null=True, blank=True)
#     dob = models.DateField(null=True, blank=True)
#     other_mobile = models.CharField(max_length=20, null=True, blank=True)
#     permanent = models.TextField(null=True, blank=True)
#     pincode = models.CharField(max_length=10, null=True, blank=True)
#     source_file = models.CharField(max_length=255, null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name}  {self.phone}"




# # class Message(models.Model):
# #     DIRECTION_CHOICES = (("incoming", "incoming"), ("outgoing", "outgoing"))
# #     STATUS_CHOICES = (("sent", "sent"), ("delivered", "delivered"), ("read", "read"), ("failed", "failed"))

# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# #     whatsapp_account = models.ForeignKey(WhatsAppAccount, on_delete=models.CASCADE, related_name="messages")
# #     contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="messages")
# #     direction = models.CharField(max_length=16, choices=DIRECTION_CHOICES)
# #     message_type = models.CharField(max_length=32, default="text")
# #     body = models.JSONField(blank=True, null=True)
# #     text = models.TextField(blank=True, null=True)
# #     status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="sent")
# #     wa_message_id = models.CharField(max_length=255, blank=True, null=True)
# #     created_at = models.DateTimeField(auto_now_add=True)

# #     class Meta:
# #         ordering = ("created_at",)

# #     def __str__(self):
# #         return f"{self.direction} {self.contact} @ {self.created_at}"


# # class Report(models.Model):
# #     campaign = models.ForeignKey(
# #         Campaign, related_name="reports", on_delete=models.CASCADE, null=True, blank=True
# #     )

# #     total = models.IntegerField(default=0)
# #     delivered = models.IntegerField(default=0)
# #     failed = models.IntegerField(default=0)
# #     read_count = models.IntegerField(default=0)  # normalized name

# #     created_at = models.DateTimeField(auto_now_add=True)
# #     last_updated = models.DateTimeField(auto_now=True)

# #     class Meta:
# #         ordering = ("created_at",)

# #     def __str__(self):
# #         return f"Report #{self.id} for Campaign {self.campaign_id}"



# import uuid
# from django.db import models


# class WhatsAppCloudNumber(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     phone_number_id = models.CharField(max_length=50, unique=True)
#     phone_number = models.CharField(max_length=32, null=True, blank=True)
#     waba_id = models.CharField(max_length=50, null=True, blank=True)
#     access_token = models.TextField()
    
#     status = models.CharField(max_length=20, default="active")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.phone_number or self.phone_number_id

# class MessageLog(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     cloud_number = models.ForeignKey(WhatsAppCloudNumber, on_delete=models.CASCADE)
#     receiver = models.CharField(max_length=20)
#     template_name = models.CharField(max_length=150)

#     message_id = models.CharField(max_length=150, blank=True, null=True)
#     status_code = models.IntegerField(null=True, blank=True)
#     response_data = models.JSONField(null=True, blank=True)

#     sent_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.receiver}  {self.template_name}"