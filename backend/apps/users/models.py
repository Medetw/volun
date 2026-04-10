from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models


class UserRole(models.TextChoices):
    VOLUNTEER = "volunteer", "Volunteer"
    ORGANIZATION = "organization", "Organization"
    ADMIN = "admin", "Admin"


class User(AbstractUser):
    """
    Base user for the platform.
    - Role defines authorization level (RBAC will be expanded later).
    - Phone is optional for now (email is handled by AbstractUser).
    """

    role = models.CharField(max_length=32, choices=UserRole.choices, default=UserRole.VOLUNTEER)
    phone = models.CharField(max_length=32, blank=True, default="")
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name="Аватар",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )

    # Password reset fields
    password_reset_code = models.CharField(max_length=6, blank=True, null=True)
    password_reset_expiry = models.DateTimeField(null=True, blank=True)


class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="volunteer_profile")
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=32, blank=True, default="")
    city = models.CharField(max_length=255, blank=True, default="")
    region = models.CharField(max_length=255, blank=True, default="")
    skills = models.JSONField(default=list, blank=True)
    interests = models.JSONField(default=list, blank=True)
    volunteer_hours = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"VolunteerProfile(user_id={self.user_id})"


class OrganizationType(models.TextChoices):
    NGO = "ngo", "НКО"
    FOUNDATION = "foundation", "Фонд"
    ASSOCIATION = "association", "Ассоциация"
    CORPORATE = "corporate", "Корпорация"
    GOVERNMENT = "government", "Государственная"
    EDUCATIONAL = "educational", "Образовательная"
    RELIGIOUS = "religious", "Религиозная"
    INITIATIVE_GROUP = "initiative_group", "Инициативная группа"
    OTHER = "other", "Другое"


class OrganizationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organization_profile")
    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=64, choices=OrganizationType.choices)
    description = models.TextField(blank=True, default="")
    region = models.CharField(max_length=255, blank=True, default="")
    contacts = models.JSONField(default=dict, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"OrganizationProfile(id={self.id}, name={self.name})"

class VolunteerCertificate(models.Model):
    """Сертификаты волонтёра."""
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    file = models.FileField(
        upload_to='certificates/', verbose_name="Файл сертификата",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='certificates',
        verbose_name="Связанный проект"
    )
    issued_by = models.CharField(max_length=255, blank=True, default="", verbose_name="Кем выдан")
    issued_at = models.DateField(null=True, blank=True, verbose_name="Дата выдачи")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружено")

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.title} — {self.volunteer.username}"
