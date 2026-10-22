import pytest
from django.test import TestCase
from apps.users.models import User, VolunteerProfile, OrganizationProfile, UserRole, OrganizationType


class TestUserModel(TestCase):
    """Test User model."""

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == UserRole.VOLUNTEER  # Default role
        assert user.check_password('testpass123')

    def test_create_volunteer_user(self):
        """Test creating a volunteer user."""
        user = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER,
            phone='+1234567890'
        )
        assert user.role == UserRole.VOLUNTEER
        assert user.phone == '+1234567890'

    def test_create_organization_user(self):
        """Test creating an organization user."""
        user = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION,
            phone='+1234567891'
        )
        assert user.role == UserRole.ORGANIZATION

    def test_create_admin_user(self):
        """Test creating an admin user."""
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role=UserRole.ADMIN
        )
        assert user.role == UserRole.ADMIN

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'testuser'

    def test_password_reset_fields(self):
        """Test password reset fields."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Initially empty
        assert user.password_reset_code is None
        assert user.password_reset_expiry is None
        
        # Set reset code
        user.password_reset_code = '123456'
        user.save()
        
        user.refresh_from_db()
        assert user.password_reset_code == '123456'


class TestVolunteerProfileModel(TestCase):
    """Test VolunteerProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )

    def test_create_volunteer_profile(self):
        """Test creating volunteer profile."""
        profile = VolunteerProfile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            birth_date='1990-01-01',
            gender='male',
            city='Almaty',
            region='Almaty',
            skills=['teaching', 'programming'],
            interests=['education', 'technology'],
            volunteer_hours=10
        )
        
        assert profile.user == self.user
        assert profile.first_name == 'John'
        assert profile.last_name == 'Doe'
        assert profile.city == 'Almaty'
        assert profile.region == 'Almaty'
        assert profile.skills == ['teaching', 'programming']
        assert profile.interests == ['education', 'technology']
        assert profile.volunteer_hours == 10

    def test_volunteer_profile_str(self):
        """Test volunteer profile string representation."""
        profile = VolunteerProfile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe'
        )
        assert str(profile) == f'VolunteerProfile(user_id={self.user.id})'

    def test_volunteer_profile_default_values(self):
        """Test volunteer profile default values."""
        profile = VolunteerProfile.objects.create(user=self.user)
        
        assert profile.first_name == ''
        assert profile.last_name == ''
        assert profile.birth_date is None
        assert profile.gender == ''
        assert profile.city == ''
        assert profile.region == ''
        assert profile.skills == []
        assert profile.interests == []
        assert profile.volunteer_hours == 0

    def test_volunteer_profile_one_to_one(self):
        """Test one-to-one relationship with user."""
        profile = VolunteerProfile.objects.create(user=self.user)
        
        # Should be able to access profile from user
        assert self.user.volunteer_profile == profile
        
        # Should not be able to create second profile
        with pytest.raises(Exception):
            VolunteerProfile.objects.create(user=self.user)


class TestOrganizationProfileModel(TestCase):
    """Test OrganizationProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )

    def test_create_organization_profile(self):
        """Test creating organization profile."""
        profile = OrganizationProfile.objects.create(
            user=self.user,
            name='Test Organization',
            organization_type=OrganizationType.NGO,
            description='Test description',
            region='Almaty',
            contacts={'phone': '+123456789', 'email': 'org@example.com'},
            is_verified=True
        )
        
        assert profile.user == self.user
        assert profile.name == 'Test Organization'
        assert profile.organization_type == OrganizationType.NGO
        assert profile.description == 'Test description'
        assert profile.region == 'Almaty'
        assert profile.contacts == {'phone': '+123456789', 'email': 'org@example.com'}
        assert profile.is_verified is True

    def test_organization_profile_str(self):
        """Test organization profile string representation."""
        profile = OrganizationProfile.objects.create(
            user=self.user,
            name='Test Organization',
            organization_type=OrganizationType.NGO
        )
        assert str(profile) == f'OrganizationProfile(id={profile.id}, name=Test Organization)'

    def test_organization_profile_default_values(self):
        """Test organization profile default values."""
        profile = OrganizationProfile.objects.create(
            user=self.user,
            name='Test Organization',
            organization_type=OrganizationType.NGO
        )
        
        assert profile.description == ''
        assert profile.region == ''
        assert profile.contacts == {}
        assert profile.is_verified is False

    def test_organization_profile_one_to_one(self):
        """Test one-to-one relationship with user."""
        profile = OrganizationProfile.objects.create(
            user=self.user,
            name='Test Organization',
            organization_type=OrganizationType.NGO
        )
        
        # Should be able to access profile from user
        assert self.user.organization_profile == profile
        
        # Should not be able to create second profile
        with pytest.raises(Exception):
            OrganizationProfile.objects.create(user=self.user)


class TestUserRoleChoices(TestCase):
    """Test UserRole choices."""

    def test_user_role_choices(self):
        """Test user role choices are valid."""
        assert UserRole.VOLUNTEER == 'volunteer'
        assert UserRole.ORGANIZATION == 'organization'
        assert UserRole.MODERATOR == 'moderator'
        assert UserRole.ADMIN == 'admin'
        
        # Test choices list
        choices = UserRole.choices
        assert len(choices) == 4
        assert (UserRole.VOLUNTEER.value, UserRole.VOLUNTEER.label) in choices
        assert (UserRole.ORGANIZATION.value, UserRole.ORGANIZATION.label) in choices
        assert (UserRole.MODERATOR.value, UserRole.MODERATOR.label) in choices
        assert (UserRole.ADMIN.value, UserRole.ADMIN.label) in choices


class TestOrganizationTypeChoices(TestCase):
    """Test OrganizationType choices."""

    def test_organization_type_choices(self):
        """Test organization type choices are valid."""
        assert OrganizationType.NGO == 'ngo'
        assert OrganizationType.INITIATIVE_GROUP == 'initiative_group'
        assert OrganizationType.GOVERNMENT == 'government'
        
        # Test choices list
        choices = OrganizationType.choices
        assert len(choices) == 9
        assert (OrganizationType.NGO.value, OrganizationType.NGO.label) in choices
        assert (OrganizationType.INITIATIVE_GROUP.value, OrganizationType.INITIATIVE_GROUP.label) in choices
        assert (OrganizationType.GOVERNMENT.value, OrganizationType.GOVERNMENT.label) in choices
