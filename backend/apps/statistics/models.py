"""
Модели для статистики - избегаем circular imports.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserStats(models.Model):
    """Кэшированная статистика пользователей."""
    total_users = models.IntegerField(default=0)
    volunteers = models.IntegerField(default=0)
    organizations = models.IntegerField(default=0)
    admins = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    recent_users = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stats_users'


class ProjectStats(models.Model):
    """Кэшированная статистика проектов."""
    total_projects = models.IntegerField(default=0)
    active_projects = models.IntegerField(default=0)
    completed_projects = models.IntegerField(default=0)
    total_volunteers_needed = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stats_projects'


class ApplicationStats(models.Model):
    """Кэшированная статистика заявок."""
    total_applications = models.IntegerField(default=0)
    pending_applications = models.IntegerField(default=0)
    approved_applications = models.IntegerField(default=0)
    total_hours = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stats_applications'
