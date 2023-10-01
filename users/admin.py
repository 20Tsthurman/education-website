from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_active', 'is_staff', 'user_type')
    ordering = ['email']  # You can use other fields from your model here

admin.site.register(CustomUser, CustomUserAdmin)
