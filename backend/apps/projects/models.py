from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import User


class Category(models.Model):
    """Category for projects (e.g., Education, Environment, Healthcare)."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Region(models.Model):
    """Region for projects and users."""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=32, blank=True, default="")  # Optional region code
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class ProjectFormat(models.TextChoices):
    ONLINE = "online", "Online"
    OFFLINE = "offline", "Offline"
    HYBRID = "hybrid", "Hybrid"


class ProjectStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Project(models.Model):
    """Project created by an organization."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="projects")
    format = models.CharField(max_length=32, choices=ProjectFormat.choices, default=ProjectFormat.OFFLINE)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="projects", null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    volunteers_needed = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    status = models.CharField(max_length=32, choices=ProjectStatus.choices, default=ProjectStatus.DRAFT)
    organization = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects", limit_choices_to={'role': 'organization'})
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    requirements = models.TextField(blank=True, default="")  # Requirements for volunteers
    contact_info = models.JSONField(default=dict, blank=True)  # Additional contact information

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['region', 'status']),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.organization.username})"

    @property
    def is_active(self) -> bool:
        """Check if project is currently active."""
        return self.status == ProjectStatus.ACTIVE

    @property
    def volunteers_count(self) -> int:
        """Get current number of approved volunteers."""
        # Will be implemented when applications app is ready
        # return self.applications.filter(status='approved').count()
        return 0

    @property
    def volunteers_remaining(self) -> int:
        """Calculate remaining volunteer slots."""
        return max(0, self.volunteers_needed - self.volunteers_count)
