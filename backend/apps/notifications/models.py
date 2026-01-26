from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class NotificationType(models.TextChoices):
    APPLICATION_APPROVED = "application_approved", "Заявка одобрена"
    APPLICATION_REJECTED = "application_rejected", "Заявка отклонена"
    NEW_PROJECT = "new_project", "Новый проект"
    PROJECT_UPDATE = "project_update", "Обновление проекта"
    SYSTEM = "system", "Системное уведомление"


class NotificationStatus(models.TextChoices):
    UNREAD = "unread", "Непрочитано"
    READ = "read", "Прочитано"
    ARCHIVED = "archived", "Архивировано"


class Notification(models.Model):
    """Уведомления для пользователей."""
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Получатель"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
        verbose_name="Отправитель"
    )
    
    # Тип и содержание
    notification_type = models.CharField(
        max_length=32,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        verbose_name="Тип уведомления"
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    message = models.TextField(verbose_name="Сообщение")
    
    # Связанные объекты
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Связанный объект (проект, заявка и т.д.)"
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Статус и метаданные
    status = models.CharField(
        max_length=32,
        choices=NotificationStatus.choices,
        default=NotificationStatus.UNREAD,
        verbose_name="Статус"
    )
    is_email_sent = models.BooleanField(default=False, verbose_name="Email отправлен")
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Прочитано")
    
    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.title} → {self.recipient.username}"

    @property
    def is_unread(self) -> bool:
        """Проверяет, является ли уведомление непрочитанным."""
        return self.status == NotificationStatus.UNREAD

    def mark_as_read(self):
        """Отмечает уведомление как прочитанное."""
        if self.status == NotificationStatus.UNREAD:
            self.status = NotificationStatus.READ
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])

    def mark_as_archived(self):
        """Архивирует уведомление."""
        self.status = NotificationStatus.ARCHIVED
        self.save(update_fields=['status'])


class NotificationPreference(models.Model):
    """Настройки уведомлений пользователя."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name="Пользователь"
    )
    
    # Email уведомления
    email_application_approved = models.BooleanField(
        default=True,
        verbose_name="Email при одобрении заявки"
    )
    email_application_rejected = models.BooleanField(
        default=True,
        verbose_name="Email при отклонении заявки"
    )
    email_new_projects = models.BooleanField(
        default=False,
        verbose_name="Email о новых проектах"
    )
    email_project_updates = models.BooleanField(
        default=True,
        verbose_name="Email об обновлениях проектов"
    )
    
    # In-app уведомления
    inapp_application_approved = models.BooleanField(
        default=True,
        verbose_name="In-app при одобрении заявки"
    )
    inapp_application_rejected = models.BooleanField(
        default=True,
        verbose_name="In-app при отклонении заявки"
    )
    inapp_new_projects = models.BooleanField(
        default=True,
        verbose_name="In-app о новых проектах"
    )
    inapp_project_updates = models.BooleanField(
        default=True,
        verbose_name="In-app об обновлениях проектов"
    )

    class Meta:
        verbose_name = "Настройки уведомлений"
        verbose_name_plural = "Настройки уведомлений"

    def __str__(self) -> str:
        return f"Настройки уведомлений для {self.user.username}"
