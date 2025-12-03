from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import ContactFileListView
# from .views import ApprovedTemplateListView
# ,ForgotPasswordAPIView, VerifyCodeAPIView, ResetPasswordAPIView

from .views import (
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
    send_whatsapp_template,
#     AddRecipientsView,
#     CampaignRecipientsListView,
)

router = DefaultRouter()

# router.register("users", UserViewSet)
# router.register("contacts", ContactViewSet)
# router.register("campaigns", CampaignViewSet)
# router.register("business-numbers", BusinessNumberViewSet)
# router.register("virtual-numbers", VirtualNumberViewSet)
# router.register("templates", MessageTemplateViewSet)
# router.register("webhook-logs", WebhookLogViewSet)
# router.register("campaign-jobs", CampaignJobViewSet)
# router.register("sent-messages", SentMessageViewSet)
# router.register("wa-accounts", WhatsAppAccountViewSet)
# router.register("messages", MessageViewSet)
# router.register("reports", ReportViewSet)


urlpatterns = [
    # ⭐ Custom route
    path("send-template/", send_whatsapp_template, name="send_template"),  
    # # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path("campaigns/<int:campaign_id>/recipients/", AddRecipientsView.as_view()),
    # path("campaigns/<int:campaign_id>/recipients/list/", CampaignRecipientsListView.as_view()),
    # path("files", ContactFileListView.as_view()),
    # path("approved", ApprovedTemplateListView.as_view()),
    # path("contacts/", include("contacts.urls")),
    # path("templates/", include("templates.urls")),

    # path('api/forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    # path('api/verify-code/', VerifyCodeAPIView.as_view(), name='verify_code'),
    # path('api/reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('', include(router.urls)),
]
