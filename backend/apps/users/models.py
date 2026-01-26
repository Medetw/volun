from django.contrib.auth.models import AbstractUser
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
    NGO = "ngo", "NPO/NGO"
    INITIATIVE_GROUP = "initiative_group", "Initiative group"
    GOVERNMENT = "government", "Government"


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

# Create your models here.
