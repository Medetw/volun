from rest_framework import serializers
from django.db.models import Avg
from apps.users.models import (
    User, VolunteerProfile, OrganizationProfile,
    VolunteerCertificate, VolunteerHoursLog, ModeratorProfile, Blacklist,
)


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователей."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    volunteer_profile = serializers.SerializerMethodField()
    organization_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'avatar',
            'volunteer_profile', 'organization_profile'
        ]
        read_only_fields = ['id', 'role']

    def get_volunteer_profile(self, obj):
        if hasattr(obj, 'volunteer_profile'):
            vp = obj.volunteer_profile
            return {
                'first_name': vp.first_name,
                'last_name': vp.last_name,
                'city': vp.city,
                'skills': vp.skills,
            }
        return None

    def get_organization_profile(self, obj):
        if hasattr(obj, 'organization_profile'):
            op = obj.organization_profile
            return {
                'name': op.name,
                'organization_type': op.organization_type,
            }
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('volunteer_profile') is None:
            ret.pop('volunteer_profile', None)
        if ret.get('organization_profile') is None:
            ret.pop('organization_profile', None)
        return ret


class VolunteerProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля волонтера."""
    user = UserSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerProfile
        fields = [
            'id', 'user', 'first_name', 'last_name', 'birth_date',
            'gender', 'city', 'region', 'skills', 'interests', 'volunteer_hours',
            'average_rating'
        ]

    def get_average_rating(self, obj):
        from apps.reports.models import VolunteerContribution
        result = VolunteerContribution.objects.filter(
            volunteer=obj.user
        ).aggregate(avg=Avg('performance_rating'))
        return round(result['avg'], 1) if result['avg'] else 0


class VolunteerCertificateSerializer(serializers.ModelSerializer):
    """Сериализатор для сертификатов волонтёра."""
    project_title = serializers.CharField(source='project.title', read_only=True, default='')
    volunteer_name = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerCertificate
        fields = [
            'id', 'volunteer', 'volunteer_name', 'title', 'description',
            'file', 'project', 'project_title', 'issued_by', 'issued_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_volunteer_name(self, obj):
        profile = getattr(obj.volunteer, 'volunteer_profile', None)
        if profile and (profile.first_name or profile.last_name):
            return f"{profile.first_name} {profile.last_name}".strip()
        return obj.volunteer.username

    def validate_file(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("Размер файла не должен превышать 10 МБ")
        return value


class OrganizationProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля организации."""
    user = UserSerializer(read_only=True)
    organization_type_display = serializers.CharField(source='get_organization_type_display', read_only=True)
    
    class Meta:
        model = OrganizationProfile
        fields = [
            'id', 'user', 'name', 'organization_type', 'organization_type_display',
            'description', 'region', 'contacts', 'is_verified'
        ]


class VolunteerHoursLogSerializer(serializers.ModelSerializer):
    """Сериализатор для записей часов волонтёра."""
    volunteer_name = serializers.SerializerMethodField()
    moderator_name = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerHoursLog
        fields = [
            'id', 'volunteer', 'volunteer_name', 'moderator', 'moderator_name',
            'hours', 'description', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'moderator']

    def get_volunteer_name(self, obj):
        profile = getattr(obj.volunteer, 'volunteer_profile', None)
        if profile and (profile.first_name or profile.last_name):
            return f"{profile.first_name} {profile.last_name}".strip()
        return obj.volunteer.username

    def get_moderator_name(self, obj):
        if obj.moderator:
            return obj.moderator.get_full_name() or obj.moderator.username
        return None


class ModeratorProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля модератора с RBAC-разрешениями."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = ModeratorProfile
        fields = [
            'id', 'username', 'email', 'department',
            'can_view_volunteers', 'can_manage_hours', 'can_manage_certificates',
            'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'username', 'email']


class BlacklistSerializer(serializers.ModelSerializer):
    """Сериализатор ЧС-записи."""
    volunteer_name = serializers.SerializerMethodField()
    banned_by_name = serializers.SerializerMethodField()
    is_currently_banned = serializers.SerializerMethodField()

    class Meta:
        model = Blacklist
        fields = [
            'id', 'volunteer', 'volunteer_name',
            'reason', 'banned_until',
            'banned_by', 'banned_by_name',
            'is_active', 'is_currently_banned', 'created_at',
        ]
        read_only_fields = ['id', 'banned_by', 'is_active', 'created_at']

    def get_volunteer_name(self, obj) -> str:
        profile = getattr(obj.volunteer, 'volunteer_profile', None)
        if profile and (profile.first_name or profile.last_name):
            return f"{profile.first_name} {profile.last_name}".strip()
        return obj.volunteer.username

    def get_banned_by_name(self, obj) -> str | None:
        return obj.banned_by.username if obj.banned_by else None

    def get_is_currently_banned(self, obj) -> bool:
        return obj.is_currently_banned()

    def validate_reason(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Причина обязательна при добавлении в ЧС.")
        return value

    def validate_banned_until(self, value):
        """Дата блокировки не может быть в прошлом."""
        if value is not None:
            from django.utils import timezone
            if value <= timezone.now():
                raise serializers.ValidationError(
                    "Дата окончания блокировки не может быть в прошлом."
                )
        return value

    def validate_volunteer(self, user):
        """Нельзя забанить не-волонтёра."""
        if user.role != 'volunteer':
            raise serializers.ValidationError("Добавлять в ЧС можно только волонтёров.")
        # Проверка уже существующего активного бана
        if Blacklist.objects.filter(volunteer=user, is_active=True).exists():
            raise serializers.ValidationError("Этот волонтёр уже в чёрном списке.")
        return user


class UserAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для администрирования пользователей."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
