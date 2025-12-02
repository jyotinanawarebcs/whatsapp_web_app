from django.urls import path
from . import views

urlpatterns = [
    # Campaign CRUD endpoints
    path('campaigns/create/', views.create_campaign, name='create-campaign'),
    path('campaigns/run/', views.run_campaign, name='run-campaign'),
    path('campaigns/', views.get_all_campaigns, name='get-all-campaigns'),
    path('campaigns/active-campaigns/', views.get_active_campaigns, name='active-campaigns'),
    path('campaigns/stats/', views.get_dashboard_stats, name='dashboard-stats'),
    path('campaigns/recent/', views.get_recent_campaigns, name='recent-campaigns'),
    
    # Campaign by ID endpoints
    path('campaigns/<int:id>/', views.get_campaign, name='get-campaign'),
    path('campaigns/<int:id>/status/', views.update_campaign_status, name='update-campaign-status'),
    path('campaigns/<int:id>/', views.update_campaign, name='update-campaign'),
    path('campaigns/<int:id>/', views.delete_campaign, name='delete-campaign'),
]