from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.applications.models import Application, ApplicationStatus
from apps.projects.models import Project
from apps.notifications.models import Notification, NotificationType
from apps.notifications.tasks import send_notification_email


@receiver(post_save, sender=Application)
def application_status_changed(sender, instance, created, **kwargs):
    """Отправка уведомлений при изменении статуса заявки."""
    
    # Пропускаем создание новой заявки
    if created:
        return
    
    # Отправляем уведомление волонтеру об изменении статуса
    if instance.status in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]:
        notification_type = (
            NotificationType.APPLICATION_APPROVED 
            if instance.status == ApplicationStatus.APPROVED 
            else NotificationType.APPLICATION_REJECTED
        )
        
        title = (
            f"Ваша заявка на проект '{instance.project.title}' одобрена!"
            if instance.status == ApplicationStatus.APPROVED
            else f"Ваша заявка на проект '{instance.project.title}' отклонена"
        )
        
        message = (
            f"Поздравляем! Ваша заявка на участие в проекте '{instance.project.title}' была одобрена."
            if instance.status == ApplicationStatus.APPROVED
            else f"К сожалению, ваша заявка на проект '{instance.project.title}' была отклонена."
        )
        
        if instance.reviewed_by:
            message += f"\n\nКомментарий от организации: {instance.review_comment or 'Без комментария'}"
        
        # Создаем уведомление
        notification = Notification.objects.create(
            recipient=instance.volunteer,
            sender=instance.reviewed_by or instance.project.organization,
            notification_type=notification_type,
            title=title,
            message=message,
            content_type=ContentType.objects.get_for_model(Application),
            object_id=instance.id
        )
        
        # Отправляем email асинхронно, если Celery доступен
        try:
            send_notification_email.delay(notification.id)
        except Exception as e:
            # Если Celery недоступен, логируем ошибку, но не прерываем процесс
            print(f"Warning: Could not send notification email: {e}")


@receiver(post_save, sender=Project)
def project_created_or_updated(sender, instance, created, **kwargs):
    """Отправка уведомлений о новых проектах."""
    
    # Уведомляем только о создании новых активных проектов
    if created and instance.status == 'active':
        from apps.users.models import User, UserRole
        
        # Находим всех волонтеров
        volunteers = User.objects.filter(role=UserRole.VOLUNTEER, is_active=True)
        
        title = f"Новый проект: {instance.title}"
        message = f"""
        Опубликован новый проект, который может вас заинтересовать!
        
        Название: {instance.title}
        Описание: {instance.description[:200]}...
        Категория: {instance.category.name}
        Формат: {instance.get_format_display()}
        Регион: {instance.region.name if instance.region else 'Онлайн'}
        
        Подайте заявку прямо сейчас!
        """
        
        # Создаем уведомления для всех волонтеров
        notifications = []
        for volunteer in volunteers:
            notifications.append(Notification(
                recipient=volunteer,
                sender=instance.organization,
                notification_type=NotificationType.NEW_PROJECT,
                title=title,
                message=message.strip(),
                content_type=ContentType.objects.get_for_model(Project),
                object_id=instance.id
            ))
        
        # Массовое создание
        Notification.objects.bulk_create(notifications)
        
        # Отправляем email уведомления тем, кто подписан
        for notification in notifications:
            try:
                preferences = notification.recipient.notification_preferences
                if preferences.email_new_projects:
                    try:
                        send_notification_email.delay(notification.id)
                    except Exception as e:
                        print(f"Warning: Could not send notification email: {e}")
            except NotificationPreference.DoesNotExist:
                # Если настроек нет, создаем их с настройками по умолчанию
                from apps.notifications.models import NotificationPreference
                NotificationPreference.objects.create(user=notification.recipient)
                if notification.recipient.notification_preferences.email_new_projects:
                    try:
                        send_notification_email.delay(notification.id)
                    except Exception as e:
                        print(f"Warning: Could not send notification email: {e}")
