import pytest
from rest_framework import serializers
from apps.reports.models import ProjectReport, ReportStatus, VolunteerContribution
from apps.reports.serializers import (
    ProjectReportSerializer,
    ProjectReportCreateSerializer,
    ProjectReportUpdateSerializer,
    VolunteerContributionSerializer
)
from apps.users.models import User, UserRole
from apps.projects.models import Project, Category


class TestProjectReportSerializer:
    """Test ProjectReportSerializer."""

    def test_project_report_serialization(self, db, project_report):
        """Test project report serialization output."""
        serializer = ProjectReportSerializer(project_report)
        data = serializer.data
        
        assert data['title'] == project_report.title
        assert data['description'] == project_report.description
        assert data['goals_achieved'] == project_report.goals_achieved
        assert data['total_volunteers_participated'] == project_report.total_volunteers_participated
        assert data['total_volunteer_hours'] == project_report.total_volunteer_hours
        assert data['beneficiaries_count'] == project_report.beneficiaries_count
        assert data['status'] == project_report.status
        assert data['is_submitted'] == project_report.is_submitted
        assert data['is_approved'] == project_report.is_approved
        assert 'project' in data

    def test_report_with_review_data(self, db, project_report, admin_user):
        """Test serialization with review data."""
        project_report.status = ReportStatus.APPROVED
        project_report.reviewed_by = admin_user
        project_report.review_comment = 'Approved!'
        project_report.save()
        
        serializer = ProjectReportSerializer(project_report)
        data = serializer.data
        
        assert data['reviewed_by'] == admin_user.id
        assert data['review_comment'] == 'Approved!'

    def test_report_with_contributions(self, db, project_report, volunteer_contribution):
        """Test serialization with volunteer contributions."""
        serializer = ProjectReportSerializer(project_report)
        data = serializer.data
        
        assert 'contributions' in data
        assert len(data['contributions']) >= 1
        assert data['contributions'][0]['hours_contributed'] == volunteer_contribution.hours_contributed

    def test_read_only_fields(self, db, project_report):
        """Test that certain fields are read-only."""
        serializer = ProjectReportSerializer(project_report, data={
            'is_submitted': False,
            'is_approved': True
        }, partial=True)
        
        assert serializer.is_valid(raise_exception=True)
        updated_report = serializer.save()
        
        # These fields should not be updated
        assert updated_report.is_submitted == project_report.is_submitted
        assert updated_report.is_approved == project_report.is_approved


