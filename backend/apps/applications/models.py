from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import User
from apps.projects.models import Project


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "Ожидает рассмотрения"
    APPROVED = "approved", "Принята"
    REJECTED = "rejected", "Отклонена"
    CANCELLED = "cancelled", "Отменена"


class Application(models.Model):
    """Заявка волонтера на участие в проекте."""
    volunteer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="applications",
        limit_choices_to={'role': 'volunteer'}
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name="applications"
    )
    status = models.CharField(
        max_length=32, 
        choices=ApplicationStatus.choices, 
        default=ApplicationStatus.PENDING
    )
    
    # Данные заявки
    cover_letter = models.TextField(
        blank=True, 
        default="", 
        help_text="Сопроводительное письмо волонтера"
    )
    hours_committed = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Количество часов, которое волонтер готов уделить"
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Даты рассмотрения
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
        limit_choices_to={'role': 'organization'}
    )
    
    # Комментарий организации при рассмотрении
    review_comment = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ['volunteer', 'project']  # 1 волонтер = 1 заявка на проект
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['volunteer', 'status']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self) -> str:
        return f"Application({self.volunteer.username} → {self.project.title})"

    @property
    def is_pending(self) -> bool:
        """Проверяет, находится ли заявка на рассмотрении."""
        return self.status == ApplicationStatus.PENDING

    @property
    def is_approved(self) -> bool:
        """Проверяет, принята ли заявка."""
        return self.status == ApplicationStatus.APPROVED

    @property
    def can_be_cancelled(self) -> bool:
        """Может ли заявка быть отменена волонтером."""
        return self.status in [ApplicationStatus.PENDING, ApplicationStatus.APPROVED]
