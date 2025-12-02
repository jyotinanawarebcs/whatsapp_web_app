from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSet
router = DefaultRouter()
router.register(r'automations', views.AutomationViewSet, basename='automation')
router.register(r'logs', views.AutomationLogViewSet, basename='automation-log')

urlpatterns = [
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('stats/', views.AutomationViewSet.as_view({'get': 'stats'}), name='automation-stats'),
]