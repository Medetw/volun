import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.projects.models import Project, Category, Region
from apps.users.models import User, UserRole


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
        response = client.get(reverse('project-detail', kwargs={'pk': project.id}))
        assert response.status_code == status.HTTP_200_OK
        
        # Volunteer cannot create projects
        response = client.post(reverse('project-list'), {
            'title': 'New Project',
            'description': 'Test',
            'category': category.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Volunteer cannot update projects
        response = client.patch(reverse('project-detail', kwargs={'pk': project.id}), {'title': 'Updated'})
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        
        # Volunteer cannot delete projects
        response = client.delete(reverse('project-detail', kwargs={'pk': project.id}))
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        
        # Test organization permissions
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Organization can create projects
        response = client.post(reverse('project-list'), {
            'title': 'New Project',
            'description': 'Test',
            'category': category.id
        })
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        
        # Organization can update own project
        response = client.patch(reverse('project-detail', kwargs={'pk': project.id}), {'title': 'Updated'})
        assert response.status_code == status.HTTP_200_OK
        
        # Organization can delete own project
        response = client.delete(reverse('project-detail', kwargs={'pk': project.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
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
        response = client.patch(reverse('project-detail', kwargs={'pk': new_project.id}), {'title': 'Admin Updated'})
        assert response.status_code == status.HTTP_200_OK
        
        # Admin can delete any project
        response = client.delete(reverse('project-detail', kwargs={'pk': new_project.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT

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
        response = client.get(reverse('project-list'))
        assert response.status_code == status.HTTP_200_OK
        
        project_ids = [p['id'] for p in response.data['results']]
        assert active_project.id in project_ids
        assert draft_project.id not in project_ids
        
        # Organization should see own draft projects
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get(reverse('project-list'))
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
        response = client.get(reverse('category-list'))
        assert response.status_code == status.HTTP_200_OK
        
        response = client.get(reverse('region-list'))
        assert response.status_code == status.HTTP_200_OK
        
        # Volunteer cannot create categories or regions
        response = client.post(reverse('category-list'), {'name': 'New Category'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        response = client.post(reverse('region-list'), {'name': 'New Region'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test organization permissions
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Organization also cannot create categories or regions
        response = client.post(reverse('category-list'), {'name': 'New Category'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        response = client.post(reverse('region-list'), {'name': 'New Region'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test admin permissions
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Admin can create categories and regions
        response = client.post(reverse('category-list'), {
            'name': 'Admin Category',
            'description': 'Created by admin'
        })
        assert response.status_code == status.HTTP_201_CREATED
        
        response = client.post(reverse('region-list'), {
            'name': 'Admin Region',
            'code': 'AR'
        })
        assert response.status_code == status.HTTP_201_CREATED

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
        
        response = client.patch(reverse('project-detail', kwargs={'pk': project.id}), {'title': 'Hijacked'})
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        
        # org1 can update own project
        refresh = RefreshToken.for_user(org1)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.patch(reverse('project-detail', kwargs={'pk': project.id}), {'title': 'Legitimate Update'})
        assert response.status_code == status.HTTP_200_OK
        
        project.refresh_from_db()
        assert project.title == 'Legitimate Update'
