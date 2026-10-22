import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.reports.models import ProjectReport, ReportStatus, VolunteerContribution
from apps.projects.models import Project, Category
from apps.users.models import UserRole

User = get_user_model()


class TestProjectReportPermissions:
    """Test project report permissions and access control."""

    def test_report_crud_permissions(self, db):
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
            role=UserRole.ADMIN,
            is_staff=True
        )
        
        # Create project and report
        category = Category.objects.create(name='Test Category')
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test',
            goals_achieved='Test'
        )
        
        client = APIClient()
        
        # Test volunteer permissions
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Volunteer cannot view reports
        response = client.get(f'/api/reports/reports/{report.id}/')
        assert response.status_code == 403
        
        # Volunteer cannot create reports
        response = client.post('/api/reports/reports/', {
            'project': project.id,
            'title': 'Volunteer Report',
            'description': 'Test',
            'goals_achieved': 'Test'
        })
        assert response.status_code == 403
        
        # Volunteer cannot update reports
        response = client.patch(f'/api/reports/reports/{report.id}/', {'title': 'Updated'})
        assert response.status_code == 403
        
        # Test organization permissions
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Organization can view own reports
        response = client.get(f'/api/reports/reports/{report.id}/')
        assert response.status_code == 200
        
        # Organization can create reports for own projects
        new_project_for_org = Project.objects.create(
            title='Another Org Project',
            description='Test',
            category=category,
            organization=organization
        )
        response = client.post('/api/reports/reports/', {
            'project': new_project_for_org.id,
            'title': 'New Report',
            'description': 'Test',
            'goals_achieved': 'Test'
        })
        assert response.status_code in [201, 400]  # 400 if duplicate
        
        # Organization can update own reports (limited fields)
        response = client.patch(f'/api/reports/reports/{report.id}/', {
            'title': 'Updated Title',
            'description': 'Updated description'
        })
        assert response.status_code == 200
        
        # Organization cannot approve/reject reports
        response = client.post(f'/api/reports/reports/{report.id}/approve/')
        assert response.status_code == 403
        
        response = client.post(f'/api/reports/reports/{report.id}/reject/')
        assert response.status_code == 403
        
        # Test admin permissions
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Admin can view any report
        response = client.get(f'/api/reports/reports/{report.id}/')
        assert response.status_code == 200
        
        # Admin can update any report
        response = client.patch(f'/api/reports/reports/{report.id}/', {
            'title': 'Admin Updated'
        })
        assert response.status_code == 200
        
        # Admin can approve/reject reports
        report.status = ReportStatus.SUBMITTED
        report.save()
        
        response = client.post(f'/api/reports/reports/{report.id}/approve/', {
            'review_comment': 'Approved!'
        })
        assert response.status_code == 200
        
        # Create new project and report for rejection test
        reject_project = Project.objects.create(
            title='Reject Project',
            description='Test',
            category=category,
            organization=organization
        )
        new_report = ProjectReport.objects.create(
            project=reject_project,
            title='New Report',
            description='Test',
            goals_achieved='Test',
            status=ReportStatus.SUBMITTED
        )
        
        response = client.post(f'/api/reports/reports/{new_report.id}/reject/', {
            'review_comment': 'Rejected!'
        })
        assert response.status_code == 200

    def test_report_visibility_filters(self, db):
        """Test report visibility based on user role."""
        # Create users
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
        
        # Create projects and reports
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
        
        report1 = ProjectReport.objects.create(
            project=project1,
            title='Report 1',
            description='Test',
            goals_achieved='Test'
        )
        
        report2 = ProjectReport.objects.create(
            project=project2,
            title='Report 2',
            description='Test',
            goals_achieved='Test'
        )
        
        client = APIClient()
        
        # Org1 should see only their own reports
        refresh = RefreshToken.for_user(org1)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get('/api/reports/reports/')
        assert response.status_code == 200
        
        report_ids = [r['id'] for r in response.data['results']]
        assert report1.id in report_ids  # Own report
        assert report2.id not in report_ids  # Other organization's report
        
        # Admin should see all reports
        admin = User.objects.create_user(
            username='admin_vis',
            email='admin_vis@example.com',
            password='testpass123',
            role=UserRole.ADMIN,
            is_staff=True
        )
        
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get('/api/reports/reports/')
        assert response.status_code == 200
        
        report_ids = [r['id'] for r in response.data['results']]
        assert report1.id in report_ids
        assert report2.id in report_ids

    def test_report_submission_permissions(self, db):
        """Test who can submit reports."""
        organization = User.objects.create_user(
            username='organization',
            email='org@example.com',
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
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test',
            goals_achieved='Test'
        )
        
        client = APIClient()
        
        # Organization can submit own report
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.post(f'/api/reports/reports/{report.id}/submit/')
        assert response.status_code == 200
        
        report.refresh_from_db()
        assert report.status == ReportStatus.SUBMITTED
        
        # Volunteer cannot submit reports
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.post(f'/api/reports/reports/{report.id}/submit/')
        assert response.status_code == 403

    def test_cross_organization_access(self, db):
        """Test that organizations cannot access other organization's reports."""
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
        
        # Report for org1's project
        report1 = ProjectReport.objects.create(
            project=project1,
            title='Report 1',
            description='Test',
            goals_achieved='Test'
        )
        
        # Report for org2's project
        report2 = ProjectReport.objects.create(
            project=project2,
            title='Report 2',
            description='Test',
            goals_achieved='Test'
        )
        
        client = APIClient()
        
        # Org1 trying to access org2's report
        refresh = RefreshToken.for_user(org1)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get(f'/api/reports/reports/{report2.id}/')
        assert response.status_code == 404  # IsFiltered
        
        response = client.patch(f'/api/reports/reports/{report2.id}/', {'title': 'Hijacked'})
        assert response.status_code == 404  # IsFiltered

    def test_volunteer_contribution_permissions(self, db):
        """Test volunteer contribution permissions."""
        organization = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        admin = User.objects.create_user(
            username='admin_contrib',
            email='admin_contrib@example.com',
            password='testpass123',
            role=UserRole.ADMIN,
            is_staff=True
        )
        
        category = Category.objects.create(name='Test Category')
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test',
            goals_achieved='Test'
        )
        
        contribution = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer,
            hours_contributed=10,
            tasks_completed='Test tasks'
        )
        
        client = APIClient()
        
        # Volunteer cannot access contributions
        refresh = RefreshToken.for_user(volunteer)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get(f'/api/reports/contributions/{contribution.id}/')
        assert response.status_code == 403
        
        response = client.post('/api/reports/contributions/', {
            'report': report.id,
            'volunteer': volunteer.id,
            'hours_contributed': 5,
            'tasks_completed': 'Test'
        })
        assert response.status_code == 403
        
        # Organization can manage contributions for their reports
        refresh = RefreshToken.for_user(organization)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get(f'/api/reports/contributions/{contribution.id}/')
        assert response.status_code == 200
        
        new_volunteer = User.objects.create_user(
            username='volunteer2',
            email='volunteer2@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        response = client.post('/api/reports/contributions/', {
            'report': report.id,
            'volunteer': new_volunteer.id,
            'hours_contributed': 8,
            'tasks_completed': 'Another test',
            'impact_description': 'Impact'
        })
        assert response.status_code == 201
        
        # Admin can manage any contributions
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get(f'/api/reports/contributions/{contribution.id}/')
        assert response.status_code == 200
        
        response = client.patch(f'/api/reports/contributions/{contribution.id}/', {
            'hours_contributed': 12,
            'performance_rating': 5
        })
        assert response.status_code == 200
