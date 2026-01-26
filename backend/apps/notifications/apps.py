from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Уведомления'

    def ready(self):
        """Импорт сигналов при готовности приложения."""
        try:
            import apps.notifications.signals
        except ImportError:
            pass
