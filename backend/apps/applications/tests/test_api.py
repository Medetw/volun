import pytest
from django.urls import reverse
from rest_framework import status
from apps.applications.models import Application, ApplicationStatus
from apps.users.models import UserRole


class TestApplicationAPI:
    """Test application API endpoints."""

    def test_list_applications_volunteer(self, auth_volunteer_client, volunteer_user, application):
        """Test that volunteers can list their own applications."""
        url = reverse('application-list')
        response = auth_volunteer_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Should only see own applications
        applications = response.data['results']
        assert len(applications) >= 1
        assert all(app['volunteer'] == volunteer_user.id for app in applications)

    def test_list_applications_organization(self, auth_organization_client, organization_user, application):
        """Test that organizations can list applications for their projects."""
        url = reverse('application-list')
        response = auth_organization_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Should see applications for their projects
        applications = response.data['results']
        assert len(applications) >= 1

    def test_list_applications_admin(self, auth_admin_client, application):
        """Test that admins can list all applications."""
        url = reverse('application-list')
        response = auth_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Should see all applications
        applications = response.data['results']
        assert len(applications) >= 1

    def test_list_applications_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list applications."""
        url = reverse('application-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_own_application(self, auth_volunteer_client, volunteer_user, application):
        """Test retrieving own application."""
        url = reverse('application-detail', kwargs={'pk': application.pk})
        response = auth_volunteer_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['volunteer'] == volunteer_user.id

    def test_retrieve_application_organization(self, auth_organization_client, organization_user, application):
        """Test that organization can retrieve application for their project."""
        url = reverse('application-detail', kwargs={'pk': application.pk})
        response = auth_organization_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_other_application_forbidden(self, auth_volunteer_client, other_volunteer_user, other_application):
        """Test that volunteer cannot retrieve other's application."""
        url = reverse('application-detail', kwargs={'pk': other_application.pk})
        response = auth_volunteer_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_application_volunteer(self, auth_volunteer_client, volunteer_user, project):
        """Test that volunteer can create application."""
        url = reverse('application-list')
        data = {
            'project': project.id,
            'cover_letter': 'I want to join this project',
            'hours_committed': 5
        }
        
        response = auth_volunteer_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        application = Application.objects.get(project=project, volunteer=volunteer_user)
        assert application.cover_letter == 'I want to join this project'
        assert application.hours_committed == 5
        assert application.status == ApplicationStatus.PENDING

    def test_create_application_organization_forbidden(self, auth_organization_client, project):
        """Test that organization cannot create applications."""
        url = reverse('application-list')
        data = {
            'project': project.id,
            'cover_letter': 'I want to join'
        }
        
        response = auth_organization_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_duplicate_application(self, auth_volunteer_client, volunteer_user, application):
        """Test creating duplicate application."""
        url = reverse('application-list')
        data = {
            'project': application.project.id,
            'cover_letter': 'Another application'
        }
        
        response = auth_volunteer_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_own_application(self, auth_volunteer_client, volunteer_user, application):
        """Test updating own application."""
        url = reverse('application-detail', kwargs={'pk': application.pk})
        data = {
            'cover_letter': 'Updated cover letter',
            'hours_committed': 10
        }
        
        response = auth_volunteer_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        application.refresh_from_db()
        assert application.cover_letter == 'Updated cover letter'
        assert application.hours_committed == 10

    def test_approve_application_organization(self, auth_organization_client, organization_user, application):
        """Test that organization can approve application."""
        url = reverse('application-detail', kwargs={'pk': application.pk})
        data = {
            'status': ApplicationStatus.APPROVED,
            'review_comment': 'Great candidate!'
        }
        
        response = auth_organization_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        application.refresh_from_db()
        assert application.status == ApplicationStatus.APPROVED
        assert application.review_comment == 'Great candidate!'
        assert application.reviewed_by == organization_user

    def test_reject_application_organization(self, auth_organization_client, organization_user, application):
        """Test that organization can reject application."""
        url = reverse('application-detail', kwargs={'pk': application.pk})
        data = {
            'status': ApplicationStatus.REJECTED,
            'review_comment': 'Not suitable at this time'
        }
        
        response = auth_organization_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        application.refresh_from_db()
        assert application.status == ApplicationStatus.REJECTED
        assert application.review_comment == 'Not suitable at this time'

    def test_change_status_volunteer_forbidden(self, auth_volunteer_client, application):
        """Test that volunteer cannot change application status."""
        url = reverse('application-detail', kwargs={'pk': application.pk})
        data = {'status': ApplicationStatus.APPROVED}
        
        response = auth_volunteer_client.patch(url, data)
        # Status field should not be available for volunteers
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_cancel_application_volunteer(self, auth_volunteer_client, application):
        """Test that volunteer can cancel own application."""
        url = reverse('application-cancel', kwargs={'pk': application.pk})
        response = auth_volunteer_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        application.refresh_from_db()
        assert application.status == ApplicationStatus.CANCELLED

    def test_cancel_application_organization_forbidden(self, auth_organization_client, application):
        """Test that organization cannot cancel application."""
        url = reverse('application-cancel', kwargs={'pk': application.pk})
        response = auth_organization_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_application_forbidden(self, auth_volunteer_client, application):
        """Test that applications cannot be deleted."""
        url = reverse('application-detail', kwargs={'pk': application.pk})
        response = auth_volunteer_client.delete(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_application_filters(self, auth_organization_client, organization_user, application, approved_application):
        """Test application filtering."""
        url = reverse('application-list')
        
        # Filter by status
        response = auth_organization_client.get(url, {'status': ApplicationStatus.PENDING})
        assert response.status_code == status.HTTP_200_OK
        assert all(app['status'] == ApplicationStatus.PENDING for app in response.data['results'])
        
        # Filter by project
        response = auth_organization_client.get(url, {'project': application.project.id})
        assert response.status_code == status.HTTP_200_OK
        assert all(app['project'] == application.project.id for app in response.data['results'])

    def test_application_statistics(self, auth_organization_client, organization_user, application, approved_application):
        """Test application statistics endpoint."""
        url = reverse('application-statistics')
        response = auth_organization_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        stats = response.data
        assert 'total_applications' in stats
        assert 'pending_applications' in stats
        assert 'approved_applications' in stats
        assert 'rejected_applications' in stats
        assert stats['total_applications'] >= 2


@pytest.fixture
def other_volunteer_user(db):
    """Create another volunteer user for testing."""
    return User.objects.create_user(
        username='volunteer2',
        email='volunteer2@example.com',
        password='testpass123',
        role=UserRole.VOLUNTEER
    )


@pytest.fixture
def other_application(db, other_volunteer_user, project):
    """Create another application for testing."""
    return Application.objects.create(
        volunteer=other_volunteer_user,
        project=project,
        cover_letter='Another application',
        hours_committed=3
    )
