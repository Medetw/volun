import pytest
from django.urls import reverse
from rest_framework import status
from apps.reports.models import ProjectReport, ReportStatus, VolunteerContribution
from apps.projects.models import Project
from apps.users.models import User, UserRole


class TestProjectReportAPI:
    """Test project report API endpoints."""

    def test_list_reports_organization(self, auth_organization_client, organization_user, project_report):
        """Test that organizations can list their own reports."""
        url = reverse('projectreport-list')
        response = auth_organization_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Should only see reports for their projects
        reports = response.data['results']
        assert len(reports) >= 1
        # Verify reports belong to organization's projects

    def test_list_reports_admin(self, auth_admin_client, project_report):
        """Test that admins can list all reports."""
        url = reverse('projectreport-list')
        response = auth_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Should see all reports
        reports = response.data['results']
        assert len(reports) >= 1

    def test_list_reports_volunteer_forbidden(self, auth_volunteer_client):
        """Test that volunteers cannot list reports."""
        url = reverse('projectreport-list')
        response = auth_volunteer_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_own_report(self, auth_organization_client, organization_user, project_report):
        """Test retrieving own report."""
        url = reverse('projectreport-detail', kwargs={'pk': project_report.pk})
        response = auth_organization_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == project_report.title

    def test_retrieve_report_admin(self, auth_admin_client, project_report):
        """Test that admin can retrieve any report."""
        url = reverse('projectreport-detail', kwargs={'pk': project_report.pk})
        response = auth_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_other_organization_report_forbidden(self, auth_organization_client, other_organization_user, other_project_report):
        """Test that organization cannot retrieve other's report."""
        url = reverse('projectreport-detail', kwargs={'pk': other_project_report.pk})
        response = auth_organization_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_report_organization(self, auth_organization_client, organization_user, project):
        """Test that organization can create report."""
        url = reverse('projectreport-list')
        data = {
            'project': project.id,
            'title': 'New Report',
            'description': 'Project completed successfully',
            'goals_achieved': 'All goals achieved',
            'total_volunteers_participated': 10,
            'total_volunteer_hours': 50,
            'beneficiaries_count': 100
        }
        
        response = auth_organization_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        report = ProjectReport.objects.get(title='New Report')
        assert report.project == project
        assert report.status == ReportStatus.DRAFT

    def test_create_report_volunteer_forbidden(self, auth_volunteer_client, project):
        """Test that volunteer cannot create report."""
        url = reverse('projectreport-list')
        data = {
            'project': project.id,
            'title': 'Volunteer Report',
            'description': 'Test',
            'goals_achieved': 'Test'
        }
        
        response = auth_volunteer_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_duplicate_report(self, auth_organization_client, organization_user, project, project_report):
        """Test creating duplicate report for same project."""
        url = reverse('projectreport-list')
        data = {
            'project': project.id,
            'title': 'Another Report',
            'description': 'Test',
            'goals_achieved': 'Test'
        }
        
        response = auth_organization_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_own_report(self, auth_organization_client, organization_user, project_report):
        """Test updating own report."""
        url = reverse('projectreport-detail', kwargs={'pk': project_report.pk})
        data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'goals_achieved': 'Updated goals'
        }
        
        response = auth_organization_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        project_report.refresh_from_db()
        assert project_report.title == 'Updated Title'

    def test_update_other_report_forbidden(self, auth_organization_client, other_organization_user, other_project_report):
        """Test that organization cannot update other's report."""
        url = reverse('projectreport-detail', kwargs={'pk': other_project_report.pk})
        data = {'title': 'Hijacked'}
        
        response = auth_organization_client.patch(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_submit_report(self, auth_organization_client, organization_user, project_report):
        """Test submitting report for review."""
        url = reverse('projectreport-submit', kwargs={'pk': project_report.pk})
        response = auth_organization_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        project_report.refresh_from_db()
        assert project_report.status == ReportStatus.SUBMITTED
        assert project_report.submitted_at is not None

    def test_submit_already_submitted_report(self, auth_organization_client, organization_user, project_report):
        """Test submitting already submitted report."""
        project_report.status = ReportStatus.SUBMITTED
        project_report.save()
        
        url = reverse('projectreport-submit', kwargs={'pk': project_report.pk})
        response = auth_organization_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_approve_report_admin(self, auth_admin_client, admin_user, project_report):
        """Test that admin can approve report."""
        project_report.status = ReportStatus.SUBMITTED
        project_report.save()
        
        url = reverse('projectreport-approve', kwargs={'pk': project_report.pk})
        data = {'review_comment': 'Great report!'}
        
        response = auth_admin_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        project_report.refresh_from_db()
        assert project_report.status == ReportStatus.APPROVED
        assert project_report.review_comment == 'Great report!'
        assert project_report.reviewed_by == admin_user

    def test_reject_report_admin(self, auth_admin_client, admin_user, project_report):
        """Test that admin can reject report."""
        project_report.status = ReportStatus.SUBMITTED
        project_report.save()
        
        url = reverse('projectreport-reject', kwargs={'pk': project_report.pk})
        data = {'review_comment': 'Needs more details'}
        
        response = auth_admin_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        project_report.refresh_from_db()
        assert project_report.status == ReportStatus.REJECTED
        assert project_report.review_comment == 'Needs more details'
        assert project_report.reviewed_by == admin_user

    def test_approve_report_organization_forbidden(self, auth_organization_client, organization_user, project_report):
        """Test that organization cannot approve report."""
        url = reverse('projectreport-approve', kwargs={'pk': project_report.pk})
        response = auth_organization_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_report_forbidden(self, auth_organization_client, project_report):
        """Test that reports cannot be deleted."""
        url = reverse('projectreport-detail', kwargs={'pk': project_report.pk})
        response = auth_organization_client.delete(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestVolunteerContributionAPI:
    """Test volunteer contribution API endpoints."""

    def test_list_contributions_report_owner(self, auth_organization_client, organization_user, volunteer_contribution):
        """Test that report owner can list contributions."""
        url = reverse('volunteercontribution-list')
        response = auth_organization_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        contributions = response.data['results']
        assert len(contributions) >= 1

    def test_list_contributions_admin(self, auth_admin_client, volunteer_contribution):
        """Test that admin can list all contributions."""
        url = reverse('volunteercontribution-list')
        response = auth_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        contributions = response.data['results']
        assert len(contributions) >= 1

    def test_create_contribution_organization(self, auth_organization_client, organization_user, project_report, volunteer_user):
        """Test that organization can create contribution."""
        url = reverse('volunteercontribution-list')
        data = {
            'report': project_report.id,
            'volunteer': volunteer_user.id,
            'hours_contributed': 10,
            'tasks_completed': 'Taught classes',
            'impact_description': 'Great impact',
            'performance_rating': 5,
            'feedback': 'Excellent work'
        }
        
        response = auth_organization_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        contribution = VolunteerContribution.objects.get(
            report=project_report,
            volunteer=volunteer_user
        )
        assert contribution.hours_contributed == 10

    def test_create_contribution_volunteer_forbidden(self, auth_volunteer_client, project_report):
        """Test that volunteer cannot create contribution."""
        url = reverse('volunteercontribution-list')
        data = {
            'report': project_report.id,
            'volunteer': 1,  # Would be their own ID
            'hours_contributed': 5,
            'tasks_completed': 'Test'
        }
        
        response = auth_volunteer_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_contribution_organization(self, auth_organization_client, organization_user, volunteer_contribution):
        """Test updating contribution."""
        url = reverse('volunteercontribution-detail', kwargs={'pk': volunteer_contribution.pk})
        data = {
            'hours_contributed': 15,
            'performance_rating': 4,
            'feedback': 'Updated feedback'
        }
        
        response = auth_organization_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        volunteer_contribution.refresh_from_db()
        assert volunteer_contribution.hours_contributed == 15
        assert volunteer_contribution.performance_rating == 4

    def test_contribution_filters(self, auth_organization_client, organization_user, volunteer_contribution):
        """Test contribution filtering."""
        url = reverse('volunteercontribution-list')
        
        # Filter by report
        response = auth_organization_client.get(url, {'report': volunteer_contribution.report.id})
        assert response.status_code == status.HTTP_200_OK
        assert all(c['report'] == volunteer_contribution.report.id for c in response.data['results'])
        
        # Filter by volunteer
        response = auth_organization_client.get(url, {'volunteer': volunteer_contribution.volunteer.id})
        assert response.status_code == status.HTTP_200_OK
        assert all(c['volunteer'] == volunteer_contribution.volunteer.id for c in response.data['results'])


@pytest.fixture
def other_organization_user(db):
    """Create another organization user for testing."""
    return User.objects.create_user(
        username='otherorg',
        email='other@example.com',
        password='testpass123',
        role=UserRole.ORGANIZATION
    )


@pytest.fixture
def other_project(db, other_organization_user, category):
    """Create another project for testing."""
    return Project.objects.create(
        title='Other Project',
        description='Test description',
        category=category,
        organization=other_organization_user
    )


@pytest.fixture
def other_project_report(db, other_project):
    """Create another project report for testing."""
    return ProjectReport.objects.create(
        project=other_project,
        title='Other Report',
        description='Test description',
        goals_achieved='Test goals'
    )
