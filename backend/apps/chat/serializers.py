from rest_framework import serializers
from django.contrib.auth import get_user_model
# from .models import (
    # Campaign,
    # BusinessNumber,
    # VirtualNumber,
    # MessageTemplate,
    # WebhookLog,
    # CampaignJob,
    # SentMessage,
    # WhatsAppAccount,
    # Contact,
    # Message,
    # Report,
# )

# User = get_user_model()

# # =====================================================
# # USER SERIALIZER
# # =====================================================

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = [
#             "id",
#             "username",
#             "email",
#             "first_name",
#             "last_name",
#             "service",
#             "account_type",
#             "credit",
#             "validity",
#         ]


# # =====================================================
# # CONTACT SERIALIZERS
# # =====================================================

# class ContactSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Contact
#         fields = "__all__"


# # =====================================================
# # BUSINESS NUMBER SERIALIZER
# # =====================================================

# class BusinessNumberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BusinessNumber
#         fields = "__all__"


# # =====================================================
# # VIRTUAL NUMBER SERIALIZER
# # =====================================================

# class VirtualNumberSerializer(serializers.ModelSerializer):
#     business_number = BusinessNumberSerializer(read_only=True)

#     class Meta:
#         model = VirtualNumber
#         fields = "__all__"


# # =====================================================
# # MESSAGE TEMPLATE SERIALIZER
# # =====================================================

# class MessageTemplateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MessageTemplate
#         fields = "__all__"


# # =====================================================
# # CAMPAIGN SERIALIZER
# # =====================================================

# class CampaignSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)

#     class Meta:
#         model = Campaign
#         fields = "__all__"


# class CampaignCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Campaign
#         fields = "__all__"


# # =====================================================
# # CAMPAIGN JOB SERIALIZER
# # =====================================================

# class CampaignJobSerializer(serializers.ModelSerializer):
#     campaign = CampaignSerializer(read_only=True)

#     class Meta:
#         model = CampaignJob
#         fields = "__all__"


# # =====================================================
# # SENT MESSAGE SERIALIZER
# # =====================================================

# class SentMessageSerializer(serializers.ModelSerializer):
#     contact = ContactSerializer(read_only=True)

#     class Meta:
#         model = SentMessage
#         fields = "__all__"


# # =====================================================
# # WHATSAPP ACCOUNT SERIALIZER
# # =====================================================

# class WhatsAppAccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WhatsAppAccount
#         fields = "__all__"


# # =====================================================
# # MESSAGE SERIALIZER (INBOX / CHAT)
# # =====================================================

# class MessageSerializer(serializers.ModelSerializer):
#     contact = ContactSerializer(read_only=True)
#     whatsapp_account = WhatsAppAccountSerializer(read_only=True)

#     class Meta:
#         model = Message
#         fields = "__all__"


# # =====================================================
# # WEBHOOK LOG SERIALIZER
# # =====================================================

# class WebhookLogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WebhookLog
#         fields = "__all__"


# # =====================================================
# # REPORT SERIALIZER
# # =====================================================

# class ReportSerializer(serializers.ModelSerializer):
#     campaign = CampaignSerializer(read_only=True)

#     class Meta:
#         model = Report
#         fields = "__all__"

from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class SendTemplateSerializer(serializers.Serializer):
    cloud_number_id = serializers.IntegerField(required=True)
    to = serializers.CharField(required=True)
    template = serializers.CharField(required=True)

# app/serializers.py
from rest_framework import serializers
# from .models import Campaign, CampaignRecipient

# class CampaignSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Campaign
#         fields = "__all__"
#         read_only_fields = ("id", "created_at", "updated_at", "user")


# class CampaignRecipientSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CampaignRecipient
#         fields = "__all__"
#         read_only_fields = ("id", "sent_at", "delivered_at", "read_at")

# from rest_framework import serializers
# from .models import Contact

# class ContactSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Contact
#         fields = "__all__"   # includes all fields
#         read_only_fields = ("id", "created_at")
