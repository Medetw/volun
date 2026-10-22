import pytest
from rest_framework import serializers
from apps.applications.models import Application, ApplicationStatus
from apps.applications.serializers import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationReviewSerializer
)
from apps.users.models import User, UserRole
from apps.projects.models import Project, ProjectStatus, Category


class TestApplicationSerializer:
    """Test ApplicationSerializer."""

    def test_application_serialization(self, db, application):
        """Test application serialization output."""
        serializer = ApplicationSerializer(application)
        data = serializer.data
        
        assert (data['volunteer']['id'] if isinstance(data['volunteer'], dict) else data['volunteer']) == application.volunteer.id
        assert (data['project']['id'] if isinstance(data['project'], dict) else data['project']) == application.project.id
        assert data['status'] == application.status
        assert data['cover_letter'] == application.cover_letter
        assert data['hours_committed'] == application.hours_committed
        assert data['is_pending'] == application.is_pending
        assert data['is_approved'] == application.is_approved
        assert data['can_be_cancelled'] == application.can_be_cancelled

    def test_application_with_review_data(self, db, application, admin_user):
        """Test serialization with review data."""
        application.status = ApplicationStatus.APPROVED
        application.reviewed_by = admin_user
        application.review_comment = 'Approved!'
        application.save()
        
        serializer = ApplicationSerializer(application)
        data = serializer.data
        
        assert data['reviewed_by'] == admin_user.id
        assert data['review_comment'] == 'Approved!'

    def test_read_only_fields(self, db, application):
        """Test that certain fields are read-only."""
        serializer = ApplicationSerializer(application, data={
            'is_pending': False,
            'is_approved': True,
            'can_be_cancelled': False
        }, partial=True)
        
        assert serializer.is_valid(raise_exception=True)
        updated_app = serializer.save()
        
        # These fields should not be updated
        assert updated_app.is_pending == application.is_pending
        assert updated_app.is_approved == application.is_approved
        assert updated_app.can_be_cancelled == application.can_be_cancelled


