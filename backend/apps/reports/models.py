from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class ReportStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    SUBMITTED = "submitted", "Отправлен"
    APPROVED = "approved", "Одобрен"
    REJECTED = "rejected", "Отклонен"


class ProjectReport(models.Model):
    """Отчет организации по проекту."""
    project = models.OneToOneField(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name="report",
        verbose_name="Проект"
    )
    
    # Основная информация
    title = models.CharField(max_length=255, verbose_name="Заголовок отчета")
    description = models.TextField(verbose_name="Описание проекта")
    
    # Результаты
    goals_achieved = models.TextField(
        verbose_name="Достигнутые цели",
        help_text="Опишите цели, которые были достигнуты в рамках проекта"
    )
    challenges_faced = models.TextField(
        blank=True,
        default="",
        verbose_name="Сложности и проблемы",
        help_text="Опишите трудности, с которыми столкнулись"
    )
    
    # Статистика
    total_volunteers_participated = models.PositiveIntegerField(
        default=0,
        verbose_name="Всего волонтеров участвовало"
    )
    total_volunteer_hours = models.PositiveIntegerField(
        default=0,
        verbose_name="Всего волонтерских часов"
    )
    beneficiaries_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество beneficiarieв"
    )
    
    # Файлы и медиа
    report_file = models.FileField(
        upload_to='reports/files/',
        blank=True,
        null=True,
        verbose_name="Файл отчета"
    )
    photos = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Фотографии",
        help_text="Список URL фотографий"
    )
    
    # Дополнительная информация
    lessons_learned = models.TextField(
        blank=True,
        default="",
        verbose_name="Уроки и выводы",
        help_text="Главные уроки, извлеченные из проекта"
    )
    future_plans = models.TextField(
        blank=True,
        default="",
        verbose_name="Планы на будущее",
        help_text="Планы по развитию проекта"
    )
    
    # Статус и модерация
    status = models.CharField(
        max_length=32,
        choices=ReportStatus.choices,
        default=ReportStatus.DRAFT,
        verbose_name="Статус"
    )
    
    # Модерация
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_reports",
        limit_choices_to={'role': 'admin'},
        verbose_name="Проверил"
    )
    review_comment = models.TextField(
        blank=True,
        default="",
        verbose_name="Комментарий модератора"
    )
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Отправлено")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Проверено")

    class Meta:
        verbose_name = "Отчет по проекту"
        verbose_name_plural = "Отчеты по проектам"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['status', 'submitted_at']),
        ]

    def __str__(self) -> str:
        return f"Отчет: {self.title} ({self.project.title})"

    @property
    def is_submitted(self) -> bool:
        """Проверяет, отправлен ли отчет."""
        return self.status == ReportStatus.SUBMITTED

    @property
    def is_approved(self) -> bool:
        """Проверяет, одобрен ли отчет."""
        return self.status == ReportStatus.APPROVED

    def submit(self):
        """Отправить отчет на модерацию."""
        if self.status == ReportStatus.DRAFT:
            self.status = ReportStatus.SUBMITTED
            self.submitted_at = timezone.now()
            self.save(update_fields=['status', 'submitted_at'])

    def approve(self, reviewer, comment=""):
        """Одобрить отчет."""
        self.status = ReportStatus.APPROVED
        self.reviewed_by = reviewer
        self.review_comment = comment
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'review_comment', 'reviewed_at'])

    def reject(self, reviewer, comment=""):
        """Отклонить отчет."""
        self.status = ReportStatus.REJECTED
        self.reviewed_by = reviewer
        self.review_comment = comment
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'review_comment', 'reviewed_at'])


class VolunteerContribution(models.Model):
    """Вклад волонтера в проект (для отчетов)."""
    report = models.ForeignKey(
        ProjectReport,
        on_delete=models.CASCADE,
        related_name="contributions",
        verbose_name="Отчет"
    )
    volunteer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'volunteer'},
        verbose_name="Волонтер"
    )
    
    # Вклад волонтера
    hours_contributed = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(1)],
        verbose_name="Часы участия"
    )
    tasks_completed = models.TextField(
        verbose_name="Выполненные задачи",
        help_text="Опишите задачи, которые выполнил волонтер"
    )
    impact_description = models.TextField(
        verbose_name="Вклад и влияние",
        help_text="Опишите вклад волонтера в успех проекта"
    )
    
    # Оценка (необязательно)
    performance_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка работы (1-5)",
        help_text="Оцените работу волонтера от 1 до 5"
    )
    feedback = models.TextField(
        blank=True,
        default="",
        verbose_name="Обратная связь",
        help_text="Отзыв о работе волонтера"
    )

    class Meta:
        verbose_name = "Вклад волонтера"
        verbose_name_plural = "Вклады волонтеров"
        unique_together = ['report', 'volunteer']
        ordering = ['-hours_contributed']

    def __str__(self) -> str:
        return f"{self.volunteer.username} - {self.hours_contributed}ч в {self.report.project.title}"
