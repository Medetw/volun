from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Count, Q
from django.core.cache import cache

from apps.notifications.models import Notification, NotificationPreference, NotificationType
from apps.notifications.serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationPreferenceSerializer,
    NotificationStatsSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления уведомлениями."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'notification_type']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'read_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Пользователь видит только свои уведомления."""
        return Notification.objects.filter(recipient=self.request.user)

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия."""
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        """При создании устанавливаем получателя."""
        serializer.save(recipient=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Получить непрочитанные уведомления."""
        unread_notifications = self.get_queryset().filter(status='unread')
        page = self.paginate_queryset(unread_notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Отметить все уведомления как прочитанные."""
        count = self.get_queryset().filter(status='unread').update(
            status='read',
            read_at=timezone.now()
        )
        return Response({'message': f'Отмечено {count} уведомлений как прочитанные'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Отметить уведомление как прочитанное."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Уведомление отмечено как прочитанное'})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Архивировать уведомление."""
        notification = self.get_object()
        notification.mark_as_archived()
        return Response({'message': 'Уведомление архивировано'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получить статистику уведомлений."""
        user = request.user
        cache_key = f'notification_stats_{user.id}'
        
        # Пробуем получить из кэша
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return Response(cached_stats)
        
        # Генерируем статистику
        queryset = self.get_queryset()
        stats = {
            'total': queryset.count(),
            'unread': queryset.filter(status='unread').count(),
            'read': queryset.filter(status='read').count(),
            'recent': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }
        
        # Сохраняем в кэш на 5 минут
        cache.set(cache_key, stats, 300)
        
        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet для управления настройками уведомлений."""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Пользователь управляет только своими настройками."""
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_object(self):
        """Получаем или создаем настройки для пользователя."""
        obj, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj

    def retrieve(self, request, *args, **kwargs):
        """Получить настройки уведомлений."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Обновить настройки уведомлений."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Создание настроек не разрешено (только обновление)."""
        return Response(
            {'detail': 'Используйте PUT/PATCH для обновления настроек.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        """Удаление настроек не разрешено."""
        return Response(
            {'detail': 'Удаление настроек не разрешено.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class NotificationAdminViewSet(viewsets.ModelViewSet):
    """Admin ViewSet для управления всеми уведомлениями."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'notification_type', 'recipient']
    search_fields = ['title', 'message', 'recipient__username']
    ordering_fields = ['created_at', 'read_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Только админы могут управлять всеми уведомлениями."""
        if self.request.user.role == 'admin':
            return Notification.objects.all()
        return Notification.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        """Админ может создавать уведомления для любых пользователей."""
        serializer.save()

    @action(detail=False, methods=['post'])
    def broadcast(self, request):
        """Рассылка уведомлений всем пользователям."""
        if request.user.role != 'admin':
            return Response(
                {'detail': 'Только администраторы могут рассылать уведомления.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('notification_type', NotificationType.SYSTEM)
        
        if not title or not message:
            return Response(
                {'detail': 'Необходимо указать заголовок и сообщение.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Создаем уведомления для всех активных пользователей
        users = User.objects.filter(is_active=True)
        notifications = []
        
        for user in users:
            notifications.append(Notification(
                recipient=user,
                sender=request.user,
                notification_type=notification_type,
                title=title,
                message=message
            ))
        
        # Массовое создание
        Notification.objects.bulk_create(notifications)
        
        return Response({
            'message': f'Рассылка создана для {len(notifications)} пользователей'
        })
