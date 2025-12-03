
# # Webhook receiver (Meta calls this)
# @method_decorator(csrf_exempt, name="dispatch")
# class WebhookAPIView(APIView):
#     authentication_classes = []   # webhook doesn't need DRF auth
#     permission_classes = []

#     def get(self, request):
#         # verification challenge
#         verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_verify_token")
#         mode = request.GET.get("hub.mode")
#         token = request.GET.get("hub.verify_token")
#         challenge = request.GET.get("hub.challenge")
#         if mode and token:
#             if token == verify_token:
#                 return Response(int(challenge), status=200)
#             else:
#                 return Response("verification failed", status=403)
#         return Response("ok", status=200)

#     def post(self, request):
#         payload = request.data
#         # Basic flow: parse and store incoming messages or status updates.
#         try:
#             entry = payload.get("entry", [])
#             for e in entry:
#                 changes = e.get("changes", [])
#                 for c in changes:
#                     value = c.get("value", {})
#                     # messages
#                     messages = value.get("messages", [])
#                     for m in messages:
#                         from_phone = m.get("from")
#                         text_body = m.get("text", {}).get("body")
#                         phone_number_id = value.get("metadata", {}).get("phone_number_id")
#                         # link to account
#                         account = None
#                         try:
#                             account = WhatsAppAccount.objects.get(phone_number_id=phone_number_id)
#                         except WhatsAppAccount.DoesNotExist:
#                             account = WhatsAppAccount.objects.first()  # fallback

#                         contact, _ = Contact.objects.get_or_create(phone=from_phone)
#                         Message.objects.create(
#                             whatsapp_account=account,
#                             contact=contact,
#                             direction="incoming",
#                             message_type=m.get("type","text"),
#                             body=m,
#                             text=text_body,
#                             wa_message_id=m.get("id")
#                         )
#                     # statuses (optional)
#                     statuses = value.get("statuses", [])
#                     for s in statuses:
#                         msg_id = s.get("id")
#                         status_text = s.get("status")
#                         try:
#                             msg = Message.objects.filter(wa_message_id=msg_id).first()
#                             if msg:
#                                 msg.status = status_text
#                                 msg.save()
#                         except:
#                             pass
#             return Response({"ok": True})
#         except Exception as exc:
#             return Response({"error": str(exc)}, status=500)

# # Contacts list
# class ContactListAPIView(generics.ListAPIView):
#     queryset = Contact.objects.all().order_by("-added_at")
#     serializer_class = ContactSerializer

# # Messages list (filter by contact id or phone)
# class MessagesListAPIView(generics.ListAPIView):
#     serializer_class = MessageSerializer

#     def get_queryset(self):
#         contact_phone = self.request.query_params.get("contact")
#         if contact_phone:
#             return Message.objects.filter(contact__phone=contact_phone).order_by("created_at")
#         return Message.objects.all().order_by("created_at")

# # Test connection to Meta using saved account
# class WAConnectionTest(APIView):
#     def get(self, request):
#         account = WhatsAppAccount.objects.first()
#         if not account:
#             return Response({"ok": False, "error": "no account configured"}, status=400)
#         version = getattr(settings, "WHATSAPP_API_VERSION", "v17.0")
#         url = f"https://graph.facebook.com/{version}/{account.phone_number_id}"
#         headers = {"Authorization": f"Bearer {account.access_token}"}
#         resp = requests.get(url, headers=headers)
#         if resp.status_code == 200:
#             return Response({"ok": True, "data": resp.json()})
#         return Response({"ok": False, "status": resp.status_code, "detail": resp.text}, status=resp.status_code)

# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.decorators import action

# from django.contrib.auth import get_user_model

# from .models import (
#     CustomUser,
#     Campaign,
#     BusinessNumber,
#     VirtualNumber,
#     MessageTemplate,
#     WebhookLog,
#     CampaignJob,
#     SentMessage,
#     WhatsAppAccount,
#     Contact,
#     Message,
#     Report,
# )

