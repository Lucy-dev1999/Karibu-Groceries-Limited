from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Stock, Sale, Credit, UserProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'branch', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'contact', 'gender')}),
        ('Role and Branch', {'fields': ('role', 'branch')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'branch'),
        }),
    )

admin.site.register(UserProfile, CustomUserAdmin)
admin.site.register(Stock)
admin.site.register(Sale)
admin.site.register(Credit)
