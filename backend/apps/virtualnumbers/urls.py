from django.urls import path
from . import views, views_webhooks

# Admin endpoints (require authentication)
urlpatterns = [
    # Business Number Management
    path('admin/business-number/', views.get_business_number, name='get-business-number'),
    path('admin/business-number/', views.update_business_number, name='update-business-number'),
    
    # Virtual Number Management
    path('admin/virtual-numbers/', views.list_virtual_numbers, name='list-virtual-numbers'),
    path('admin/virtual-numbers/', views.create_virtual_number, name='create-virtual-number'),
    path('admin/virtual-numbers/<int:id>/', views.update_virtual_number, name='update-virtual-number'),
    path('admin/virtual-numbers/switch/', views.manual_switch, name='manual-switch'),
]

# Webhook endpoints (public, no authentication required)
webhook_patterns = [
    path('webhooks/meta/', views_webhooks.handle_meta_webhook, name='meta-webhook'),
]

# Combine all URLs
urlpatterns += webhook_patterns