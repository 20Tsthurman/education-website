from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserAdminForm

class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    add_form = CustomUserAdminForm
    list_display = ('email', 'user_type', 'is_staff', 'is_active',)
    list_filter = ('user_type', 'is_staff', 'is_active',)
    search_fields = ('email',)
    ordering = ('email',)

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (None, {'fields': ('email', 'password')}),
                ('Permissions', {
                    'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
                }),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
            )
        else:
            return (
                (None, {
                    'classes': ('wide',),
                    'fields': ('email', 'user_type', 'password1', 'password2'),
                }),
            )

admin.site.register(CustomUser, CustomUserAdmin)
