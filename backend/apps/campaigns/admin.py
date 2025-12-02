from django.contrib import admin
from .models import MessageTemplate, Campaign, CampaignContact

@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'language', 'approval_status', 'created_at']
    list_filter = ['approval_status', 'category', 'created_at']
    search_fields = ['name', 'body']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['campaign_name', 'status', 'recipients_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['campaign_name', 'name']

@admin.register(CampaignContact)
class CampaignContactAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'contact', 'sequence', 'job_id', 'created_at']
    list_filter = ['campaign', 'created_at']
    search_fields = ['contact__name', 'contact__phone']