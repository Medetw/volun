from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_alter_organizationprofile_organization_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("volunteer", "Волонтер"),
                    ("organization", "Организация"),
                    ("moderator", "Модератор"),
                    ("admin", "Админ"),
                ],
                default="volunteer",
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="VolunteerHoursLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "hours",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Часы",
                    ),
                ),
                ("description", models.TextField(blank=True, default="", verbose_name="Описание деятельности")),
                ("date", models.DateField(verbose_name="Дата активности")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Записано")),
                (
                    "moderator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="moderated_hours",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Модератор",
                    ),
                ),
                (
                    "volunteer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hours_logs",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Волонтёр",
                    ),
                ),
            ],
            options={
                "verbose_name": "Запись часов волонтёра",
                "verbose_name_plural": "Записи часов волонтёров",
                "ordering": ["-date"],
            },
        ),
    ]
