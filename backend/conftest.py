import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import VolunteerProfile, OrganizationProfile, ModeratorProfile
from apps.projects.models import Category, Region, Project
from apps.applications.models import Application

User = get_user_model()


@pytest.fixture
def api_client():
    """Return APIClient instance."""
    return APIClient()


@pytest.fixture
def volunteer_user(db):
    """Create a volunteer user with profile."""
    user = User.objects.create_user(
        username='volunteer1',
        email='volunteer@example.com',
        password='testpass123',
        role='volunteer',
        phone='+1234567890'
    )
    VolunteerProfile.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        city='Almaty',
        region='Almaty',
        skills=['teaching', 'programming'],
        interests=['education', 'technology']
    )
    return user


@pytest.fixture
def organization_user(db):
    """Create an organization user with profile."""
    user = User.objects.create_user(
        username='org1',
        email='org@example.com',
        password='testpass123',
        role='organization',
        phone='+1234567891'
    )
    OrganizationProfile.objects.create(
        user=user,
        name='Test Organization',
        organization_type='ngo',
        description='Test organization description',
        city='Almaty',
        region='Almaty',
        contacts={'phone': '+1234567891', 'email': 'org@example.com'}
    )
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_user(
        username='admin1',
        email='admin@example.com',
        password='testpass123',
        role='admin',
        is_staff=True,
        is_superuser=True,
        phone='+1234567892'
    )


@pytest.fixture
def moderator_user(db):
    """Create a full-access moderator user with a ModeratorProfile."""
    user = User.objects.create_user(
        username='moderator1',
        email='moderator@example.com',
        password='testpass123',
        role='moderator',
        phone='+1234567893'
    )
    ModeratorProfile.objects.create(
        user=user,
        department='Test Department',
        can_view_volunteers=True,
        can_manage_hours=True,
        can_manage_certificates=True,
        notes='Full-access moderator fixture.',
    )
    return user


@pytest.fixture
def moderator_user_limited(db):
    """Create a moderator with all RBAC permissions disabled."""
    user = User.objects.create_user(
        username='moderator_limited',
        email='moderator_limited@example.com',
        password='testpass123',
        role='moderator',
        phone='+1234567894'
    )
    ModeratorProfile.objects.create(
        user=user,
        department='Limited Dept',
        can_view_volunteers=False,
        can_manage_hours=False,
        can_manage_certificates=False,
        notes='Limited moderator fixture – all RBAC permissions off.',
    )
    return user


@pytest.fixture
def auth_volunteer_client(api_client, volunteer_user):
    """Return authenticated client for volunteer."""
    refresh = RefreshToken.for_user(volunteer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def auth_organization_client(api_client, organization_user):
    """Return authenticated client for organization."""
    refresh = RefreshToken.for_user(organization_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def auth_admin_client(api_client, admin_user):
    """Return authenticated client for admin."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def auth_moderator_client(api_client, moderator_user):
    """Return authenticated client for full-access moderator."""
    refresh = RefreshToken.for_user(moderator_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def auth_moderator_limited_client(api_client, moderator_user_limited):
    """Return authenticated client for limited moderator (all RBAC permissions off)."""
    refresh = RefreshToken.for_user(moderator_user_limited)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name='Education',
        description='Education related projects'
    )


@pytest.fixture
def region(db):
    """Create a test region."""
    return Region.objects.create(
        name='Almaty',
        code='ALM'
    )


@pytest.fixture
def project(db, organization_user, category, region):
    """Create a test project."""
    return Project.objects.create(
        title='Test Project',
        description='Test project description',
        category=category,
        organization=organization_user,
        region=region,
        volunteers_needed=10,
        status='active'
    )


@pytest.fixture
def draft_project(db, organization_user, category, region):
    """Create a draft project."""
    return Project.objects.create(
        title='Draft Project',
        description='Draft project description',
        category=category,
        organization=organization_user,
        region=region,
        volunteers_needed=5,
        status='draft'
    )


@pytest.fixture
def application(db, volunteer_user, project):
    """Create a test application."""
    return Application.objects.create(
        volunteer=volunteer_user,
        project=project,
        cover_letter='I want to join this project',
        hours_committed=5
    )


@pytest.fixture
def approved_application(db, volunteer_user, project):
    """Create an approved application."""
    return Application.objects.create(
        volunteer=volunteer_user,
        project=project,
        status='approved',
        cover_letter='I want to join this project',
        hours_committed=5
    )


@pytest.fixture
def mock_email_backend(mocker):
    """Mock email backend."""
    mock = mocker.patch('django.core.mail.outlook.EmailBackend.send_messages')
    mock.return_value = True
    return mock


@pytest.fixture
def mock_celery_task(mocker):
    """Mock celery task."""
    mock = mocker.patch('apps.notifications.tasks.send_notification_email.delay')
    return mock


@pytest.fixture
def mock_storage(mocker):
    """Mock file storage."""
    mock = mocker.patch('django.core.files.storage.default_storage.save')
    mock.return_value = 'test_file.jpg'
    return mock
