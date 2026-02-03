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
        elif self.action == 'list':
            return ApplicationListSerializer
        return ApplicationSerializer

    def perform_create(self, serializer):
        """При создании заявки устанавливаем волонтера."""
        serializer.save(volunteer=self.request.user)

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
            
            return Response(ApplicationSerializer(application).data)
        except Exception as e:
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
            
            return Response(ApplicationSerializer(application).data)
        except Exception as e:
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
        
        return Response(ApplicationSerializer(application).data)
