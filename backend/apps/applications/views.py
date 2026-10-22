from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.applications.models import Application, ApplicationStatus
from apps.applications.serializers import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationReviewSerializer,
    ApplicationListSerializer
)
from apps.core.logging import logger


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления заявками."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'project', 'volunteer']
    search_fields = ['cover_letter', 'volunteer__username', 'project__title']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Фильтруем заявки в зависимости от роли пользователя."""
        user = self.request.user
        
        if user.role == 'volunteer':
            # Волонтер видит только свои заявки
            return Application.objects.filter(volunteer=user)
        elif user.role == 'organization':
            # Организация видит заявки на свои проекты
            return Application.objects.filter(project__organization=user)
        elif user.role == 'admin':
            # Админ видит все заявки
            return Application.objects.all()
        
        return Application.objects.none()

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия."""
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['approve', 'reject']:
            return ApplicationReviewSerializer
        return ApplicationSerializer

    def create(self, request, *args, **kwargs):
        if request.user.role != 'volunteer':
            return Response(
                {'error': 'Только волонтеры могут подавать заявки.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """При создании заявки устанавливаем волонтера."""
        instance = serializer.save(volunteer=self.request.user)
        logger.user_action(
            action="APPLICATION_CREATED",
            user_id=self.request.user.id,
            details={'application_id': instance.id, 'project_id': instance.project_id}
        )

    def perform_update(self, serializer):
        kwargs = {}
        if 'status' in serializer.validated_data and self.request.user.role in ['organization', 'admin']:
            kwargs['reviewed_by'] = self.request.user
            kwargs['reviewed_at'] = timezone.now()
        serializer.save(**kwargs)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def statistics(self, request):
        """Получить статистику по заявкам."""
        qs = self.get_queryset()
        return Response({
            'total_applications': qs.count(),
            'pending_applications': qs.filter(status=ApplicationStatus.PENDING).count(),
            'approved_applications': qs.filter(status=ApplicationStatus.APPROVED).count(),
            'rejected_applications': qs.filter(status=ApplicationStatus.REJECTED).count(),
        })

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'error': 'Удаление заявок запрещено.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        """Одобрить заявку."""
        application = self.get_object()
        
        # Проверяем права: только организация-владелец проекта
        if request.user != application.project.organization:
            return Response(
                {'error': 'Только владелец проекта может одобрять заявки.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if application.status != ApplicationStatus.PENDING:
            return Response(
                {'error': f'Нельзя одобрить заявку со статусом "{application.get_status_display()}". Заявка уже рассмотрена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            serializer = self.get_serializer(application, data={'status': ApplicationStatus.APPROVED}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                reviewed_by=request.user,
                reviewed_at=timezone.now()
            )
            logger.user_action(
                action="APPLICATION_APPROVED",
                user_id=request.user.id,
                details={'application_id': application.id, 'project_id': application.project_id}
            )
            return Response(ApplicationSerializer(application).data)
        except Exception as e:
            logger.error(f"Error approving application {application.id}", exception=e)
            return Response(
                {'error': f'Ошибка при одобрении заявки: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        """Отклонить заявку."""
        application = self.get_object()
        
        # Проверяем права: только организация-владелец проекта
        if request.user != application.project.organization:
            return Response(
                {'error': 'Только владелец проекта может отклонять заявки.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if application.status != ApplicationStatus.PENDING:
            return Response(
                {'error': f'Нельзя отклонить заявку со статусом "{application.get_status_display()}". Заявка уже рассмотрена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            serializer = self.get_serializer(application, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                status=ApplicationStatus.REJECTED,
                reviewed_by=request.user,
                reviewed_at=timezone.now()
            )
            logger.user_action(
                action="APPLICATION_REJECTED",
                user_id=request.user.id,
                details={'application_id': application.id, 'project_id': application.project_id}
            )
            return Response(ApplicationSerializer(application).data)
        except Exception as e:
            logger.error(f"Error rejecting application {application.id}", exception=e)
            return Response(
                {'error': f'Ошибка при отклонении заявки: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        """Отменить заявку (для волонтера)."""
        application = self.get_object()
        
        # Только волонтер может отменить свою заявку
        if request.user != application.volunteer:
            return Response(
                {'error': 'Только волонтер может отменить свою заявку.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not application.can_be_cancelled:
            return Response(
                {'error': 'Эту заявку нельзя отменить.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = ApplicationStatus.CANCELLED
        application.save()
        logger.user_action(
            action="APPLICATION_CANCELLED",
            user_id=request.user.id,
            details={'application_id': application.id, 'project_id': application.project_id}
        )
        return Response(ApplicationSerializer(application).data)
