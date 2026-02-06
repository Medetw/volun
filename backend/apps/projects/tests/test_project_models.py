import pytest
from apps.projects.models import Category, Region, Project, ProjectFormat, ProjectStatus
from apps.users.models import User, UserRole


class TestCategoryModel:
    """Test Category model."""

    def test_create_category(self, db):
        """Test creating a category."""
        category = Category.objects.create(
            name='Education',
            description='Education related projects'
        )
        assert category.name == 'Education'
        assert category.description == 'Education related projects'
        assert str(category) == 'Education'

    def test_category_ordering(self, db):
        """Test category ordering."""
        Category.objects.create(name='Healthcare')
        Category.objects.create(name='Education')
        Category.objects.create(name='Environment')
        
        categories = list(Category.objects.all())
        assert categories[0].name == 'Education'
        assert categories[1].name == 'Environment'
        assert categories[2].name == 'Healthcare'

    def test_category_unique_name(self, db):
        """Test category name uniqueness."""
        Category.objects.create(name='Education')
        
        with pytest.raises(Exception):
            Category.objects.create(name='Education')

    def test_category_verbose_name_plural(self, db):
        """Test category verbose name plural."""
        assert Category._meta.verbose_name_plural == 'Categories'


class TestRegionModel:
    """Test Region model."""

    def test_create_region(self, db):
        """Test creating a region."""
        region = Region.objects.create(
            name='Almaty',
            code='ALM'
        )
        assert region.name == 'Almaty'
        assert region.code == 'ALM'
        assert str(region) == 'Almaty'

    def test_region_ordering(self, db):
        """Test region ordering."""
        Region.objects.create(name='Zhambyl')
        Region.objects.create(name='Almaty')
        Region.objects.create(name='Shymkent')
        
        regions = list(Region.objects.all())
        assert regions[0].name == 'Almaty'
        assert regions[1].name == 'Shymkent'
        assert regions[2].name == 'Zhambyl'

    def test_region_unique_name(self, db):
        """Test region name uniqueness."""
        Region.objects.create(name='Almaty')
        
        with pytest.raises(Exception):
            Region.objects.create(name='Almaty')

    def test_region_default_code(self, db):
        """Test region default code is empty."""
        region = Region.objects.create(name='Test Region')
        assert region.code == ''


class TestProjectModel:
    """Test Project model."""

    def test_create_project(self, db):
        """Test creating a project."""
        user = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        category = Category.objects.create(name='Education')
        region = Region.objects.create(name='Almaty')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test project description',
            category=category,
            organization=user,
            region=region,
            volunteers_needed=10,
            status=ProjectStatus.ACTIVE
        )
        
        assert project.title == 'Test Project'
        assert project.description == 'Test project description'
        assert project.category == category
        assert project.organization == user
        assert project.region == region
        assert project.volunteers_needed == 10
        assert project.status == ProjectStatus.ACTIVE
        assert str(project) == 'Test Project (org1)'

    def test_project_default_values(self, db):
        """Test project default values."""
        user = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test project description',
            category=category,
            organization=user
        )
        
        assert project.format == ProjectFormat.OFFLINE
        assert project.status == ProjectStatus.DRAFT
        assert project.volunteers_needed == 1
        assert project.region is None
        assert project.start_date is None
        assert project.end_date is None

    def test_project_is_active_property(self, db):
        """Test project is_active property."""
        user = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        category = Category.objects.create(name='Education')
        
        active_project = Project.objects.create(
            title='Active Project',
            description='Test',
            category=category,
            organization=user,
            status=ProjectStatus.ACTIVE
        )
        assert active_project.is_active is True
        
        draft_project = Project.objects.create(
            title='Draft Project',
            description='Test',
            category=category,
            organization=user,
            status=ProjectStatus.DRAFT
        )
        assert draft_project.is_active is False
        
        completed_project = Project.objects.create(
            title='Completed Project',
            description='Test',
            category=category,
            organization=user,
            status=ProjectStatus.COMPLETED
        )
        assert completed_project.is_active is False

    def test_project_volunteers_count_property(self, db):
        """Test project volunteers_count property."""
        user = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=user,
            volunteers_needed=5,
            status=ProjectStatus.ACTIVE
        )
        
        # Initially no volunteers
        assert project.volunteers_count == 0
        
        # Create approved application
        from apps.applications.models import Application, ApplicationStatus
        
        Application.objects.create(
            volunteer=volunteer,
            project=project,
            status=ApplicationStatus.APPROVED
        )
        assert project.volunteers_count == 1  # Now 1 approved

    def test_project_volunteers_remaining_property(self, db):
        """Test project volunteers_remaining property."""
        user = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        category = Category.objects.create(name='Education')
        
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=user,
            volunteers_needed=5,
            status=ProjectStatus.ACTIVE
        )
        
        # Initially all slots available
        assert project.volunteers_remaining == 5
        
        # Create approved application
        from apps.applications.models import Application, ApplicationStatus
        
        Application.objects.create(
            volunteer=volunteer,
            project=project,
            status=ApplicationStatus.APPROVED
        )
        assert project.volunteers_remaining == 4  # One slot taken

    def test_project_ordering(self, db):
        """Test project ordering."""
        user = User.objects.create_user(
            username='org1',
            email='org@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        category = Category.objects.create(name='Education')
        
        project1 = Project.objects.create(
            title='Old Project',
            description='Test',
            category=category,
            organization=user
        )
        
        project2 = Project.objects.create(
            title='New Project',
            description='Test',
            category=category,
            organization=user
        )
        
        projects = list(Project.objects.all())
        assert projects[0] == project2  # New project first (descending by created_at)

    def test_project_indexes(self, db):
        """Test project indexes are defined."""
        indexes = Project._meta.indexes
        assert len(indexes) == 3
        
        # Check index fields
        index_fields = [index.fields for index in indexes]
        assert ['status', 'category'] in index_fields
        assert ['organization', 'status'] in index_fields
        assert ['region', 'status'] in index_fields

    def test_project_organization_role_constraint(self, db):
        """Test that only organizations can create projects."""
        volunteer = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='testpass123',
            role=UserRole.VOLUNTEER
        )
        category = Category.objects.create(name='Education')
        
        # This should work at model level (constraint is at admin/form level)
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category=category,
            organization=volunteer
        )
        assert project.organization == volunteer

    def test_project_format_choices(self, db):
        """Test project format choices."""
        assert ProjectFormat.ONLINE == 'online'
        assert ProjectFormat.OFFLINE == 'offline'
        assert ProjectFormat.HYBRID == 'hybrid'
        
        choices = ProjectFormat.choices
        assert len(choices) == 3
        assert ('online', 'Online') in choices

    def test_project_status_choices(self, db):
        """Test project status choices."""
        assert ProjectStatus.DRAFT == 'draft'
        assert ProjectStatus.ACTIVE == 'active'
        assert ProjectStatus.COMPLETED == 'completed'
        assert ProjectStatus.CANCELLED == 'cancelled'
        
        choices = ProjectStatus.choices
        assert len(choices) == 4
        assert ('draft', 'Draft') in choices
