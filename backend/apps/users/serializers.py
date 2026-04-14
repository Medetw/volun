from rest_framework import serializers
from django.db.models import Avg
from apps.users.models import User, VolunteerProfile, OrganizationProfile, VolunteerCertificate, VolunteerHoursLog


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователей."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 'is_active', 'avatar']
        read_only_fields = ['id', 'role']


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

    class Meta:
        model = VolunteerCertificate
        fields = [
            'id', 'title', 'description', 'file', 'project', 'project_title',
            'issued_by', 'issued_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

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