# from .serializers import (
#     UserSerializer,
#     CampaignSerializer,
#     CampaignCreateSerializer,
#     BusinessNumberSerializer,
#     VirtualNumberSerializer,
#     MessageTemplateSerializer,
#     WebhookLogSerializer,
#     CampaignJobSerializer,
#     SentMessageSerializer,
#     WhatsAppAccountSerializer,
#     ContactSerializer,
#     MessageSerializer,
#     ReportSerializer,
# )

# User = get_user_model()

# # -------------------------------------------------------------
# # USER VIEWSET
# # -------------------------------------------------------------
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]


# # -------------------------------------------------------------
# # CONTACT VIEWSET
# # -------------------------------------------------------------
# class ContactViewSet(viewsets.ModelViewSet):
#     queryset = Contact.objects.all()
#     serializer_class = ContactSerializer
#     permission_classes = [IsAuthenticated]


# # -------------------------------------------------------------
# # BUSINESS NUMBER VIEWSET
# # -------------------------------------------------------------
# class BusinessNumberViewSet(viewsets.ModelViewSet):
#     queryset = BusinessNumber.objects.all()
#     serializer_class = BusinessNumberSerializer
#     permission_classes = [IsAuthenticated]


# # -------------------------------------------------------------
# # VIRTUAL NUMBER VIEWSET
# # -------------------------------------------------------------
# class VirtualNumberViewSet(viewsets.ModelViewSet):
#     queryset = VirtualNumber.objects.all()
#     serializer_class = VirtualNumberSerializer
#     permission_classes = [IsAuthenticated]


# # -------------------------------------------------------------
# # MESSAGE TEMPLATE VIEWSET
# # -------------------------------------------------------------
# class MessageTemplateViewSet(viewsets.ModelViewSet):
#     queryset = MessageTemplate.objects.all()
#     serializer_class = MessageTemplateSerializer
#     permission_classes = [IsAuthenticated]


# # -------------------------------------------------------------
# # CAMPAIGN VIEWSET
# # -------------------------------------------------------------
# class CampaignViewSet(viewsets.ModelViewSet):
#     queryset = Campaign.objects.all().order_by("-created_at")
#     permission_classes = [IsAuthenticated]

#     def get_serializer_class(self):
#         if self.action in ["create", "update", "partial_update"]:
#             return CampaignCreateSerializer
#         return CampaignSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     @action(detail=True, methods=["post"])
#     def activate(self, request, pk=None):
#         """Activate a campaign."""
#         campaign = self.get_object()
#         campaign.status = "active"
#         campaign.save()
#         return Response({"message": "Campaign activated"}, status=200)

#     @action(detail=True, methods=["post"])
#     def stop(self, request, pk=None):
#         """Stop a running campaign."""
#         campaign = self.get_object()
#         campaign.status = "completed"
#         campaign.save()
#         return Response({"message": "Campaign completed"}, status=200)


# # -------------------------------------------------------------
# # CAMPAIGN JOB VIEWSET
# # -------------------------------------------------------------
# class CampaignJobViewSet(viewsets.ModelViewSet):
#     queryset = CampaignJob.objects.all().order_by("-queued_at")
#     serializer_class = CampaignJobSerializer
#     permission_classes = [IsAuthenticated]


# # -------------------------------------------------------------
# # SENT MESSAGE VIEWSET
# # -------------------------------------------------------------
# class SentMessageViewSet(viewsets.ModelViewSet):
#     queryset = SentMessage.objects.all().order_by("-queued_at")
#     serializer_class = SentMessageSerializer
#     permission_classes = [IsAuthenticated]


# # -------------------------------------------------------------
# # WHATSAPP ACCOUNT VIEWSET
# # -------------------------------------------------------------
# class WhatsAppAccountViewSet(viewsets.ModelViewSet):
#     queryset = WhatsAppAccount.objects.all()
#     serializer_class = WhatsAppAccountSerializer
#     permission_classes = [IsAuthenticated]


