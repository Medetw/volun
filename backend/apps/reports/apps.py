from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reports'
    verbose_name = 'Отчеты'

    def ready(self):
        """Импорт сигналов при готовности приложения."""
        try:
            import apps.reports.signals
        except ImportError:
            pass
