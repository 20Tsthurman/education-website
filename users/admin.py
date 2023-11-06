from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserAdminForm
from .models import Discussion, Reply

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
        
@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'teacher')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'user', 'created_at')
    search_fields = ('content',)
    list_filter = ('created_at', 'user')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

admin.site.register(CustomUser, CustomUserAdmin)