# # -------------------------------------------------------------
# # MESSAGE (CHAT/INBOX) VIEWSET
# # -------------------------------------------------------------
# class MessageViewSet(viewsets.ModelViewSet):
#     queryset = Message.objects.all().order_by("-created_at")
#     serializer_class = MessageSerializer
#     permission_classes = [IsAuthenticated]

#     @action(detail=False, methods=["get"])
#     def by_contact(self, request):
#         """Fetch chat history for a phone number."""
#         phone = request.query_params.get("phone")
#         if not phone:
#             return Response({"error": "phone param required"}, status=400)

#         messages = Message.objects.filter(contact__phone=phone).order_by("created_at")
#         serializer = MessageSerializer(messages, many=True)
#         return Response(serializer.data)


# # -------------------------------------------------------------
# # WEBHOOK LOG VIEWSET
# # -------------------------------------------------------------
# class WebhookLogViewSet(viewsets.ModelViewSet):
#     queryset = WebhookLog.objects.all().order_by("-received_at")
#     serializer_class = WebhookLogSerializer
#     permission_classes = [AllowAny]


# # -------------------------------------------------------------
# # REPORT VIEWSET
# # -------------------------------------------------------------
# class ReportViewSet(viewsets.ModelViewSet):
#     queryset = Report.objects.all()
#     serializer_class = ReportSerializer
#     permission_classes = [IsAuthenticated]


# # import requests
# # import json
# # from rest_framework.response import Response
# # from rest_framework.decorators import api_view

# # WHATSAPP_PHONE_NUMBER_ID = "874475419083125"


# # @api_view(["POST"])
# # def send_whatsapp_template(request):
# #     """
# #     Send WhatsApp Cloud API template message
# #     """

# #     access_token = request.data.get("access_token")
# #     to = request.data.get("to")
# #     template_name = request.data.get("template_name", "hello_world")

# #     if not access_token or not to:
# #         return Response({"error": "access_token and to are required"}, status=400)

# #     url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# #     headers = {
# #         "Authorization": f"Bearer {access_token}",
# #         "Content-Type": "application/json"
# #     }

# #     payload = {
# #         "messaging_product": "whatsapp",
# #         "to": to,
# #         "type": "template",
# #         "template": {
# #             "name": template_name,
# #             "language": {"code": "en_US"}
# #         }
# #     }

# #     response = requests.post(url, headers=headers, data=json.dumps(payload))

# #     return Response({
# #         "status_code": response.status_code,
# #         "response": response.json()
# #     })
# import requests
# import json
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import WhatsAppCloudNumber, MessageLog

# @api_view(["POST"])
# def send_whatsapp_template(request):
#     try:
#         cloud_id = request.data.get("cloud_number_id")
#         receiver = request.data.get("to")
#         template_name = request.data.get("template")

#         cloud_number = WhatsAppCloudNumber.objects.get(id=cloud_id)

#         url = f"https://graph.facebook.com/v18.0/{cloud_number.phone_number_id}/messages"

#         headers = {
#             "Authorization": f"Bearer {cloud_number.access_token}",
#             "Content-Type": "application/json",
#         }

#         payload = {
#             "messaging_product": "whatsapp",
#             "to": receiver,
#             "type": "template",
#             "template": {
#                 "name": template_name,
#                 "language": {"code": "en_US"}
#             }
#         }

#         response = requests.post(url, headers=headers, data=json.dumps(payload))
#         data = response.json()

#         # Store logs
#         MessageLog.objects.create(
#             cloud_number=cloud_number,
#             receiver=receiver,
#             template_name=template_name,
#             message_id=data.get("messages", [{}])[0].get("id"),
#             status_code=response.status_code,
#             response_data=data,
#         )

#         return Response({
#             "success": True,
#             "status_code": response.status_code,
#             "response": data
#         })

