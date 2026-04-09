from typing import Optional, Dict, Any
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from apps.users.models import User, UserRole, VolunteerProfile, OrganizationProfile, OrganizationType


class VolunteerRegisterSerializer(serializers.Serializer):
    """Serializer for volunteer registration."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    
    # Volunteer profile fields
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, max_length=32)
    city = serializers.CharField(required=False, allow_blank=True, max_length=255)
    region = serializers.CharField(required=False, allow_blank=True, max_length=255)
    skills = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    interests = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        password_confirm = validated_data.pop('password_confirm')
        
        # Extract volunteer profile fields
        volunteer_fields = {
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', ''),
            'birth_date': validated_data.pop('birth_date', None),
            'gender': validated_data.pop('gender', ''),
            'city': validated_data.pop('city', ''),
            'region': validated_data.pop('region', ''),
            'skills': validated_data.pop('skills', []),
            'interests': validated_data.pop('interests', []),
        }
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],  # Use email as username
            password=password,
            role=UserRole.VOLUNTEER,
            phone=validated_data.get('phone', ''),
        )
        
        # Create volunteer profile
        VolunteerProfile.objects.create(user=user, **volunteer_fields)
        
        return user


class OrganizationRegisterSerializer(serializers.Serializer):
    """Serializer for organization registration."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    
    # Organization profile fields
    name = serializers.CharField(required=True, max_length=255)
    organization_type = serializers.ChoiceField(choices=OrganizationType.choices, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True, max_length=255)
    contacts = serializers.DictField(required=False, allow_empty=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        password_confirm = validated_data.pop('password_confirm')
        
        # Extract organization profile fields
        org_fields = {
            'name': validated_data.pop('name'),
            'organization_type': validated_data.pop('organization_type'),
            'description': validated_data.pop('description', ''),
            'region': validated_data.pop('region', ''),
            'contacts': validated_data.pop('contacts', {}),
        }
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],  # Use email as username
            password=password,
            role=UserRole.ORGANIZATION,
            phone=validated_data.get('phone', ''),
        )
        
        # Create organization profile
        OrganizationProfile.objects.create(user=user, **org_fields)
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Try to authenticate using email
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    volunteer_profile = serializers.SerializerMethodField()
    organization_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'phone', 'avatar', 'date_joined', 'is_active',
                  'volunteer_profile', 'organization_profile']
        read_only_fields = ['id', 'date_joined', 'is_active']

    def get_volunteer_profile(self, obj: User) -> Optional[Dict[str, Any]]:
        if hasattr(obj, 'volunteer_profile'):
            return {
                'first_name': obj.volunteer_profile.first_name,
                'last_name': obj.volunteer_profile.last_name,
                'birth_date': obj.volunteer_profile.birth_date,
                'gender': obj.volunteer_profile.gender,
                'city': obj.volunteer_profile.city,
                'region': obj.volunteer_profile.region,
                'skills': obj.volunteer_profile.skills,
                'interests': obj.volunteer_profile.interests,
                'volunteer_hours': obj.volunteer_profile.volunteer_hours,
            }
        return None

    def get_organization_profile(self, obj: User) -> Optional[Dict[str, Any]]:
        if hasattr(obj, 'organization_profile'):
            return {
                'name': obj.organization_profile.name,
                'organization_type': obj.organization_profile.organization_type,
                'description': obj.organization_profile.description,
                'region': obj.organization_profile.region,
                'contacts': obj.organization_profile.contacts,
                'is_verified': obj.organization_profile.is_verified,
            }
        return None


class UserUpdateSerializer(serializers.Serializer):
    """Serializer for updating user profile."""
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    
    # Volunteer profile fields
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, max_length=32)
    city = serializers.CharField(required=False, allow_blank=True, max_length=255)
    region = serializers.CharField(required=False, allow_blank=True, max_length=255)
    skills = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    interests = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    
    # Organization profile fields
    name = serializers.CharField(required=False, max_length=255)
    organization_type = serializers.ChoiceField(choices=OrganizationType.choices, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    contacts = serializers.DictField(required=False, allow_empty=True)

    def update(self, instance, validated_data):
        # Update user fields
        if 'phone' in validated_data:
            instance.phone = validated_data['phone']
            instance.save()
        
        # Update volunteer profile if exists
        if hasattr(instance, 'volunteer_profile'):
            volunteer_fields = ['first_name', 'last_name', 'birth_date', 'gender', 
                              'city', 'region', 'skills', 'interests']
            for field in volunteer_fields:
                if field in validated_data:
                    setattr(instance.volunteer_profile, field, validated_data[field])
            instance.volunteer_profile.save()
        
        # Update organization profile if exists
        if hasattr(instance, 'organization_profile'):
            org_fields = ['name', 'organization_type', 'description', 'contacts']
            for field in org_fields:
                if field in validated_data:
                    setattr(instance.organization_profile, field, validated_data[field])
            instance.organization_profile.save()
        
        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса сброса пароля."""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Проверяем существование email."""
        if not User.objects.filter(email=value).exists():
            # Не сообщаем о несуществующем email для безопасности
            return value
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения сброса пароля."""
    email = serializers.EmailField(required=True)
    reset_code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        min_length=8
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Проверяем совпадение паролей."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Пароли не совпадают'
            })
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля."""
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        min_length=8
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        """Проверяем текущий пароль."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value

    def validate(self, attrs):
        """Проверяем совпадение новых паролей."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Новые пароли не совпадают'
            })
        return attrs

    def save(self):
        """Сохраняем новый пароль."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
