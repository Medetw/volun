import pytest
from rest_framework import serializers
from apps.users.models import User, VolunteerProfile, OrganizationProfile, UserRole, OrganizationType
from apps.users.serializers import (
    UserRegistrationSerializer, 
    VolunteerProfileSerializer,
    OrganizationProfileSerializer,
    UserSerializer
)


class TestUserRegistrationSerializer:
    """Test UserRegistrationSerializer."""

    def test_valid_volunteer_registration(self, db):
        """Test valid volunteer registration data."""
        data = {
            'username': 'volunteer1',
            'email': 'volunteer@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'volunteer',
            'phone': '+1234567890'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)

    def test_valid_organization_registration(self, db):
        """Test valid organization registration data."""
        data = {
            'username': 'org1',
            'email': 'org@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'organization',
            'phone': '+1234567891'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)

    def test_password_mismatch(self, db):
        """Test password mismatch validation."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'role': 'volunteer'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors

    def test_duplicate_username(self, db, volunteer_user):
        """Test duplicate username validation."""
        data = {
            'username': volunteer_user.username,
            'email': 'different@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'volunteer'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_duplicate_email(self, db, volunteer_user):
        """Test duplicate email validation."""
        data = {
            'username': 'differentuser',
            'email': volunteer_user.email,
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'volunteer'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_invalid_role(self, db):
        """Test invalid role validation."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'invalid_role'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'role' in serializer.errors

    def test_missing_required_fields(self, db):
        """Test missing required fields."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing password, password_confirm, role
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
        assert 'password_confirm' in serializer.errors
        assert 'role' in serializer.errors

    def test_create_volunteer_user(self, db):
        """Test creating volunteer user through serializer."""
        data = {
            'username': 'volunteer1',
            'email': 'volunteer@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'volunteer',
            'phone': '+1234567890'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        assert user.username == 'volunteer1'
        assert user.email == 'volunteer@example.com'
        assert user.role == UserRole.VOLUNTEER
        assert user.check_password('testpass123')
        assert not hasattr(user, 'volunteer_profile')  # Profile created separately

    def test_create_organization_user(self, db):
        """Test creating organization user through serializer."""
        data = {
            'username': 'org1',
            'email': 'org@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'organization',
            'phone': '+1234567891'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        assert user.username == 'org1'
        assert user.email == 'org@example.com'
        assert user.role == UserRole.ORGANIZATION
        assert user.check_password('testpass123')


class TestVolunteerProfileSerializer:
    """Test VolunteerProfileSerializer."""

    def test_valid_data(self, db, volunteer_user):
        """Test valid volunteer profile data."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'birth_date': '1990-01-01',
            'gender': 'male',
            'city': 'Almaty',
            'region': 'Almaty',
            'skills': ['teaching', 'programming'],
            'interests': ['education', 'technology'],
            'volunteer_hours': 10
        }
        serializer = VolunteerProfileSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)

    def test_partial_update(self, db, volunteer_user):
        """Test partial update of volunteer profile."""
        profile = VolunteerProfile.objects.create(user=volunteer_user)
        data = {'first_name': 'Updated Name'}
        serializer = VolunteerProfileSerializer(profile, data=data, partial=True)
        assert serializer.is_valid(raise_exception=True)
        
        updated_profile = serializer.save()
        assert updated_profile.first_name == 'Updated Name'

    def test_serialization_output(self, db, volunteer_user):
        """Test serializer output format."""
        profile = VolunteerProfile.objects.create(
            user=volunteer_user,
            first_name='John',
            last_name='Doe',
            city='Almaty',
            skills=['teaching'],
            volunteer_hours=5
        )
        
        serializer = VolunteerProfileSerializer(profile)
        data = serializer.data
        
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert data['city'] == 'Almaty'
        assert data['skills'] == ['teaching']
        assert data['volunteer_hours'] == 5


class TestOrganizationProfileSerializer:
    """Test OrganizationProfileSerializer."""

    def test_valid_data(self, db, organization_user):
        """Test valid organization profile data."""
        data = {
            'name': 'Test Organization',
            'organization_type': 'ngo',
            'description': 'Test description',
            'region': 'Almaty',
            'contacts': {'phone': '+123456789', 'email': 'org@example.com'},
            'is_verified': True
        }
        serializer = OrganizationProfileSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)

    def test_invalid_organization_type(self, db, organization_user):
        """Test invalid organization type."""
        data = {
            'name': 'Test Organization',
            'organization_type': 'invalid_type'
        }
        serializer = OrganizationProfileSerializer(data=data)
        assert not serializer.is_valid()
        assert 'organization_type' in serializer.errors

    def test_serialization_output(self, db, organization_user):
        """Test serializer output format."""
        profile = OrganizationProfile.objects.create(
            user=organization_user,
            name='Test Organization',
            organization_type=OrganizationType.NGO,
            description='Test description'
        )
        
        serializer = OrganizationProfileSerializer(profile)
        data = serializer.data
        
        assert data['name'] == 'Test Organization'
        assert data['organization_type'] == OrganizationType.NGO
        assert data['description'] == 'Test description'
        assert data['is_verified'] is False


class TestUserSerializer:
    """Test UserSerializer."""

    def test_user_serialization(self, db, volunteer_user):
        """Test user serialization with profile."""
        VolunteerProfile.objects.create(
            user=volunteer_user,
            first_name='John',
            last_name='Doe'
        )
        
        serializer = UserSerializer(volunteer_user)
        data = serializer.data
        
        assert data['username'] == volunteer_user.username
        assert data['email'] == volunteer_user.email
        assert data['role'] == volunteer_user.role
        assert data['phone'] == volunteer_user.phone
        assert 'volunteer_profile' in data
        assert data['volunteer_profile']['first_name'] == 'John'

    def test_organization_user_serialization(self, db, organization_user):
        """Test organization user serialization."""
        OrganizationProfile.objects.create(
            user=organization_user,
            name='Test Organization',
            organization_type=OrganizationType.NGO
        )
        
        serializer = UserSerializer(organization_user)
        data = serializer.data
        
        assert data['role'] == UserRole.ORGANIZATION
        assert 'organization_profile' in data
        assert data['organization_profile']['name'] == 'Test Organization'

    def test_admin_user_serialization(self, db, admin_user):
        """Test admin user serialization."""
        serializer = UserSerializer(admin_user)
        data = serializer.data
        
        assert data['role'] == UserRole.ADMIN
        assert 'volunteer_profile' not in data
        assert 'organization_profile' not in data
