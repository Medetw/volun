from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from apps.projects.models import Project, Category, Region
from apps.projects.serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
    CategorySerializer,
    RegionSerializer,
)
from apps.projects.permissions import IsOrganizationOrReadOnly, IsProjectOwnerOrReadOnly


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing categories (read-only)."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None  # No pagination for categories


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing regions (read-only)."""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # No pagination for regions


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for projects.
    
    - List: Public access, filtered by status, category, region, format
    - Retrieve: Public access
    - Create: Only for organizations
    - Update/Delete: Only for project owner
    """
    queryset = Project.objects.select_related('category', 'region', 'organization').all()
    permission_classes = [IsOrganizationOrReadOnly, IsProjectOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'region', 'format']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'start_date', 'volunteers_needed']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action in ['list']:
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by status (default: show active and draft for public, all for owner)
        status_filter = self.request.query_params.get('status')
        if not status_filter:
            # For unauthenticated users, show only active projects
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(status='active')
            # For authenticated users, show active and draft
            elif self.request.user.role != 'organization':
                queryset = queryset.filter(status__in=['active', 'draft'])
            # For organizations, show all their projects + active others
            else:
                # Show all projects, but we'll filter in list action
                pass
        
        # Filter by organization (for organizations to see their projects)
        if self.request.user.is_authenticated and self.request.user.role == 'organization':
            my_projects = self.request.query_params.get('my', '').lower() == 'true'
            if my_projects:
                queryset = queryset.filter(organization=self.request.user)
        
        return queryset

    @extend_schema(
        summary="List projects",
        description="Get list of projects with filtering and search capabilities.",
    )
    def list(self, request, *args, **kwargs):
        """List projects with filtering."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get project details",
        description="Retrieve detailed information about a project.",
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve project details."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create project",
        description="Create a new project (organizations only).",
    )
    def create(self, request, *args, **kwargs):
        """Create a new project."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            ProjectDetailSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @extend_schema(
        summary="Update project",
        description="Update project information (owner only).",
    )
    def update(self, request, *args, **kwargs):
        """Update project."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(ProjectDetailSerializer(serializer.instance).data)

    @extend_schema(
        summary="Delete project",
        description="Delete a project (owner only).",
    )
    def destroy(self, request, *args, **kwargs):
        """Delete project."""
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """Get current organization's projects."""
        if request.user.role != 'organization':
            return Response(
                {'detail': 'Only organizations can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        projects = self.get_queryset().filter(organization=request.user)
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)
