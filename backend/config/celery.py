import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('volunteering-platform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic Tasks
app.conf.beat_schedule = {
    # Очистка старых уведомлений каждый день в 3:00
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=3, minute=0),
    },
    # Обновление статистики каждые 10 минут
    'update-notification-stats': {
        'task': 'apps.notifications.tasks.update_notification_stats',
        'schedule': crontab(minute='*/10'),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