class TestProjectReportCreateSerializer:
    """Test ProjectReportCreateSerializer."""

    def test_valid_report_creation(self, db, organization_user, project):
        """Test valid report creation data."""
        data = {
            'project': project.id,
            'title': 'Project Report',
            'description': 'Project completed successfully',
            'goals_achieved': 'All goals achieved',
            'total_volunteers_participated': 10,
            'total_volunteer_hours': 50,
            'beneficiaries_count': 100,
            'challenges_faced': 'Some challenges',
            'photos': ['photo1.jpg', 'photo2.jpg'],
            'lessons_learned': 'Important lessons',
            'future_plans': 'Future plans'
        }
        
        serializer = ProjectReportCreateSerializer(
            data=data,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert serializer.is_valid(raise_exception=True)

    def test_missing_required_fields(self, db, organization_user):
        """Test missing required fields."""
        data = {}  # Empty data
        
        serializer = ProjectReportCreateSerializer(
            data=data,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert not serializer.is_valid()
        
        required_fields = ['project', 'title', 'description', 'goals_achieved']
        for field in required_fields:
            assert field in serializer.errors

    def test_invalid_project_id(self, db, organization_user):
        """Test invalid project ID."""
        data = {
            'project': 99999,  # Non-existent project
            'title': 'Test Report',
            'description': 'Test',
            'goals_achieved': 'Test'
        }
        
        serializer = ProjectReportCreateSerializer(
            data=data,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert not serializer.is_valid()
        assert 'project' in serializer.errors

    def test_duplicate_report_validation(self, db, organization_user, project, project_report):
        """Test duplicate report validation."""
        data = {
            'project': project.id,
            'title': 'Another Report',
            'description': 'Test',
            'goals_achieved': 'Test'
        }
        
        serializer = ProjectReportCreateSerializer(
            data=data,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert not serializer.is_valid()
        assert 'project' in serializer.errors

    def test_negative_values_validation(self, db, organization_user, project):
        """Test validation of negative numeric values."""
        data = {
            'project': project.id,
            'title': 'Test Report',
            'description': 'Test',
            'goals_achieved': 'Test',
            'total_volunteers_participated': -1,  # Should be positive
            'total_volunteer_hours': -5,  # Should be positive
            'beneficiaries_count': -10  # Should be positive
        }
        
        serializer = ProjectReportCreateSerializer(
            data=data,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert not serializer.is_valid()
        assert 'total_volunteers_participated' in serializer.errors
        assert 'total_volunteer_hours' in serializer.errors
        assert 'beneficiaries_count' in serializer.errors

    def test_create_report(self, db, organization_user, project):
        """Test creating report through serializer."""
        data = {
            'project': project.id,
            'title': 'New Report',
            'description': 'Project description',
            'goals_achieved': 'All goals achieved',
            'total_volunteers_participated': 15,
            'total_volunteer_hours': 75,
            'beneficiaries_count': 150
        }
        
        serializer = ProjectReportCreateSerializer(
            data=data,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert serializer.is_valid(raise_exception=True)
        
        report = serializer.save()
        assert report.title == 'New Report'
        assert report.project == project
        assert report.status == ReportStatus.DRAFT

    def test_non_organization_cannot_create(self, db, volunteer_user, project):
        """Test that non-organization users cannot create reports."""
        data = {
            'project': project.id,
            'title': 'Test Report',
            'description': 'Test',
            'goals_achieved': 'Test'
        }
        
        serializer = ProjectReportCreateSerializer(
            data=data,
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        
        # Should be valid at serializer level, business logic prevents it
        assert serializer.is_valid()


class TestProjectReportUpdateSerializer:
    """Test ProjectReportUpdateSerializer."""

    def test_organization_update_fields(self, db, project_report, organization_user):
        """Test that organization can update certain fields."""
        data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'goals_achieved': 'Updated goals',
            'challenges_faced': 'Updated challenges',
            'photos': ['new_photo.jpg'],
            'lessons_learned': 'Updated lessons',
            'future_plans': 'Updated plans'
        }
        
        serializer = ProjectReportUpdateSerializer(
            project_report,
            data=data,
            partial=True,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert serializer.is_valid(raise_exception=True)
        
        updated_report = serializer.save()
        assert updated_report.title == 'Updated Title'
        assert updated_report.description == 'Updated description'

    def test_organization_cannot_change_status(self, db, project_report, organization_user):
        """Test that organization cannot change report status directly."""
        data = {'status': ReportStatus.APPROVED}
        
        serializer = ProjectReportUpdateSerializer(
            project_report,
            data=data,
            partial=True,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        
        # Status field should not be available for organizations
        assert 'status' not in serializer.fields

    def test_admin_can_review_report(self, db, project_report, admin_user):
        """Test that admin can review report."""
        data = {
            'status': ReportStatus.APPROVED,
            'review_comment': 'Great report!'
        }
        
        serializer = ProjectReportUpdateSerializer(
            project_report,
            data=data,
            partial=True,
            context={'request': type('Request', (), {'user': admin_user})()}
        )
        assert serializer.is_valid(raise_exception=True)
        
        updated_report = serializer.save()
        assert updated_report.status == ReportStatus.APPROVED
        assert updated_report.review_comment == 'Great report!'
        assert updated_report.reviewed_by == admin_user

    def test_submit_report_action(self, db, project_report, organization_user):
        """Test submitting report for review."""
        # This would typically be a separate action endpoint
        data = {'title': 'Final Report'}
        
        serializer = ProjectReportUpdateSerializer(
            project_report,
            data=data,
            partial=True,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert serializer.is_valid(raise_exception=True)


class TestVolunteerContributionSerializer:
    """Test VolunteerContributionSerializer."""

    def test_contribution_serialization(self, db, volunteer_contribution):
        """Test volunteer contribution serialization."""
        serializer = VolunteerContributionSerializer(volunteer_contribution)
        data = serializer.data
        
        assert data['report'] == volunteer_contribution.report.id
        assert data['volunteer'] == volunteer_contribution.volunteer.id
        assert data['hours_contributed'] == volunteer_contribution.hours_contributed
        assert data['tasks_completed'] == volunteer_contribution.tasks_completed
        assert data['impact_description'] == volunteer_contribution.impact_description
        assert data['performance_rating'] == volunteer_contribution.performance_rating
        assert data['feedback'] == volunteer_contribution.feedback

    def test_contribution_with_rating(self, db, volunteer_contribution):
        """Test serialization with performance rating."""
        volunteer_contribution.performance_rating = 5
        volunteer_contribution.feedback = 'Excellent work!'
        volunteer_contribution.save()
        
        serializer = VolunteerContributionSerializer(volunteer_contribution)
        data = serializer.data
        
        assert data['performance_rating'] == 5
        assert data['feedback'] == 'Excellent work!'

    def test_create_contribution(self, db, project_report, volunteer_user):
        """Test creating contribution through serializer."""
        data = {
            'report': project_report.id,
            'volunteer': volunteer_user.id,
            'hours_contributed': 10,
            'tasks_completed': 'Taught classes',
            'impact_description': 'Great impact',
            'performance_rating': 4,
            'feedback': 'Good work'
        }
        
        serializer = VolunteerContributionSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        
        contribution = serializer.save()
        assert contribution.report == project_report
        assert contribution.volunteer == volunteer_user
        assert contribution.hours_contributed == 10

    def test_invalid_rating_validation(self, db, project_report, volunteer_user):
        """Test invalid performance rating validation."""
        data = {
            'report': project_report.id,
            'volunteer': volunteer_user.id,
            'hours_contributed': 5,
            'tasks_completed': 'Test',
            'performance_rating': 6  # Above max value
        }
        
        serializer = VolunteerContributionSerializer(data=data)
        assert not serializer.is_valid()
        assert 'performance_rating' in serializer.errors

    def test_duplicate_contribution_validation(self, db, project_report, volunteer_user, volunteer_contribution):
        """Test duplicate contribution validation."""
        data = {
            'report': project_report.id,
            'volunteer': volunteer_user.id,
            'hours_contributed': 10,
            'tasks_completed': 'Another task'
        }
        
        serializer = VolunteerContributionSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_hours_contributed_validation(self, db, project_report, volunteer_user):
        """Test hours_contributed validation."""
        data = {
            'report': project_report.id,
            'volunteer': volunteer_user.id,
            'hours_contributed': 0,  # Should be at least 1
            'tasks_completed': 'Test'
        }
        
        serializer = VolunteerContributionSerializer(data=data)
        assert not serializer.is_valid()
        assert 'hours_contributed' in serializer.errors
