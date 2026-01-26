from django.contrib import admin
from apps.notifications.models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'recipient', 'sender', 'notification_type',
        'status', 'is_email_sent', 'created_at'
    ]
    list_filter = [
        'notification_type', 'status', 'is_email_sent',
        'created_at', 'recipient__role'
    ]
    search_fields = [
        'title', 'message', 'recipient__username',
        'recipient__email', 'sender__username'
    ]
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основное', {
            'fields': ('recipient', 'sender', 'notification_type')
        }),
        ('Содержание', {
            'fields': ('title', 'message')
        }),
        ('Связанные объекты', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('status', 'is_email_sent')
        }),
        ('Даты', {
            'fields': ('created_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'admin':
            return qs
        return qs.filter(recipient=request.user)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_application_approved', 'email_application_rejected',
        'email_new_projects', 'inapp_application_approved'
    ]
    list_filter = [
        'email_application_approved', 'email_application_rejected',
        'email_new_projects', 'email_project_updates',
        'inapp_application_approved', 'inapp_application_rejected',
        'inapp_new_projects', 'inapp_project_updates'
    ]
    search_fields = ['user__username', 'user__email']
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Email уведомления', {
            'fields': (
                'email_application_approved', 'email_application_rejected',
                'email_new_projects', 'email_project_updates'
            )
        }),
        ('In-app уведомления', {
            'fields': (
                'inapp_application_approved', 'inapp_application_rejected',
                'inapp_new_projects', 'inapp_project_updates'
            )
        }),
    )
