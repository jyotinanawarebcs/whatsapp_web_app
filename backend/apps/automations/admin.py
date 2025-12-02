from django.contrib import admin
from .models import Automation, AutomationLog

@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'automation_type', 'status', 'messages_sent', 'last_run', 'next_run', 'created_at')
    list_filter = ('status', 'automation_type', 'schedule_type')
    search_fields = ('name', 'campaign_name', 'message_template')
    readonly_fields = ('messages_sent', 'last_run', 'next_run', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'campaign_name', 'automation_type', 'status')
        }),
        ('Schedule Configuration', {
            'fields': ('schedule_type', 'cron_expression', 'specific_time', 'specific_date', 'start_date', 'end_date')
        }),
        ('Message Content', {
            'fields': ('message_template', 'cta_buttons')
        }),
        ('Target Configuration', {
            'fields': ('target_contacts', 'target_groups', 'send_to_all')
        }),
        ('Statistics', {
            'fields': ('messages_sent', 'last_run', 'next_run')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AutomationLog)
class AutomationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'automation', 'run_time', 'status', 'messages_sent', 'total_contacts')
    list_filter = ('status', 'run_time')
    search_fields = ('automation__name', 'error_log')
    readonly_fields = ('run_time',)
    fieldsets = (
        ('Log Information', {
            'fields': ('automation', 'run_time', 'status')
        }),
        ('Execution Details', {
            'fields': ('messages_sent', 'total_contacts', 'error_log')
        }),
    )