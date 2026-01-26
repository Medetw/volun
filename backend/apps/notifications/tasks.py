from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.notifications.models import Notification


@shared_task
def send_notification_email(notification_id):
    """Отправка email уведомления."""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Проверяем настройки пользователя
        try:
            preferences = notification.recipient.notification_preferences
            
            # Определяем нужно ли отправлять email
            should_send = False
            if notification.notification_type == 'application_approved':
                should_send = preferences.email_application_approved
            elif notification.notification_type == 'application_rejected':
                should_send = preferences.email_application_rejected
            elif notification.notification_type == 'new_project':
                should_send = preferences.email_new_projects
            elif notification.notification_type == 'project_update':
                should_send = preferences.email_project_updates
            else:
                should_send = True  # Системные уведомления всегда отправляем
                
            if not should_send:
                return f"Email не отправлен: пользователь {notification.recipient.username} отписан от этого типа уведомлений"
                
        except Exception:
            # Если настроек нет, отправляем по умолчанию
            pass
        
        # Формируем HTML и текст версии письма
        html_message = render_to_string('notifications/email_template.html', {
            'notification': notification,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        })
        
        plain_message = strip_tags(html_message)
        
        # Отправляем письмо
        send_mail(
            subject=notification.title,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@volunteer-platform.com'),
            recipient_list=[notification.recipient.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Отмечаем что email отправлен
        notification.is_email_sent = True
        notification.save(update_fields=['is_email_sent'])
        
        return f"Email успешно отправлен пользователю {notification.recipient.email}"
        
    except Notification.DoesNotExist:
        return f"Ошибка: уведомление с id {notification_id} не найдено"
    except Exception as e:
        return f"Ошибка при отправке email: {str(e)}"


@shared_task
def send_bulk_notifications(notification_ids):
    """Массовая отправка уведомлений."""
    success_count = 0
    error_count = 0
    
    for notification_id in notification_ids:
        try:
            result = send_notification_email(notification_id)
            if "успешно" in result.lower():
                success_count += 1
            else:
                error_count += 1
        except Exception:
            error_count += 1
    
    return f"Массовая отправка завершена: {success_count} успешно, {error_count} с ошибками"


@shared_task
def cleanup_old_notifications():
    """Очистка старых архивированных уведомлений."""
    from django.utils import timezone
    from datetime import timedelta
    
    # Удаляем архивированные уведомления старше 30 дней
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = Notification.objects.filter(
        status='archived',
        created_at__lt=cutoff_date
    ).delete()[0]
    
    return f"Удалено {deleted_count} старых уведомлений"


@shared_task
def update_notification_stats():
    """Обновление кэшированной статистики уведомлений."""
    from django.core.cache import cache
    from django.contrib.auth import get_user_model
    from django.db.models import Count
    
    User = get_user_model()
    
    # Обновляем статистику для каждого пользователя
    for user in User.objects.filter(is_active=True):
        cache_key = f'notification_stats_{user.id}'
        
        stats = {
            'total': Notification.objects.filter(recipient=user).count(),
            'unread': Notification.objects.filter(recipient=user, status='unread').count(),
            'read': Notification.objects.filter(recipient=user, status='read').count(),
            'recent': Notification.objects.filter(
                recipient=user,
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }
        
        # Сохраняем в кэш на 5 минут
        cache.set(cache_key, stats, 300)
    
    return f"Статистика обновлена для {User.objects.filter(is_active=True).count()} пользователей"
