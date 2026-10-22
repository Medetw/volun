import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import UserRole

User = get_user_model()


class TestUserPermissions:
    """Test user permissions and RBAC."""

    def test_volunteer_permissions(self, db):
        """Test volunteer user permissions."""
        user = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        # Volunteer can access own profile
        assert user.has_perm('users.view_own_profile')
        
        # Volunteer cannot access admin features
        assert not user.has_perm('users.view_all_users')
        assert not user.has_perm('users.moderate_projects')

    def test_organization_permissions(self, db):
        """Test organization user permissions."""
        user = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        # Organization can manage own projects
        assert user.has_perm('projects.add_project')
        assert user.has_perm('projects.change_own_project')
        
        # Organization cannot access other organization's projects
        assert not user.has_perm('projects.change_all_projects')

    def test_admin_permissions(self, db):
        """Test admin user permissions."""
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role=UserRole.ADMIN
        )
        
        # Admin has all permissions
        assert user.has_perm('users.view_all_users')
        assert user.has_perm('users.moderate_users')
        assert user.has_perm('projects.moderate_projects')
        assert user.has_perm('projects.view_all_projects')

    def test_unauthenticated_permissions(self, db):
        """Test unauthenticated user permissions."""
        client = APIClient()
        
        # Unauthenticated users can only access public endpoints
        response = client.get('/api/auth/me/')
        assert response.status_code == 401
        
        # But can access public project list
        response = client.get(reverse('project-list'))
        assert response.status_code == 200

    def test_role_based_api_access(self, db):
        """Test role-based API access control."""
        # Create users with different roles
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
        
        # Test volunteer access
        client = APIClient()
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Volunteer can create application
        response = client.post(reverse('application-list'), {
            'project': 1,
            'cover_letter': 'I want to join',
            'hours_committed': 5
        })
        # 400/404 because project doesn't exist, but not 403
        assert response.status_code in [400, 404]
        
        # Volunteer cannot create projects
        response = client.post(reverse('project-list'), {
            'title': 'Test Project',
            'description': 'Test',
            'category': 1
        })
        assert response.status_code == 403
        
        # Test organization access
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Organization can create projects
        response = client.post(reverse('project-list'), {
            'title': 'Test Project',
            'description': 'Test',
            'category': 1
        })
        # 400 because category doesn't exist, but not 403
        assert response.status_code == 400
        
        # Test admin access
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Admin can access admin endpoints
        response = client.get('/api/admin/statistics/')
        assert response.status_code in [200, 404]

    def test_cross_role_access_denial(self, db):
        """Test that users cannot access endpoints for other roles."""
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
        
        client = APIClient()
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Volunteer trying to access organization-only endpoints
        response = client.post(reverse('application-approve', kwargs={'pk': 1}))
        assert response.status_code in [403, 404]
        
        # Volunteer trying to access admin-only endpoints
        response = client.get(reverse('admin-users-list'))
        assert response.status_code == 403
