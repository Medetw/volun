import pytest
from apps.applications.models import Application, ApplicationStatus
from apps.users.models import User, UserRole
from apps.projects.models import Project, Category


class TestApplicationModel:
    """Test Application model."""

    def test_create_application(self, db):
        """Test creating an application."""
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization,
            volunteers_needed=5,
            status='active'
        )
        
        application = Application.objects.create(
            volunteer=volunteer,
            project=project,
            cover_letter='I want to join this project',
            hours_committed=10
        )
        
        assert application.volunteer == volunteer
        assert application.project == project
        assert application.status == ApplicationStatus.PENDING
        assert application.cover_letter == 'I want to join this project'
        assert application.hours_committed == 10
        assert str(application) == f'Application({volunteer.username} → {project.title})'

    def test_application_default_values(self, db):
        """Test application default values."""
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        application = Application.objects.create(
            volunteer=volunteer,
            project=project
        )
        
        assert application.status == ApplicationStatus.PENDING
        assert application.cover_letter == ''
        assert application.hours_committed == 1
        assert application.reviewed_at is None
        assert application.reviewed_by is None
        assert application.review_comment == ''

    def test_application_unique_constraint(self, db):
        """Test unique constraint on volunteer + project."""
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        Application.objects.create(
            volunteer=volunteer,
            project=project
        )
        
        # Should not be able to create second application
        with pytest.raises(Exception):
            Application.objects.create(
                volunteer=volunteer,
                project=project
            )

    def test_application_different_volunteers_same_project(self, db):
        """Test that different volunteers can apply to same project."""
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
        
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        app1 = Application.objects.create(
            volunteer=volunteer1,
            project=project
        )
        
        app2 = Application.objects.create(
            volunteer=volunteer2,
            project=project
        )
        
        assert app1.volunteer != app2.volunteer
        assert app1.project == app2.project

    def test_application_same_volunteer_different_projects(self, db):
        """Test that volunteer can apply to different projects."""
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project1 = Project.objects.create(
            title='Test Project 1',
            description='Test description',
            category=category,
            organization=organization
        )
        
        project2 = Project.objects.create(
            title='Test Project 2',
            description='Test description',
            category=category,
            organization=organization
        )
        
        app1 = Application.objects.create(
            volunteer=volunteer,
            project=project1
        )
        
        app2 = Application.objects.create(
            volunteer=volunteer,
            project=project2
        )
        
        assert app1.volunteer == app2.volunteer
        assert app1.project != app2.project

    def test_application_status_properties(self, db):
        """Test application status properties."""
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        application = Application.objects.create(
            volunteer=volunteer,
            project=project
        )
        
        # Test pending
        assert application.is_pending is True
        assert application.is_approved is False
        assert application.can_be_cancelled is True
        
        # Test approved
        application.status = ApplicationStatus.APPROVED
        application.save()
        assert application.is_pending is False
        assert application.is_approved is True
        assert application.can_be_cancelled is True
        
        # Test rejected
        application.status = ApplicationStatus.REJECTED
        application.save()
        assert application.is_pending is False
        assert application.is_approved is False
        assert application.can_be_cancelled is False

    def test_application_status_choices(self, db):
        """Test application status choices."""
        assert ApplicationStatus.PENDING == 'pending'
        assert ApplicationStatus.APPROVED == 'approved'
        assert ApplicationStatus.REJECTED == 'rejected'
        assert ApplicationStatus.CANCELLED == 'cancelled'
        
        choices = ApplicationStatus.choices
        assert len(choices) == 4
        assert ('pending', 'Ожидает рассмотрения') in choices
        assert ('approved', 'Принята') in choices
        assert ('rejected', 'Отклонена') in choices
        assert ('cancelled', 'Отменена') in choices

    def test_application_ordering(self, db):
        """Test application ordering."""
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
        
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project1 = Project.objects.create(
            title='Test Project 1',
            description='Test',
            category=category,
            organization=organization
        )
        
        project2 = Project.objects.create(
            title='Test Project 2',
            description='Test',
            category=category,
            organization=organization
        )
        
        app1 = Application.objects.create(
            volunteer=volunteer1,
            project=project1
        )
        
        app2 = Application.objects.create(
            volunteer=volunteer2,
            project=project2
        )
        
        applications = list(Application.objects.all())
        assert applications[0] == app2  # Most recent first
        assert applications[1] == app1

    def test_application_indexes(self, db):
        """Test application indexes."""
        indexes = Application._meta.indexes
        assert len(indexes) == 3
        
        index_fields = [index.fields for index in indexes]
        assert ['volunteer', 'status'] in index_fields
        assert ['project', 'status'] in index_fields
        assert ['status', 'created_at'] in index_fields

    def test_hours_committed_validation(self, db):
        """Test hours_committed validation."""
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        # Test minimum value
        application = Application.objects.create(
            volunteer=volunteer,
            project=project,
            hours_committed=1
        )
        assert application.hours_committed == 1
        
        # Note: MinValueValidator works at form/serializer level, not model level
        # The database accepts 0, but forms should validate
        application2 = Application.objects.create(
            volunteer=User.objects.create_user(
                username='volunteer2',
                email='volunteer2@example.com',
                password='testpass123',
                role=UserRole.VOLUNTEER
            ),
            project=Project.objects.create(
                title='Test Project 2',
                description='Test',
                category=Category.objects.create(name='Test'),
                organization=organization
            ),
            hours_committed=0  # Database accepts this
        )
        assert application2.hours_committed == 0
