from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q

from apps.reports.models import ProjectReport, ReportStatus, VolunteerContribution
from apps.reports.serializers import (
    ProjectReportSerializer,
    ProjectReportCreateSerializer,
    ProjectReportUpdateSerializer,
    ReportReviewSerializer,
    ReportStatsSerializer,
    VolunteerContributionSerializer
)


class ProjectReportViewSet(viewsets.ModelViewSet):
    """ViewSet для управления отчетами по проектам."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'project']
    search_fields = ['title', 'description', 'goals_achieved']
    ordering_fields = ['created_at', 'submitted_at', 'total_volunteer_hours']
    ordering = ['-created_at']

    def get_queryset(self):
        """Фильтруем отчеты в зависимости от роли."""
        user = self.request.user
        
        if user.role == 'admin':
            return ProjectReport.objects.all()
        elif user.role == 'organization':
            return ProjectReport.objects.filter(project__organization=user)
        elif user.role == 'volunteer':
            # Волонтеры видят отчеты проектов, в которых они участвовали
            return ProjectReport.objects.filter(
                project__applications__volunteer=user,
                project__applications__status='approved'
            ).distinct()
        
        return ProjectReport.objects.none()

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия."""
        if self.action == 'create':
            return ProjectReportCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProjectReportUpdateSerializer
        elif self.action in ['approve', 'reject']:
            return ReportReviewSerializer
        return ProjectReportSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        """Отправить отчет на модерацию."""
        report = self.get_object()
        
        # Проверяем права
        if request.user.role != 'admin' and report.project.organization != request.user:
            return Response(
                {'error': 'Только владелец проекта может отправлять отчет'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if report.status != ReportStatus.DRAFT:
            return Response(
                {'error': 'Можно отправить только черновик'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.submit()
        return Response({'message': 'Отчет отправлен на модерацию'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        """Одобрить отчет."""
        report = self.get_object()
        
        # Только админы могут одобрять
        if request.user.role != 'admin':
            return Response(
                {'error': 'Только администратор может одобрять отчеты'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        comment = serializer.validated_data.get('review_comment', '')
        report.approve(request.user, comment)
        
        return Response({'message': 'Отчет одобрен'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        """Отклонить отчет."""
        report = self.get_object()
        
        # Только админы могут отклонять
        if request.user.role != 'admin':
            return Response(
                {'error': 'Только администратор может отклонять отчеты'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        comment = serializer.validated_data.get('review_comment', '')
        if not comment:
            return Response(
                {'error': 'Необходимо указать причину отклонения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.reject(request.user, comment)
        
        return Response({'message': 'Отчет отклонен'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_contribution(self, request, pk=None):
        """Добавить вклад волонтера в отчет."""
        report = self.get_object()
        
        # Проверяем права
        if request.user.role != 'admin' and report.project.organization != request.user:
            return Response(
                {'error': 'Только владелец проекта может добавлять вклады'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = VolunteerContributionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(report=report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получить статистику отчетов."""
        user = request.user
        queryset = self.get_queryset()
        
        stats = {
            'total_reports': queryset.count(),
            'draft_reports': queryset.filter(status=ReportStatus.DRAFT).count(),
            'submitted_reports': queryset.filter(status=ReportStatus.SUBMITTED).count(),
            'approved_reports': queryset.filter(status=ReportStatus.APPROVED).count(),
            'rejected_reports': queryset.filter(status=ReportStatus.REJECTED).count(),
        }
        
        # Дополнительная статистика для организаций
        if user.role == 'organization':
            stats.update({
                'total_volunteer_hours': queryset.aggregate(
                    total=Sum('total_volunteer_hours')
                )['total'] or 0,
                'total_beneficiaries': queryset.aggregate(
                    total=Sum('beneficiaries_count')
                )['total'] or 0,
            })
        
        serializer = ReportStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_projects(self, request):
        """Отчеты по проектам текущей организации."""
        if request.user.role != 'organization':
            return Response(
                {'error': 'Только организации могут просматривать свои отчеты'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reports = self.get_queryset().filter(project__organization=request.user)
        page = self.paginate_queryset(reports)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)


class VolunteerContributionViewSet(viewsets.ModelViewSet):
    """ViewSet для управления вкладами волонтеров."""
    serializer_class = VolunteerContributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report', 'volunteer']
    search_fields = ['tasks_completed', 'impact_description', 'feedback']
    ordering_fields = ['hours_contributed', 'performance_rating']
    ordering = ['-hours_contributed']

    def get_queryset(self):
        """Фильтруем вклады в зависимости от роли."""
        user = self.request.user
        
        if user.role == 'admin':
            return VolunteerContribution.objects.all()
        elif user.role == 'organization':
            return VolunteerContribution.objects.filter(report__project__organization=user)
        elif user.role == 'volunteer':
            return VolunteerContribution.objects.filter(volunteer=user)
        
        return VolunteerContribution.objects.none()

    def perform_create(self, serializer):
        """Проверяем права при создании."""
        user = self.request.user
        
        # Только организации и админы могут создавать вклады
        if user.role not in ['organization', 'admin']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Только организации могут создавать вклады волонтеров")
        
        # Проверяем, что отчет принадлежит организации
        report = serializer.validated_data['report']
        if user.role == 'organization' and report.project.organization != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Вы можете добавлять вклады только в свои отчеты")
        
        serializer.save()
