import pytest
from rest_framework import serializers
from apps.users.models import User, VolunteerProfile, OrganizationProfile, UserRole, OrganizationType
from apps.users.serializers import (
    VolunteerProfileSerializer,
    OrganizationProfileSerializer,
    UserSerializer
)


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
        profile = volunteer_user.volunteer_profile
        data = {'first_name': 'Updated Name'}
        serializer = VolunteerProfileSerializer(profile, data=data, partial=True)
        assert serializer.is_valid(raise_exception=True)
        
        updated_profile = serializer.save()
        assert updated_profile.first_name == 'Updated Name'

    def test_serialization_output(self, db, volunteer_user):
        """Test serializer output format."""
        profile = volunteer_user.volunteer_profile
        profile.first_name = 'John'
        profile.last_name = 'Doe'
        profile.city = 'Almaty'
        profile.skills = ['teaching']
        profile.volunteer_hours = 5
        profile.save()
        
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
        profile = organization_user.organization_profile
        profile.name = 'Test Organization'
        profile.organization_type = OrganizationType.NGO
        profile.description = 'Test description'
        profile.save()
        
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
        profile = volunteer_user.volunteer_profile
        profile.first_name = 'John'
        profile.last_name = 'Doe'
        profile.save()
        
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
        profile = organization_user.organization_profile
        profile.name = 'Test Organization'
        profile.organization_type = OrganizationType.NGO
        profile.save()
        
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
