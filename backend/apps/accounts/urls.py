from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

# from .views import (
    # UserViewSet,
    # ContactViewSet,
    # CampaignViewSet,
    # BusinessNumberViewSet,
    # VirtualNumberViewSet,
    # MessageTemplateViewSet,
    # WebhookLogViewSet,
    # CampaignJobViewSet,
    # SentMessageViewSet,
    # WhatsAppAccountViewSet,
    # MessageViewSet,
    # ReportViewSet,
    # send_whatsapp_template,
# )


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')


urlpatterns = [
    # ⭐ Custom route

    # path("contacts/", include("contacts.urls")),
    # path("templates/", include("templates.urls")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('api/forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    # path('api/verify-code/', VerifyCodeAPIView.as_view(), name='verify_code'),
    # path('api/reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('', include(router.urls)),
]