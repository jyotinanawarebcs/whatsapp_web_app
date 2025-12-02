from django.contrib import admin
from .models import BusinessNumber, VirtualNumber

# ==================================================
# VIRTUAL NUMBER ADMIN CONFIGURATION
# ==================================================
@admin.register(VirtualNumber)
class VirtualNumberAdmin(admin.ModelAdmin):
    """
    Admin configuration for VirtualNumber model
    This controls how virtual numbers appear in Django Admin
    """
    
    # List display - Table columns
    list_display = [
        'id', 
        'phone_number_id', 
        'status', 
        'quality_rating', 
        'is_primary',
        'message_count_24h',
        'last_used_at',
        'business_number'
    ]
    
    # Filters for sidebar
    list_filter = [
        'status',
        'quality_rating',
        'is_primary',
        'created_at'
    ]
    
    # Search fields
    search_fields = [
        'phone_number_id',
        'waba_id',
        'business_number__business_name'
    ]
    
    # Fields to display in edit form
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'business_number',
                'waba_id',
                'phone_number_id',
                'access_token'
            )
        }),
        ('Status & Quality', {
            'fields': (
                'status',
                'quality_rating',
                'is_primary'
            )
        }),
        ('Usage Statistics', {
            'fields': (
                'message_count_24h',
                'last_used_at'
            )
        }),
    )
    
    # Readonly fields
    readonly_fields = ['created_at', 'updated_at']
    
    # Actions for bulk operations
    actions = ['mark_as_active', 'mark_as_primary', 'reset_message_count']
    
    def mark_as_active(self, request, queryset):
        """Bulk action to mark selected numbers as active"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} virtual numbers marked as active.')
    mark_as_active.short_description = "Mark selected numbers as ACTIVE"
    
    def mark_as_primary(self, request, queryset):
        """Bulk action to mark selected numbers as primary"""
        # First, unset primary from all numbers
        VirtualNumber.objects.filter(is_primary=True).update(is_primary=False)
        # Then set selected as primary
        updated = queryset.update(is_primary=True)
        self.message_user(request, f'{updated} virtual numbers marked as primary.')
    mark_as_primary.short_description = "Mark selected numbers as PRIMARY"
    
    def reset_message_count(self, request, queryset):
        """Bulk action to reset message count"""
        updated = queryset.update(message_count_24h=0)
        self.message_user(request, f'{updated} virtual numbers message count reset.')
    reset_message_count.short_description = "Reset message count to zero"

# ==================================================
# BUSINESS NUMBER ADMIN CONFIGURATION
# ==================================================
@admin.register(BusinessNumber)
class BusinessNumberAdmin(admin.ModelAdmin):
    """
    Admin configuration for BusinessNumber model
    """
    
    list_display = [
        'id',
        'business_name',
        'display_phone_number',
        'waba_id',
        'auto_switch_enabled',
        'created_at'
    ]
    
    list_filter = [
        'auto_switch_enabled',
        'created_at'
    ]
    
    search_fields = [
        'business_name',
        'display_phone_number',
        'waba_id'
    ]
    
    fieldsets = (
        ('Business Information', {
            'fields': (
                'business_name',
                'display_phone_number'
            )
        }),
        ('WhatsApp Business API', {
            'fields': (
                'waba_id',
                'phone_number_id',
                'access_token'
            )
        }),
        ('Settings', {
            'fields': (
                'auto_switch_enabled',
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']