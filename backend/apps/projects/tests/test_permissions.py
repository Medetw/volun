import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.projects.models import Project
from apps.users.models import UserRole

User = get_user_model()


class TestProjectPermissions:
    """Test project permissions and access control."""

    def test_project_crud_permissions(self, db):
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
        
        # Create project by organization
        from apps.projects.models import Category
        category = Category.objects.create(name='Test Category')
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        client = APIClient()
        
        # Test volunteer permissions
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Volunteer can view projects
        response = client.get(f'/api/projects/{project.id}/')
        assert response.status_code == 200
        
        # Volunteer cannot create projects
        response = client.post('/api/projects/', {
            'title': 'New Project',
            'description': 'Test',
            'category': category.id
        })
        assert response.status_code == 403
        
        # Volunteer cannot update projects
        response = client.patch(f'/api/projects/{project.id}/', {'title': 'Updated'})
        assert response.status_code == 404  # IsFiltered, not found for non-owner
        
        # Volunteer cannot delete projects
        response = client.delete(f'/api/projects/{project.id}/')
        assert response.status_code == 404
        
        # Test organization permissions
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Organization can create projects
        response = client.post('/api/projects/', {
            'title': 'New Project',
            'description': 'Test',
            'category': category.id
        })
        assert response.status_code in [201, 400]  # 400 if validation error, but not 403
        
        # Organization can update own project
        response = client.patch(f'/api/projects/{project.id}/', {'title': 'Updated'})
        assert response.status_code == 200
        
        # Organization can delete own project
        response = client.delete(f'/api/projects/{project.id}/')
        assert response.status_code == 204
        
        # Test admin permissions
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create new project for admin test
        new_project = Project.objects.create(
            title='Admin Test Project',
            description='Test',
            category=category,
            organization=organization
        )
        
        # Admin can update any project
        response = client.patch(f'/api/projects/{new_project.id}/', {'title': 'Admin Updated'})
        assert response.status_code == 200
        
        # Admin can delete any project
        response = client.delete(f'/api/projects/{new_project.id}/')
        assert response.status_code == 204

    def test_project_visibility_filters(self, db):
        """Test project visibility based on status."""
        # Create organization and category
        organization = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        category = Category.objects.create(name='Test Category')
        
        # Create projects with different statuses
        draft_project = Project.objects.create(
            title='Draft Project',
            description='Test',
            category=category,
            organization=organization,
            status='draft'
        )
        
        active_project = Project.objects.create(
            title='Active Project',
            description='Test',
            category=category,
            organization=organization,
            status='active'
        )
        
        completed_project = Project.objects.create(
            title='Completed Project',
            description='Test',
            category=category,
            organization=organization,
            status='completed'
        )
        
        client = APIClient()
        
        # Public user should only see active projects
        response = client.get('/api/projects/')
        assert response.status_code == 200
        
        project_ids = [p['id'] for p in response.data['results']]
        assert active_project.id in project_ids
        assert draft_project.id not in project_ids
        # Completed projects might be visible depending on implementation
        
        # Organization should see own draft projects
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get('/api/projects/')
        project_ids = [p['id'] for p in response.data['results']]
        assert draft_project.id in project_ids  # Organization can see own drafts
        assert active_project.id in project_ids

    def test_category_region_permissions(self, db):
        """Test permissions for categories and regions."""
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
        
        client = APIClient()
        
        # Test volunteer permissions
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Volunteer can view categories and regions
        response = client.get('/api/categories/')
        assert response.status_code == 200
        
        response = client.get('/api/regions/')
        assert response.status_code == 200
        
        # Volunteer cannot create categories or regions
        response = client.post('/api/categories/', {'name': 'New Category'})
        assert response.status_code == 403
        
        response = client.post('/api/regions/', {'name': 'New Region'})
        assert response.status_code == 403
        
        # Test organization permissions
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Organization also cannot create categories or regions
        response = client.post('/api/categories/', {'name': 'New Category'})
        assert response.status_code == 403
        
        response = client.post('/api/regions/', {'name': 'New Region'})
        assert response.status_code == 403
        
        # Test admin permissions
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Admin can create categories and regions
        response = client.post('/api/categories/', {
            'name': 'Admin Category',
            'description': 'Created by admin'
        })
        assert response.status_code == 201
        
        response = client.post('/api/regions/', {
            'name': 'Admin Region',
            'code': 'AR'
        })
        assert response.status_code == 201

    def test_project_ownership_validation(self, db):
        """Test that users can only manage their own projects."""
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
        
        category = Category.objects.create(name='Test Category')
        
        # Create project by org1
        project = Project.objects.create(
            title='Org1 Project',
            description='Test',
            category=category,
            organization=org1
        )
        
        client = APIClient()
        
        # org2 trying to update org1's project
        refresh = RefreshToken.for_user(org2)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.patch(f'/api/projects/{project.id}/', {'title': 'Hijacked'})
        assert response.status_code == 404  # IsFiltered, project not found for org2
        
        # org1 can update own project
        refresh = RefreshToken.for_user(org1)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.patch(f'/api/projects/{project.id}/', {'title': 'Legitimate Update'})
        assert response.status_code == 200
        
        project.refresh_from_db()
        assert project.title == 'Legitimate Update'
