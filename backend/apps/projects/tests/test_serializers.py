import pytest
from rest_framework import serializers
from apps.projects.models import Project, ProjectFormat, ProjectStatus, Category, Region
from apps.projects.serializers import (
    ProjectDetailSerializer, 
    ProjectCreateUpdateSerializer,
    ProjectCreateUpdateSerializer,
    CategorySerializer,
    RegionSerializer
)
from apps.users.models import User, UserRole


class TestProjectDetailSerializer:
    """Test ProjectDetailSerializer."""

    def test_project_serialization(self, db, project):
        """Test project serialization output."""
        serializer = ProjectDetailSerializer(project)
        data = serializer.data
        
        assert data['title'] == project.title
        assert data['description'] == project.description
        assert data['format'] == project.format
        assert data['status'] == project.status
        assert data['volunteers_needed'] == project.volunteers_needed
        assert data['is_active'] is True
        assert data['volunteers_count'] == 0
        assert data['volunteers_remaining'] == project.volunteers_needed
        assert 'category' in data
        assert 'organization' in data

    def test_project_with_applications_serialization(self, db, project, approved_application):
        """Test project serialization with applications."""
        serializer = ProjectDetailSerializer(project)
        data = serializer.data
        
        assert data['volunteers_count'] == 1
        assert data['volunteers_remaining'] == project.volunteers_needed - 1

    def test_project_read_only_fields(self, db, project):
        """Test that certain fields are read-only."""
        serializer = ProjectDetailSerializer(project, data={
            'volunteers_count': 999,
            'volunteers_remaining': 999,
            'is_active': False
        }, partial=True)
        
        assert serializer.is_valid(raise_exception=True)
        updated_project = serializer.save()
        
        # These fields should not be updated
        assert updated_project.volunteers_count == 1  # Based on applications
        assert updated_project.volunteers_remaining == project.volunteers_needed - 1
        assert updated_project.is_active == True  # Based on status


class TestProjectCreateUpdateSerializer:
    """Test ProjectCreateUpdateSerializer."""

    def test_valid_project_creation(self, db, organization_user, category, region):
        """Test valid project creation data."""
        data = {
            'title': 'New Project',
            'description': 'Project description',
            'category': category.id,
            'format': ProjectFormat.ONLINE,
            'region': region.id,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'volunteers_needed': 15,
            'requirements': 'Some requirements',
            'contact_info': {'phone': '+123456789', 'email': 'contact@example.com'}
        }
        
        serializer = ProjectCreateUpdateSerializer(data=data, context={'request': type('Request', (), {'user': organization_user})()})
        assert serializer.is_valid(raise_exception=True)

    def test_missing_required_fields(self, db, organization_user):
        """Test missing required fields."""
        data = {}  # Empty data
        
        serializer = ProjectCreateUpdateSerializer(data=data, context={'request': type('Request', (), {'user': organization_user})()})
        assert not serializer.is_valid()
        
        required_fields = ['title', 'description', 'category', 'volunteers_needed']
        for field in required_fields:
            assert field in serializer.errors

    def test_invalid_volunteers_needed(self, db, organization_user, category):
        """Test invalid volunteers_needed value."""
        data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': category.id,
            'volunteers_needed': 0  # Should be at least 1
        }
        
        serializer = ProjectCreateUpdateSerializer(data=data, context={'request': type('Request', (), {'user': organization_user})()})
        assert not serializer.is_valid()
        assert 'volunteers_needed' in serializer.errors

    def test_invalid_date_range(self, db, organization_user, category):
        """Test invalid date range."""
        data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': category.id,
            'volunteers_needed': 5,
            'start_date': '2024-12-31',
            'end_date': '2024-01-01'  # End before start
        }
        
        serializer = ProjectCreateUpdateSerializer(data=data, context={'request': type('Request', (), {'user': organization_user})()})
        assert not serializer.is_valid()
        assert 'end_date' in serializer.errors

    def test_invalid_format(self, db, organization_user, category):
        """Test invalid project format."""
        data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': category.id,
            'volunteers_needed': 5,
            'format': 'invalid_format'
        }
        
        serializer = ProjectCreateUpdateSerializer(data=data, context={'request': type('Request', (), {'user': organization_user})()})
        assert not serializer.is_valid()
        assert 'format' in serializer.errors

    def test_create_project(self, db, organization_user, category, region):
        """Test creating project through serializer."""
        data = {
            'title': 'New Project',
            'description': 'Project description',
            'category': category.id,
            'format': ProjectFormat.HYBRID,
            'region': region.id,
            'volunteers_needed': 10
        }
        
        serializer = ProjectCreateUpdateSerializer(data=data, context={'request': type('Request', (), {'user': organization_user})()})
        assert serializer.is_valid(raise_exception=True)
        
        project = serializer.save()
        assert project.title == 'New Project'
        assert project.organization == organization_user
        assert project.status == ProjectStatus.DRAFT  # Default status

    def test_non_organization_user_cannot_create(self, db, volunteer_user, category):
        """Test that non-organization users cannot create projects."""
        data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': category.id,
            'volunteers_needed': 5
        }
        
        serializer = ProjectCreateUpdateSerializer(data=data, context={'request': type('Request', (), {'user': volunteer_user})()})
        
        # Serializer should be valid but business logic should prevent creation
        assert serializer.is_valid()
        
        # This would be handled in the view/permission layer
        with pytest.raises(Exception):
            serializer.save()