#     except WhatsAppCloudNumber.DoesNotExist:
#         return Response({"error": "Invalid cloud_number_id"}, status=400)
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import WhatsAppCloudNumber, MessageLog
from .serializers import SendTemplateSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import requests
import time
from rest_framework.decorators import api_view
from rest_framework.response import Response


# -----------------------------------------
# CONFIGURATION (inside view)
# -----------------------------------------
ACCESS_TOKEN = "EAATpPOMPwgsBQOEH6iqw92ch83OtTQFndEvxt1i6nCkbXmwYbZCb5l1ovdVBBBTa23YiTDVblDZCh2wvQaF4LXej5jKAljqLgI6FsZCRXWl8RQ9BMUyXQHzPLS26eRpsjOxM9hPR1bzbMmoEiru6sxs5ZBUQW8DFzLRCSWOCweyJ0oJgGVXCV6bjv02nuZBKQRfFSklRLqhOxlPDScGfxJsjQ78QFKsrTTwuQsKBaNmLuaX9n1aRZCS6jJNOUhEUACY8KkACH1BP8fyf5znIUTxwZDZD"
PHONE_NUMBER_ID = "874475419083125"
DEFAULT_LANGUAGE = "en_US"

# @api_view(["POST"])
# def send_whatsapp_template(request):
#     try:
#         receiver = request.data.get("receiver")
#         template_name = request.data.get("template_name")

#         if not receiver or not template_name:
#             return Response(
#                 {"error": "Both 'receiver' and 'template_name' are required."}, status=400
#             )

#         url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

#         headers = {
#             "Authorization": f"Bearer {ACCESS_TOKEN}",
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "messaging_product": "whatsapp",
#             "to": receiver,
#             "type": "template",
#             "template": {
#                 "name": template_name,
#                 "language": {"code": DEFAULT_LANGUAGE}
#             }
#         }

#         response = requests.post(url, headers=headers, json=payload)
#         data = response.json()

#         return Response({
#             "success": response.status_code == 200,
#             "status_code": response.status_code,
#             "response": data
#         })

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

ACCESS_TOKEN = "EAATpPOMPwgsBQOEdWigvXXb8wkjzqOciCNd5LrwZB33si9q8ps7987trfgSZAa2GzlpOR0aZCfo1950NmGp9bZCAF7bZBR1PZBxjFuq9Xwz3UvvFmGvFUcJRWwksQZAEZAWrkT8RhsxruHQCfpK4XipG9gUSUHnxJIUSkDJzvszquIq3zddmnYXOct5eTH5MdmlRhQMvPBHcm8T0DDBahmPVVQpYYTzMh589sNOL5DZBSHWYfeoLBaDVJLjb1ocBxwB2bX4gC1KT1xlOfFTwP3x752gZDZD"
PHONE_NUMBER_ID = "874475419083125"
DEFAULT_LANGUAGE = "en_US"

@api_view(["POST"])
def send_whatsapp_template(request):
    try:
        receivers = request.data.get("receiver")
        template_name = request.data.get("template_name")
        language = request.data.get("language", DEFAULT_LANGUAGE)

        if not receivers or not template_name:
            return Response(
                {"error": "receiver and template_name are required."},
                status=400
            )

        # Normalize: convert single string → list
        if isinstance(receivers, str):
            receivers = [r.strip() for r in receivers.split(",") if r.strip()]

        url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        results = []

        for number in receivers:
            payload = {
                "messaging_product": "whatsapp",
                "to": number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language}
                }
            }

            r = requests.post(url, headers=headers, json=payload)
            try:
                body = r.json()
            except:
                body = {"raw_response": r.text}

            results.append({
                "to": number,
                "success": r.status_code == 200,
                "status": r.status_code,
                "response": body
            })

            time.sleep(0.15)  # avoid rate limit

        return Response({"results": results})

    except Exception as e:
        return Response({"error": str(e)}, status=500)

