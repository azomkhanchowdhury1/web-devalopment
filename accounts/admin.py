from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, LoginHistory, Notification


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('user_type', 'phone', 'address', 'profile_picture', 'date_of_birth', 'gender', 'bio')
        }),
    )
    
    inlines = [UserProfileInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'designation', 'department', 'created_at']
    search_fields = ['user__username', 'user__email', 'designation', 'department']
    list_filter = ['department', 'created_at']


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'ip_address', 'location']
    list_filter = ['login_time', 'user__user_type']
    search_fields = ['user__username', 'ip_address', 'location']
    readonly_fields = ['user', 'login_time', 'ip_address', 'user_agent']
    
    def has_add_permission(self, request):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_read.short_description = "Mark selected notifications as read"
    
    actions = [mark_read]


admin.site.register(User, CustomUserAdmin)
