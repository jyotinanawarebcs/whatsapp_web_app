# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from accounts.models import CustomUser


# class CustomUserAdmin(UserAdmin):
#     model = CustomUser

#     list_display = (
#         'username', 'email', 'first_name', 'last_name',
#         'service', 'account_type', 'credit', 'validity', 'is_staff'
#     )

#     fieldsets = UserAdmin.fieldsets + (
#         ('WhatsApp Account Details', {
#             'fields': ('service', 'account_type', 'credit', 'validity')
#         }),
#     )

#     add_fieldsets = UserAdmin.add_fieldsets + (
#         ('WhatsApp Account Details', {
#             'fields': ('service', 'account_type', 'credit', 'validity')
#         }),
#     )

# admin.site.register(CustomUser, CustomUserAdmin)
