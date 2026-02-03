from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для администрирования пользователей."""

    password = serializers.CharField(write_only=True, required=False)
    organization_name = serializers.CharField(
        source="organization_profile.name", required=False
    )
    organization_type = serializers.CharField(
        source="organization_profile.organization_type", required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "is_active",
            "date_joined",
            "password",
            "organization_name",
            "organization_type",
        ]
        read_only_fields = ["id", "date_joined"]

    def create(self, validated_data):
        """Создание пользователя с паролем."""
        password = validated_data.pop("password", None)
        organization_data = validated_data.pop("organization_profile", None)

        user = User.objects.create_user(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        # Обновляем профиль организации если есть данные
        if organization_data and user.role == "organization":
            if hasattr(user, "organization_profile"):
                for key, value in organization_data.items():
                    setattr(user.organization_profile, key, value)
                user.organization_profile.save()

        return user

    def update(self, instance, validated_data):
        """Обновление пользователя."""
        password = validated_data.pop("password", None)
        organization_data = validated_data.pop("organization_profile", None)

        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        # Обновляем профиль организации
        if organization_data and instance.role == "organization":
            if hasattr(instance, "organization_profile"):
                for key, value in organization_data.items():
                    setattr(instance.organization_profile, key, value)
                instance.organization_profile.save()

        return instance
