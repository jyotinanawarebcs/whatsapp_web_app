from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone',  'is_active', 'created_at')
    search_fields = ('name', 'phone', 'email_id', 'city', 'state')
    list_filter = ('is_active', 'city', 'state')


   # Method to display the username from the related User
    def get_user(self, obj):
        return obj.user.username  # or obj.user.email
    get_user.short_description = 'User'