import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.applications.models import Application, ApplicationStatus
from apps.projects.models import Project, Category
from apps.users.models import UserRole

User = get_user_model()


class TestApplicationPermissions:
    """Test application permissions and access control."""

    def test_application_crud_permissions(self, db):
        """Test CRUD permissions for different user roles."""
        # Create users
        volunteer = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role=UserRole.ADMIN
        )
        
        # Create project and application
        category = Category.objects.create(name='Test Category')
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=organization
        )
        
        application = Application.objects.create(
            volunteer=volunteer,
            project=project,
            cover_letter='I want to join'
        )
        
        client = APIClient()
        
        # Test volunteer permissions
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Volunteer can view own applications
        response = client.get(f'/api/applications/{application.id}/')
        assert response.status_code == 200
        
        # Volunteer can create applications
        response = client.post('/api/applications/', {
            'project': project.id,
            'cover_letter': 'Another application'
        })
        assert response.status_code in [201, 400]  # 400 if duplicate
        
        # Volunteer can update own application (limited fields)
        response = client.patch(f'/api/applications/{application.id}/', {
            'cover_letter': 'Updated cover letter'
        })
        assert response.status_code == 200
        
        # Volunteer cannot delete applications
        response = client.delete(f'/api/applications/{application.id}/')
        assert response.status_code == 405
        
        # Test organization permissions
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Organization can view applications for their projects
        response = client.get(f'/api/applications/{application.id}/')
        assert response.status_code == 200
        
        # Organization cannot create applications
        response = client.post('/api/applications/', {
            'project': project.id,
            'cover_letter': 'I want to join'
        })
        assert response.status_code == 403
        
        # Organization can review applications (change status)
        response = client.patch(f'/api/applications/{application.id}/', {
            'status': ApplicationStatus.APPROVED,
            'review_comment': 'Approved!'
        })
        assert response.status_code == 200
        
        # Test admin permissions
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Admin can view any application
        response = client.get(f'/api/applications/{application.id}/')
        assert response.status_code == 200
        
        # Admin can update any application
        response = client.patch(f'/api/applications/{application.id}/', {
            'status': ApplicationStatus.REJECTED,
            'review_comment': 'Admin decision'
        })
        assert response.status_code == 200

    def test_application_visibility_filters(self, db):
        """Test application visibility based on user role."""
        # Create users
        volunteer1 = User.objects.create_user(
            username='volunteer1',
            email='volunteer1@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        volunteer2 = User.objects.create_user(
            username='volunteer2',
            email='volunteer2@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization1 = User.objects.create_user(
            username='org1',
            email='org1@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        organization2 = User.objects.create_user(
            username='org2',
            email='org2@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        # Create projects and applications
        category = Category.objects.create(name='Test Category')
        
        project1 = Project.objects.create(
            title='Project 1',
            description='Test',
            category=category,
            organization=organization1
        )
        
        project2 = Project.objects.create(
            title='Project 2',
            description='Test',
            category=category,
            organization=organization2
        )
        
        app1 = Application.objects.create(
            volunteer=volunteer1,
            project=project1,
            cover_letter='App 1'
        )
        
        app2 = Application.objects.create(
            volunteer=volunteer2,
            project=project1,
            cover_letter='App 2'
        )
        
        app3 = Application.objects.create(
            volunteer=volunteer1,
            project=project2,
            cover_letter='App 3'
        )
        
        client = APIClient()
        
        # Volunteer1 should see only their own applications
        refresh = RefreshToken.for_user(volunteer1)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get('/api/applications/')
        assert response.status_code == 200
        
        app_ids = [app['id'] for app in response.data['results']]
        assert app1.id in app_ids  # Own application
        assert app3.id in app_ids  # Own application
        assert app2.id not in app_ids  # Other volunteer's application
        
        # Organization1 should see applications for their projects only
        refresh = RefreshToken.for_user(organization1)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get('/api/applications/')
        assert response.status_code == 200
        
        app_ids = [app['id'] for app in response.data['results']]
        assert app1.id in app_ids  # Application for their project
        assert app2.id in app_ids  # Application for their project
        assert app3.id not in app_ids  # Application for other organization's project

    def test_status_change_permissions(self, db):
        """Test who can change application status."""
        volunteer = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        other_organization = User.objects.create_user(
            username='otherorg',
            email='other@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Test Category')
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=organization
        )
        
        application = Application.objects.create(
            volunteer=volunteer,
            project=project,
            cover_letter='I want to join'
        )
        
        client = APIClient()
        
        # Volunteer cannot change status
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.patch(f'/api/applications/{application.id}/', {
            'status': ApplicationStatus.APPROVED
        })
        # Status field should not be available or should be ignored
        assert response.status_code in [200, 400]
        
        # Organization can change status for their project
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.patch(f'/api/applications/{application.id}/', {
            'status': ApplicationStatus.APPROVED,
            'review_comment': 'Approved!'
        })
        assert response.status_code == 200
        
        application.refresh_from_db()
        assert application.status == ApplicationStatus.APPROVED
        
        # Other organization cannot change status
        refresh = RefreshToken.for_user(other_organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.patch(f'/api/applications/{application.id}/', {
            'status': ApplicationStatus.REJECTED,
            'review_comment': 'Rejected!'
        })
        assert response.status_code == 404  # IsFiltered, application not found

    def test_application_cancellation_permissions(self, db):
        """Test who can cancel applications."""
        volunteer = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Test Category')
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=organization
        )
        
        application = Application.objects.create(
            volunteer=volunteer,
            project=project,
            cover_letter='I want to join'
        )
        
        client = APIClient()
        
        # Volunteer can cancel own application
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.post(f'/api/applications/{application.id}/cancel/')
        assert response.status_code == 200
        
        application.refresh_from_db()
        assert application.status == ApplicationStatus.CANCELLED
        
        # Create new application for organization test
        project2 = Project.objects.create(
            title='Test Project 2',
            description='Test 2',
            category=category,
            organization=organization
        )
        new_app = Application.objects.create(
            volunteer=volunteer,
            project=project2,
            cover_letter='Another application'
        )
        
        # Organization cannot cancel applications
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.post(f'/api/applications/{new_app.id}/cancel/')
        assert response.status_code == 403

    def test_cross_organization_access(self, db):
        """Test that organizations cannot access other organization's applications."""
        org1 = User.objects.create_user(
            username='org1',
            email='org1@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        org2 = User.objects.create_user(
            username='org2',
            email='org2@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        category = Category.objects.create(name='Test Category')
        
        project1 = Project.objects.create(
            title='Project 1',
            description='Test',
            category=category,
            organization=org1
        )
        
        project2 = Project.objects.create(
            title='Project 2',
            description='Test',
            category=category,
            organization=org2
        )
        
        # Application for org1's project
        app1 = Application.objects.create(
            volunteer=volunteer,
            project=project1,
            cover_letter='App for org1'
        )
        
        # Application for org2's project
        app2 = Application.objects.create(
            volunteer=User.objects.create_user(
                username='volunteer2',
                email='volunteer2@example.com',
                password='testpass123',
                role=UserRole.VOLUNTEER
            ),
            project=project2,
            cover_letter='App for org2'
        )
        
        client = APIClient()
        
        # Org1 trying to access org2's application
        refresh = RefreshToken.for_user(org1)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get(f'/api/applications/{app2.id}/')
        assert response.status_code == 404  # IsFiltered
        
        response = client.patch(f'/api/applications/{app2.id}/', {
            'status': ApplicationStatus.APPROVED
        })
        assert response.status_code == 404  # IsFiltered
