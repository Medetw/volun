from rest_framework import serializers
from apps.users.models import User, VolunteerProfile, OrganizationProfile


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователей."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 'is_active']
        read_only_fields = ['id', 'role']


class VolunteerProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля волонтера."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = VolunteerProfile
        fields = [
            'id', 'user', 'first_name', 'last_name', 'birth_date', 
            'gender', 'city', 'region', 'skills', 'interests', 'volunteer_hours'
        ]


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
