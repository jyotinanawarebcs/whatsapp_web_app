from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
# from .models import PasswordResetCode
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]


    def get_permissions(self):
        """
        Dynamic permissions:
        - First admin can register without auth
        - After that, only admins can register other admins
        - Login open to all
        """
        if self.action == 'register':
            # if CustomUser.objects.count() == 0:
            #     permission_classes = [permissions.AllowAny]  # first admin
            # else:
                permission_classes = [permissions.AllowAny]  
        elif self.action == 'login':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    # ✅ Admin registration only (no users)
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Enforce admin-only registration logic
        user = serializer.save()
        user.is_staff = True   # Force every registered user to be admin
        user.save()

        message = "Admin registered successfully"
        return Response({
            "message": message,
            "user": {
                "id": user.id,
                "username": user.username,
                "is_staff": user.is_staff,
            }
        }, status=status.HTTP_201_CREATED)

    # ✅ Login (open to all)
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)
        if not user.is_active:
            return Response({"error": "User account is disabled"}, status=403)

        refresh = RefreshToken.for_user(user)
        message = "Admin login successful" if user.is_staff else "User login successful"

        return Response({
            "message": message,
            "user": {
                "id": user.id,
                "username": user.username,
                "is_staff": user.is_staff,
            },
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        }, status=status.HTTP_200_OK)
    
#     # app/views.py
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Campaign
# from .serializers import CampaignSerializer

# @api_view(["GET"])
# def get_campaigns(request):
#     campaigns = Campaign.objects.all().order_by("-created_at")
#     serializer = CampaignSerializer(campaigns, many=True)
#     return Response(serializer.data)


# @api_view(["POST"])
# def create_campaign(request):
#     serializer = CampaignSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save(user=request.user)   # attach logged in user
#         return Response(serializer.data, status=201)
#     return Response(serializer.errors, status=400)

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

# from .models import Campaign, CampaignRecipient
# from .serializers import CampaignSerializer, CampaignRecipientSerializer

# class CampaignCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = CampaignSerializer(data=request.data)
#         if serializer.is_valid():
#             campaign = serializer.save(user=request.user)
#             return Response(CampaignSerializer(campaign).data, status=201)
#         return Response(serializer.errors, status=400)


# class AddRecipientsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, campaign_id):
#         try:
#             campaign = Campaign.objects.get(id=campaign_id, user=request.user)
#         except Campaign.DoesNotExist:
#             return Response({"error": "Campaign not found"}, status=404)

#         recipients = request.data.get("recipients", [])

#         created = []
#         for r in recipients:
#             obj = CampaignRecipient.objects.create(
#                 campaign=campaign,
#                 phone_number=r.get("phone_number"),
#                 name=r.get("name"),
#             )
#             created.append(obj)

#         campaign.recipients_count = CampaignRecipient.objects.filter(
#             campaign=campaign
#         ).count()
#         campaign.save()

#         return Response(
#             CampaignRecipientSerializer(created, many=True).data,
#             status=201
#         )

# class CampaignRecipientsListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, campaign_id):
#         recipients = CampaignRecipient.objects.filter(
#             campaign_id=campaign_id,
#             campaign__user=request.user
#         )
#         return Response(
#             CampaignRecipientSerializer(recipients, many=True).data
#         )

# from rest_framework.generics import ListAPIView
# from .models import Contact
# from .serializers import ContactSerializer

# class ContactFileListView(ListAPIView):
#     queryset = Contact.objects.all()
#     serializer_class = ContactSerializer

# from rest_framework.generics import ListAPIView
# from .models import MessageTemplate
# from .serializers import MessageTemplateSerializer

# class ApprovedTemplateListView(ListAPIView):
#     serializer_class = MessageTemplateSerializer
    
#     def get_queryset(self):
#         return MessageTemplate.objects.filter(status="approved")