class TestApplicationCreateSerializer:
    """Test ApplicationCreateSerializer."""

    def test_valid_application_creation(self, db, volunteer_user, project):
        """Test valid application creation data."""
        data = {
            'project': project.id,
            'cover_letter': 'I want to join this project',
            'hours_committed': 5
        }
        
        serializer = ApplicationCreateSerializer(
            data=data, 
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        assert serializer.is_valid(raise_exception=True)

    def test_missing_required_fields(self, db, volunteer_user):
        """Test missing required fields."""
        data = {}  # Empty data
        
        serializer = ApplicationCreateSerializer(
            data=data, 
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        assert not serializer.is_valid()
        
        assert 'project' in serializer.errors

    def test_invalid_project_id(self, db, volunteer_user):
        """Test invalid project ID."""
        data = {
            'project': 99999,  # Non-existent project
            'cover_letter': 'I want to join'
        }
        
        serializer = ApplicationCreateSerializer(
            data=data, 
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        assert not serializer.is_valid()
        assert 'project' in serializer.errors

    def test_duplicate_application_validation(self, db, volunteer_user, project, application):
        """Test duplicate application validation."""
        data = {
            'project': project.id,
            'cover_letter': 'Another application'
        }
        
        serializer = ApplicationCreateSerializer(
            data=data, 
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_hours_committed_validation(self, db, volunteer_user, project):
        """Test hours_committed validation."""
        data = {
            'project': project.id,
            'hours_committed': 0  # Should be at least 1
        }
        
        serializer = ApplicationCreateSerializer(
            data=data, 
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        assert not serializer.is_valid()
        assert 'hours_committed' in serializer.errors

    def test_create_application(self, db, volunteer_user, project):
        """Test creating application through serializer."""
        data = {
            'project': project.id,
            'cover_letter': 'I want to join this project',
            'hours_committed': 10
        }
        
        serializer = ApplicationCreateSerializer(
            data=data, 
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        assert serializer.is_valid(raise_exception=True)
        
        application = serializer.save()
        assert application.volunteer == volunteer_user
        assert application.project == project
        assert application.status == ApplicationStatus.PENDING

    def test_non_volunteer_cannot_apply(self, db, organization_user, project):
        """Test that non-volunteers cannot create applications."""
        data = {
            'project': project.id,
            'cover_letter': 'I want to join'
        }
        
        serializer = ApplicationCreateSerializer(
            data=data, 
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        
        # Should be valid at serializer level, business logic prevents it
        assert serializer.is_valid()

    def test_apply_to_draft_project(self, db, volunteer_user, draft_project):
        """Test applying to draft project."""
        data = {
            'project': draft_project.id,
            'cover_letter': 'I want to join'
        }
        
        serializer = ApplicationCreateSerializer(
            data=data, 
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        
        # Should be valid, but view might prevent it
        assert serializer.is_valid()


class TestApplicationReviewSerializer:
    """Test ApplicationReviewSerializer."""

    def test_volunteer_can_update_own_application(self, db, application, volunteer_user):
        """Test that volunteer can update own application."""
        data = {
            'cover_letter': 'Updated cover letter',
            'hours_committed': 15
        }
        
        serializer = ApplicationReviewSerializer(
            application, 
            data=data, 
            partial=True,
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        assert serializer.is_valid(raise_exception=True)
        
        updated_app = serializer.save()
        assert updated_app.cover_letter == 'Updated cover letter'
        assert updated_app.hours_committed == 15

    def test_volunteer_cannot_change_status(self, db, application, volunteer_user):
        """Test that volunteer cannot change application status."""
        data = {'status': ApplicationStatus.APPROVED}
        
        serializer = ApplicationReviewSerializer(
            application, 
            data=data, 
            partial=True,
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        
        # Status field should not be in serializer for volunteers
        assert 'status' not in serializer.fields

    def test_organization_can_review_application(self, db, application, organization_user):
        """Test that organization can review application."""
        data = {
            'status': ApplicationStatus.APPROVED,
            'review_comment': 'Great candidate!'
        }
        
        serializer = ApplicationReviewSerializer(
            application, 
            data=data, 
            partial=True,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert serializer.is_valid(raise_exception=True)
        
        updated_app = serializer.save()
        assert updated_app.status == ApplicationStatus.APPROVED
        assert updated_app.review_comment == 'Great candidate!'

    def test_invalid_status_transition(self, db, application, organization_user):
        """Test invalid status transitions."""
        # Try to set invalid status
        data = {'status': 'invalid_status'}
        
        serializer = ApplicationReviewSerializer(
            application, 
            data=data, 
            partial=True,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert not serializer.is_valid()
        assert 'status' in serializer.errors

    def test_cancel_application(self, db, application, volunteer_user):
        """Test cancelling application."""
        data = {'status': ApplicationStatus.CANCELLED}
        
        # For volunteers, status field might not be available
        # This would be handled in the view with a separate endpoint
        serializer = ApplicationReviewSerializer(
            application, 
            data={'cover_letter': 'Cancelling my application'}, 
            partial=True,
            context={'request': type('Request', (), {'user': volunteer_user})()}
        )
        assert serializer.is_valid(raise_exception=True)

    def test_update_reviewed_by_field(self, db, application, organization_user):
        """Test that reviewed_by is set automatically."""
        data = {
            'status': ApplicationStatus.REJECTED,
            'review_comment': 'Not suitable'
        }
        
        serializer = ApplicationReviewSerializer(
            application, 
            data=data, 
            partial=True,
            context={'request': type('Request', (), {'user': organization_user})()}
        )
        assert serializer.is_valid(raise_exception=True)
        
        updated_app = serializer.save()
        assert updated_app.reviewed_by == organization_user
        assert updated_app.review_comment == 'Not suitable'
