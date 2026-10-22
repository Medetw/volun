import pytest
from django.urls import reverse
from rest_framework import status
from apps.projects.models import Project, ProjectStatus
from apps.users.models import UserRole


class TestProjectAPI:
    """Test project API endpoints."""

    def test_list_projects_public(self, api_client, project):
        """Test that anyone can list projects."""
        url = reverse('project-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_list_projects_filters(self, api_client, project, category, region):
        """Test project list filters."""
        url = reverse('project-list')
        
        # Filter by category
        response = api_client.get(url, {'category': category.id})
        assert response.status_code == status.HTTP_200_OK
        assert all((p['category']['id'] if isinstance(p['category'], dict) else p['category']) == category.id for p in response.data['results'])
        
        # Filter by region
        response = api_client.get(url, {'region': region.id})
        assert response.status_code == status.HTTP_200_OK
        assert all((p['region']['id'] if isinstance(p['region'], dict) else p['region']) == region.id for p in response.data['results'])
        
        # Filter by status
        response = api_client.get(url, {'status': ProjectStatus.ACTIVE})
        assert response.status_code == status.HTTP_200_OK
        assert all(p['status'] == ProjectStatus.ACTIVE for p in response.data['results'])
        
        # Filter by format
        response = api_client.get(url, {'format': 'offline'})
        assert response.status_code == status.HTTP_200_OK
        assert all(p['format'] == 'offline' for p in response.data['results'])

    def test_list_projects_search(self, api_client, project):
        """Test project search functionality."""
        url = reverse('project-list')
        
        # Search by title
        response = api_client.get(url, {'search': project.title})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        
        # Search by description
        response = api_client.get(url, {'search': project.description[:10]})
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_project_public(self, api_client, project):
        """Test that anyone can retrieve project details."""
        url = reverse('project-detail', kwargs={'pk': project.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == project.title

    def test_create_project_organization_only(self, auth_organization_client, organization_user, category, region):
        """Test that only organizations can create projects."""
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'description': 'Project description',
            'category': category.id,
            'region': region.id,
            'volunteers_needed': 10,
            'format': 'online'
        }
        
        response = auth_organization_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        project = Project.objects.get(title='New Project')
        assert project.organization == organization_user

    def test_create_project_volunteer_forbidden(self, auth_volunteer_client, category):
        """Test that volunteers cannot create projects."""
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'description': 'Project description',
            'category': category.id,
            'volunteers_needed': 10
        }
        
        response = auth_volunteer_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_project_unauthenticated_forbidden(self, api_client, category):
        """Test that unauthenticated users cannot create projects."""
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'description': 'Project description',
            'category': category.id,
            'volunteers_needed': 10
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_own_project(self, auth_organization_client, organization_user, project):
        """Test that organization can update own project."""
        url = reverse('project-detail', kwargs={'pk': project.pk})
        data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        response = auth_organization_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        project.refresh_from_db()
        assert project.title == 'Updated Title'

    def test_update_other_project_forbidden(self, auth_organization_client, other_organization_user, project):
        """Test that organization cannot update other's project."""
        auth_organization_client.force_authenticate(user=other_organization_user)
        url = reverse('project-detail', kwargs={'pk': project.pk})
        data = {'title': 'Updated Title'}
        
        response = auth_organization_client.patch(url, data)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_delete_own_project(self, auth_organization_client, organization_user, project):
        """Test that organization can delete own project."""
        url = reverse('project-detail', kwargs={'pk': project.pk})
        response = auth_organization_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        assert not Project.objects.filter(pk=project.pk).exists()

    def test_delete_other_project_forbidden(self, auth_organization_client, other_organization_user, project):
        """Test that organization cannot delete other's project."""
        auth_organization_client.force_authenticate(user=other_organization_user)
        url = reverse('project-detail', kwargs={'pk': project.pk})
        response = auth_organization_client.delete(url)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_admin_can_manage_any_project(self, auth_admin_client, project):
        """Test that admin can manage any project."""
        url = reverse('project-detail', kwargs={'pk': project.pk})
        data = {'title': 'Admin Updated Title'}
        
        response = auth_admin_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        project.refresh_from_db()
        assert project.title == 'Admin Updated Title'

    def test_project_volunteers_count(self, api_client, project, approved_application):
        """Test that volunteers count is included in response."""
        url = reverse('project-detail', kwargs={'pk': project.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['volunteers_count'] == 1
        assert response.data['volunteers_remaining'] == project.volunteers_needed - 1


class TestCategoryAPI:
    """Test category API endpoints."""

    def test_list_categories_public(self, api_client, category):
        """Test that anyone can list categories."""
        url = reverse('category-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_category_admin_only(self, auth_admin_client):
        """Test that only admin can create categories."""
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'description': 'New category description'
        }
        
        response = auth_admin_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_category_forbidden(self, auth_organization_client):
        """Test that non-admin cannot create categories."""
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'description': 'New category description'
        }
        
        response = auth_organization_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRegionAPI:
    """Test region API endpoints."""

    def test_list_regions_public(self, api_client, region):
        """Test that anyone can list regions."""
        url = reverse('region-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_region_admin_only(self, auth_admin_client):
        """Test that only admin can create regions."""
        url = reverse('region-list')
        data = {
            'name': 'New Region',
            'code': 'NR'
        }
        
        response = auth_admin_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_region_forbidden(self, auth_organization_client):
        """Test that non-admin cannot create regions."""
        url = reverse('region-list')
        data = {
            'name': 'New Region',
            'code': 'NR'
        }
        
        response = auth_organization_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def other_organization_user(db):
    """Create another organization user for testing."""
    from apps.users.models import User
    return User.objects.create_user(
        username='otherorg',
        email='other@example.com',
        password='testpass123',
        role=UserRole.ORGANIZATION
    )