class TestProjectCreateUpdateSerializer:
    """Test ProjectCreateUpdateSerializer."""

    def test_partial_update(self, db, project, organization_user):
        """Test partial project update."""
        data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        serializer = ProjectCreateUpdateSerializer(project, data=data, partial=True)
        assert serializer.is_valid(raise_exception=True)
        
        updated_project = serializer.save()
        assert updated_project.title == 'Updated Title'
        assert updated_project.description == 'Updated description'

    def test_update_status(self, db, project, organization_user):
        """Test updating project status."""
        data = {'status': ProjectStatus.ACTIVE}
        
        serializer = ProjectCreateUpdateSerializer(project, data=data, partial=True)
        assert serializer.is_valid(raise_exception=True)
        
        updated_project = serializer.save()
        assert updated_project.status == ProjectStatus.ACTIVE

    def test_update_organization_forbidden(self, db, project, organization_user):
        """Test that organization cannot be changed."""
        other_org = User.objects.create_user(
            username='otherorg',
            email='other@example.com',
            password='testpass123',
            role=UserRole.ORGANIZATION
        )
        
        data = {'organization': other_org.id}
        
        serializer = ProjectCreateUpdateSerializer(project, data=data, partial=True)
        # Organization field should be read-only
        assert 'organization' not in serializer.fields


class TestCategorySerializer:
    """Test CategorySerializer."""

    def test_category_serialization(self, db, category):
        """Test category serialization."""
        serializer = CategorySerializer(category)
        data = serializer.data
        
        assert data['name'] == category.name
        assert data['description'] == category.description

    def test_create_category(self, db):
        """Test creating category through serializer."""
        data = {
            'name': 'New Category',
            'description': 'New category description'
        }
        
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        
        category = serializer.save()
        assert category.name == 'New Category'
        assert category.description == 'New category description'

    def test_duplicate_category_name(self, db, category):
        """Test duplicate category name validation."""
        data = {
            'name': category.name,  # Same name
            'description': 'Different description'
        }
        
        serializer = CategorySerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors


class TestRegionSerializer:
    """Test RegionSerializer."""

    def test_region_serialization(self, db, region):
        """Test region serialization."""
        serializer = RegionSerializer(region)
        data = serializer.data
        
        assert data['name'] == region.name
        assert data['code'] == region.code

    def test_create_region(self, db):
        """Test creating region through serializer."""
        data = {
            'name': 'New Region',
            'code': 'NR'
        }
        
        serializer = RegionSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        
        region = serializer.save()
        assert region.name == 'New Region'
        assert region.code == 'NR'

    def test_duplicate_region_name(self, db, region):
        """Test duplicate region name validation."""
        data = {
            'name': region.name,  # Same name
            'code': 'DIFF'
        }
        
        serializer = RegionSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
