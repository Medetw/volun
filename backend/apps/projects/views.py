from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
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
from apps.projects.permissions import IsOrganizationOrReadOnly, IsProjectOwnerOrReadOnly, IsAdminUserOrAdminRole
from apps.core.logging import logger


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and managing categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None  # No pagination for categories

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUserOrAdminRole()]


class RegionViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and managing regions."""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = None  # No pagination for regions

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUserOrAdminRole()]


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
        """
        Видимость проектов:
          - Гость: только active
          - Волонтёр: active + draft (каталог)
          - Организация: свои (любой статус) + active чужих
          - Admin / moderator: всё
        """
        from django.db.models import Q
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            queryset = queryset.filter(status='active')
        elif user.role in ('admin', 'moderator'):
            pass  # full access
        elif user.role == 'organization':
            queryset = queryset.filter(Q(organization=user) | Q(status='active'))
            my_projects = self.request.query_params.get('my', '').lower() == 'true'
            if my_projects:
                queryset = queryset.filter(organization=user)
        else:  # volunteer
            queryset = queryset.filter(status__in=['active', 'draft'])

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
        logger.user_action(
            action="PROJECT_CREATED",
            user_id=request.user.id,
            details={'project_id': serializer.instance.id, 'title': serializer.instance.title}
        )
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
        logger.user_action(
            action="PROJECT_UPDATED",
            user_id=request.user.id,
            details={'project_id': instance.id, 'title': instance.title}
        )
        return Response(ProjectDetailSerializer(serializer.instance).data)

    @extend_schema(
        summary="Delete project",
        description="Delete a project (owner only).",
    )
    def destroy(self, request, *args, **kwargs):
        """Delete project."""
        instance = self.get_object()
        logger.user_action(
            action="PROJECT_DELETED",
            user_id=request.user.id,
            details={'project_id': instance.id, 'title': instance.title}
        )
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def close(self, request, pk=None):
        """
        Закрыть проект — перевести в статус COMPLETED.
        Доступ: admin / moderator / организация-владелец.
        Возвращает обновлённый проект + список одобренных волонтёров.
        """
        project = self.get_object()
        user = request.user

        is_admin_or_mod = user.role in ('admin', 'moderator')
        is_owner = user == project.organization
        if not (is_admin_or_mod or is_owner):
            return Response(
                {'error': 'Нет прав на закрытие этого проекта.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Атомарная смена статуса — защита от race condition
        from apps.projects.models import Project as ProjectModel
        updated = ProjectModel.objects.filter(
            id=project.id
        ).exclude(status='completed').update(status='completed')
        if updated == 0:
            return Response(
                {'error': 'Проект уже закрыт.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        project.refresh_from_db()

        logger.user_action(
            action="PROJECT_CLOSED",
            user_id=user.id,
            details={'project_id': project.id, 'title': project.title}
        )
        return Response({
            'project': ProjectDetailSerializer(project, context={'request': request}).data,
            'participants': self._participants_payload(project, request),
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def participants(self, request, pk=None):
        """
        Список одобренных волонтёров проекта с их данными:
        hours_committed, total_hours, is_banned, has_certificate.
        Доступ: admin / moderator / организация-владелец.
        """
        project = self.get_object()
        user = request.user

        is_admin_or_mod = user.role in ('admin', 'moderator')
        is_owner = user == project.organization
        if not (is_admin_or_mod or is_owner):
            return Response(
                {'error': 'Нет прав на просмотр участников.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(self._participants_payload(project, request))

    def _participants_payload(self, project, request):
        """Собрать данные участников проекта одним методом (используется в close и participants)."""
        from django.db.models import Sum, Q
        from django.utils import timezone as tz
        from apps.users.models import Blacklist, VolunteerHoursLog, VolunteerCertificate

        apps_qs = (
            project.applications
            .filter(status='approved')
            .select_related('volunteer__volunteer_profile')
        )
        volunteer_ids = [a.volunteer_id for a in apps_qs]

        # Активные баны (с учётом срока)
        now = tz.now()
        banned_ids = set(
            Blacklist.objects
            .filter(volunteer_id__in=volunteer_ids, is_active=True)
            .filter(Q(banned_until__isnull=True) | Q(banned_until__gt=now))
            .values_list('volunteer_id', flat=True)
        )

        # Суммарные часы на этом проекте
        hours_by_vol = {
            r['volunteer_id']: r['total'] or 0
            for r in VolunteerHoursLog.objects
            .filter(volunteer_id__in=volunteer_ids)
            .values('volunteer_id')
            .annotate(total=Sum('hours'))
        }

        # Есть ли сертификат на этот проект
        cert_vols = set(
            VolunteerCertificate.objects
            .filter(volunteer_id__in=volunteer_ids, project=project)
            .values_list('volunteer_id', flat=True)
        )

        result = []
        for app in apps_qs:
            v = app.volunteer
            profile = getattr(v, 'volunteer_profile', None)
            name = f"{profile.first_name} {profile.last_name}".strip() if profile else ''
            avatar_url = None
            if v.avatar:
                req_obj = request._request if hasattr(request, '_request') else request
                avatar_url = req_obj.build_absolute_uri(v.avatar.url)
            result.append({
                'volunteer_id': v.id,
                'application_id': app.id,
                'username': v.username,
                'name': name or v.username,
                'email': v.email,
                'avatar': avatar_url,
                'hours_committed': app.hours_committed,
                'total_hours': hours_by_vol.get(v.id, 0),
                'is_banned': v.id in banned_ids,
                'has_certificate': v.id in cert_vols,
            })
        return result
