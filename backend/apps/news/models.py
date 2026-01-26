from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import User


class NewsCategory(models.TextChoices):
    GENERAL = "general", "Общие новости"
    EVENTS = "events", "Мероприятия"
    ANNOUNCEMENTS = "announcements", "Объявления"
    SUCCESS_STORIES = "success_stories", "Истории успеха"
    PARTNERS = "partners", "Партнеры"


class NewsStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    PUBLISHED = "published", "Опубликовано"
    ARCHIVED = "archived", "Архив"


class News(models.Model):
    """Модель новостей для платформы."""
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    content = models.TextField(verbose_name="Содержание")
    excerpt = models.TextField(
        max_length=500, 
        blank=True, 
        default="",
        verbose_name="Краткое описание",
        help_text="Отображается в списках новостей"
    )
    
    # Категория и статус
    category = models.CharField(
        max_length=32,
        choices=NewsCategory.choices,
        default=NewsCategory.GENERAL,
        verbose_name="Категория"
    )
    status = models.CharField(
        max_length=32,
        choices=NewsStatus.choices,
        default=NewsStatus.DRAFT,
        verbose_name="Статус"
    )
    
    # Изображение
    image = models.ImageField(
        upload_to='news/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    
    # SEO поля
    meta_title = models.CharField(
        max_length=255, 
        blank=True, 
        default="",
        verbose_name="Meta title"
    )
    meta_description = models.CharField(
        max_length=255, 
        blank=True, 
        default="",
        verbose_name="Meta description"
    )
    
    # Метаданные
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="news_articles",
        limit_choices_to={'role': 'admin'},
        verbose_name="Автор"
    )
    featured = models.BooleanField(
        default=False,
        verbose_name="Избранная новость",
        help_text="Отображается на главной странице"
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество просмотров"
    )
    
    # Даты
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата публикации"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['featured', 'status']),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def is_published(self) -> bool:
        """Проверяет, опубликована ли новость."""
        return self.status == NewsStatus.PUBLISHED

    @property
    def reading_time(self) -> int:
        """Примерное время чтения в минутах."""
        words_count = len(self.content.split())
        return max(1, round(words_count / 200))  # 200 слов в минуту

    def increment_views(self):
        """Увеличивает счетчик просмотров."""
        self.views_count += 1
        self.save(update_fields=['views_count'])
