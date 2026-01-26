from rest_framework import serializers
from apps.notifications.models import Notification, NotificationPreference, NotificationType


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для уведомлений."""
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', 
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )
    time_ago = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_name',
            'notification_type', 'notification_type_display',
            'title', 'message', 'status', 'status_display',
            'content_type', 'object_id', 'is_email_sent',
            'created_at', 'read_at', 'time_ago', 'is_unread'
        ]
        read_only_fields = [
            'id', 'created_at', 'read_at', 'is_email_sent'
        ]

    def get_time_ago(self, obj):
        """Возвращает время создания в формате '2 часа назад'."""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "только что"
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f"{minutes} {'минуту' if minutes == 1 else 'минуты' if 2 <= minutes <= 4 else 'минут'} назад"
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f"{hours} {'час' if hours == 1 else 'часа' if 2 <= hours <= 4 else 'часов'} назад"
        elif diff < timedelta(days=30):
            days = diff.days
            return f"{days} {'день' if days == 1 else 'дня' if 2 <= days <= 4 else 'дней'} назад"
        else:
            return obj.created_at.strftime("%d %b %Y")


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания уведомлений."""
    class Meta:
        model = Notification
        fields = [
            'recipient', 'sender', 'notification_type',
            'title', 'message', 'content_type', 'object_id'
        ]

    def validate_recipient(self, value):
        """Проверяем, что получатель существует."""
        if not value.is_active:
            raise serializers.ValidationError("Получатель неактивен.")
        return value


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек уведомлений."""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = NotificationPreference
        fields = [
            'user', 'user_email',
            'email_application_approved', 'email_application_rejected',
            'email_new_projects', 'email_project_updates',
            'inapp_application_approved', 'inapp_application_rejected',
            'inapp_new_projects', 'inapp_project_updates'
        ]
        read_only_fields = ['user']


class NotificationStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики уведомлений."""
    total = serializers.IntegerField(read_only=True)
    unread = serializers.IntegerField(read_only=True)
    read = serializers.IntegerField(read_only=True)
    recent = serializers.IntegerField(read_only=True)
