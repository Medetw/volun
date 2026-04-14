from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_add_moderator_role_volunteerhours"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModeratorProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("department", models.CharField(blank=True, default="", max_length=255, verbose_name="Отдел / направление")),
                ("can_view_volunteers", models.BooleanField(default=True, verbose_name="Просматривать таблицу волонтёров")),
                ("can_manage_hours", models.BooleanField(default=True, verbose_name="Вносить учёт рабочего времени")),
                ("can_manage_certificates", models.BooleanField(default=True, verbose_name="Добавлять сертификаты волонтёрам")),
                ("notes", models.TextField(blank=True, default="", verbose_name="Заметки")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="moderator_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Профиль модератора",
                "verbose_name_plural": "Профили модераторов",
            },
        ),
    ]
