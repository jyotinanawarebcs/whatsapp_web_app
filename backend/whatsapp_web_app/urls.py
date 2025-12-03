from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Comment out other apps temporarily while fixing
    path('api/', include('contacts.urls')),
    path('api/', include('campaigns.urls')), 
    path('api/', include('virtualnumbers.urls')), 
    path('api/', include('dispatch.urls')), 
    path('api/', include('automations.urls')),  # Only automations for now
    path('api/', include('chat.urls')),
    path('api/', include('accounts.urls')),
]
