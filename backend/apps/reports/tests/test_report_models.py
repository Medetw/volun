import pytest
from apps.reports.models import ProjectReport, ReportStatus, VolunteerContribution
from apps.users.models import User, UserRole
from apps.projects.models import Project, Category


class TestProjectReportModel:
    """Test ProjectReport model."""

    def test_create_project_report(self, db):
        """Test creating a project report."""
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
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Project completed successfully',
            goals_achieved='All goals achieved',
            total_volunteers_participated=10,
            total_volunteer_hours=50,
            beneficiaries_count=100
        )
        
        assert report.project == project
        assert report.title == 'Project Report'
        assert report.description == 'Project completed successfully'
        assert report.goals_achieved == 'All goals achieved'
        assert report.total_volunteers_participated == 10
        assert report.total_volunteer_hours == 50
        assert report.beneficiaries_count == 100
        assert report.status == ReportStatus.DRAFT
        assert str(report) == f'Отчет: {report.title} ({project.title})'

    def test_report_default_values(self, db):
        """Test report default values."""
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
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test description',
            goals_achieved='Test goals'
        )
        
        assert report.challenges_faced == ''
        assert report.photos == []
        assert report.lessons_learned == ''
        assert report.future_plans == ''
        assert report.status == ReportStatus.DRAFT
        assert report.reviewed_by is None
        assert report.review_comment == ''
        assert report.submitted_at is None
        assert report.reviewed_at is None

    def test_report_one_to_one_with_project(self, db):
        """Test one-to-one relationship with project."""
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
        
        report = ProjectReport.objects.create(
            project=project,
            title='Report 1',
            description='Test'
        )
        
        # Should be able to access report from project
        assert project.report == report
        
        # Should not be able to create second report for same project
        with pytest.raises(Exception):
            ProjectReport.objects.create(
                project=project,
                title='Report 2',
                description='Test'
            )

    def test_report_status_properties(self, db):
        """Test report status properties."""
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
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test',
            goals_achieved='Test'
        )
        
        # Test draft
        assert report.is_submitted is False
        assert report.is_approved is False
        
        # Test submitted
        report.status = ReportStatus.SUBMITTED
        report.save()
        assert report.is_submitted is True
        assert report.is_approved is False
        
        # Test approved
        report.status = ReportStatus.APPROVED
        report.save()
        assert report.is_submitted is False  # Approved is not submitted
        assert report.is_approved is True

    def test_submit_report(self, db):
        """Test submitting report for review."""
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
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test',
            goals_achieved='Test'
        )
        
        # Initially draft
        assert report.status == ReportStatus.DRAFT
        assert report.submitted_at is None
        
        # Submit report
        report.submit()
        
        report.refresh_from_db()
        assert report.status == ReportStatus.SUBMITTED
        assert report.submitted_at is not None

    def test_approve_report(self, db):
        """Test approving report."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role=UserRole.ADMIN
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test',
            goals_achieved='Test',
            status=ReportStatus.SUBMITTED
        )
        
        # Approve report
        report.approve(admin_user, 'Great report!')
        
        report.refresh_from_db()
        assert report.status == ReportStatus.APPROVED
        assert report.reviewed_by == admin_user
        assert report.review_comment == 'Great report!'
        assert report.reviewed_at is not None

    def test_reject_report(self, db):
        """Test rejecting report."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role=UserRole.ADMIN
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test',
            goals_achieved='Test',
            status=ReportStatus.SUBMITTED
        )
        
        # Reject report
        report.reject(admin_user, 'Needs more details')
        
        report.refresh_from_db()
        assert report.status == ReportStatus.REJECTED
        assert report.reviewed_by == admin_user
        assert report.review_comment == 'Needs more details'
        assert report.reviewed_at is not None

    def test_report_status_choices(self, db):
        """Test report status choices."""
        assert ReportStatus.DRAFT == 'draft'
        assert ReportStatus.SUBMITTED == 'submitted'
        assert ReportStatus.APPROVED == 'approved'
        assert ReportStatus.REJECTED == 'rejected'
        
        choices = ReportStatus.choices
        assert len(choices) == 4
        assert ('draft', 'Черновик') in choices
        assert ('submitted', 'Отправлен') in choices
        assert ('approved', 'Одобрен') in choices
        assert ('rejected', 'Отклонен') in choices

    def test_json_fields(self, db):
        """Test JSON field handling."""
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
        
        report = ProjectReport.objects.create(
            project=project,
            title='Test Report',
            description='Test',
            goals_achieved='Test',
            photos=['photo1.jpg', 'photo2.jpg']
        )
        
        assert report.photos == ['photo1.jpg', 'photo2.jpg']
        
        # Update JSON field
        report.photos = ['photo3.jpg']
        report.save()
        assert report.photos == ['photo3.jpg']

    def test_report_ordering(self, db):
        """Test report ordering."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        category = Category.objects.create(name='Education')
        
        project1 = Project.objects.create(
            title='Project 1',
            description='Test',
            category=category,
            organization=organization
        )
        
        project2 = Project.objects.create(
            title='Project 2',
            description='Test',
            category=category,
            organization=organization
        )
        
        report1 = ProjectReport.objects.create(
            project=project1,
            title='Report 1',
            description='Test'
        )
        
        report2 = ProjectReport.objects.create(
            project=project2,
            title='Report 2',
            description='Test'
        )
        
        reports = list(ProjectReport.objects.all())
        assert reports[0] == report2  # Most recent first
        assert reports[1] == report1

    def test_report_indexes(self, db):
        """Test report indexes."""
        indexes = ProjectReport._meta.indexes
        assert len(indexes) == 2
        
        index_fields = [index.fields for index in indexes]
        assert ['project', 'status'] in index_fields
        assert ['status', 'submitted_at'] in index_fields


class TestVolunteerContributionModel:
    """Test VolunteerContribution model."""

    def test_create_volunteer_contribution(self, db):
        """Test creating volunteer contribution."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Test',
            goals_achieved='Test'
        )
        
        contribution = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer,
            hours_contributed=10,
            tasks_completed='Taught classes',
            impact_description='Great impact'
        )
        
        assert contribution.report == report
        assert contribution.volunteer == volunteer
        assert contribution.hours_contributed == 10
        assert contribution.tasks_completed == 'Taught classes'
        assert contribution.impact_description == 'Great impact'
        assert str(contribution) == f'{volunteer.username} - {contribution.hours_contributed}ч в {report.project.title}'

    def test_contribution_default_values(self, db):
        """Test contribution default values."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Test',
            goals_achieved='Test'
        )
        
        contribution = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer,
            hours_contributed=5,
            tasks_completed='Test tasks'
        )
        
        assert contribution.performance_rating is None
        assert contribution.feedback == ''

    def test_contribution_with_rating(self, db):
        """Test contribution with performance rating."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Test',
            goals_achieved='Test'
        )
        
        contribution = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer,
            hours_contributed=8,
            tasks_completed='Test tasks',
            performance_rating=5,
            feedback='Excellent work!'
        )
        
        assert contribution.performance_rating == 5
        assert contribution.feedback == 'Excellent work!'

    def test_contribution_unique_constraint(self, db):
        """Test unique constraint on report + volunteer."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Test',
            goals_achieved='Test'
        )
        
        VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer,
            hours_contributed=5,
            tasks_completed='Test'
        )
        
        # Should not be able to create second contribution for same report+volunteer
        with pytest.raises(Exception):
            VolunteerContribution.objects.create(
                report=report,
                volunteer=volunteer,
                hours_contributed=10
            )

    def test_contribution_different_volunteers_same_report(self, db):
        """Test that different volunteers can contribute to same report."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer1 = User.objects.create_user(
            username='volunteer1',
            email='volunteer1@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        volunteer2 = User.objects.create_user(
            username='volunteer2',
            email='volunteer2@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Test',
            goals_achieved='Test'
        )
        
        contrib1 = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer1,
            hours_contributed=5,
            tasks_completed='Test tasks 1'
        )
        
        contrib2 = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer2,
            hours_contributed=8,
            tasks_completed='Test tasks 2'
        )
        
        assert contrib1.volunteer != contrib2.volunteer
        assert contrib1.report == contrib2.report

    def test_contribution_ordering(self, db):
        """Test contribution ordering."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer1 = User.objects.create_user(
            username='volunteer1',
            email='volunteer1@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        volunteer2 = User.objects.create_user(
            username='volunteer2',
            email='volunteer2@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Test',
            goals_achieved='Test'
        )
        
        contrib1 = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer1,
            hours_contributed=5,
            tasks_completed='Test tasks 1'
        )
        
        contrib2 = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer2,
            hours_contributed=10,
            tasks_completed='Test tasks 2'
        )
        
        contributions = list(VolunteerContribution.objects.all())
        assert contributions[0] == contrib2  # Most hours first
        assert contributions[1] == contrib1

    def test_hours_contributed_validation(self, db):
        """Test hours_contributed validation."""
        organization = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='test_pass123',
            role=UserRole.VOLUNTEER
        )
        
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=category,
            organization=organization
        )
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Test',
            goals_achieved='Test'
        )
        
        # Test minimum value
        contribution = VolunteerContribution.objects.create(
            report=report,
            volunteer=volunteer,
            hours_contributed=1
        )
        assert contribution.hours_contributed == 1

    def test_performance_rating_validation(self, db):
        """Test performance rating validation."""
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
        
        report = ProjectReport.objects.create(
            project=project,
            title='Project Report',
            description='Test',
            goals_achieved='Test',
            status=ReportStatus.SUBMITTED
        )
        
        # Valid ratings
        for rating in [1, 2, 3, 4, 5]:
            contribution = VolunteerContribution.objects.create(
                report=report,
                volunteer=User.objects.create_user(
                    username=f'volunteer{rating}',
                    email=f'volunteer{rating}@example.com',
                    password='testpass123',
                    role=UserRole.VOLUNTEER
                ),
                hours_contributed=5,
                tasks_completed='Test',
                performance_rating=rating
            )
            assert contribution.performance_rating == rating
