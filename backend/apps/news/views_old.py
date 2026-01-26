from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from apps.news.models import News, NewsStatus
from apps.news.serializers import (
    NewsListSerializer,
    NewsDetailSerializer,
    NewsCreateUpdateSerializer,
    NewsFeaturedSerializer
)


class NewsViewSet(viewsets.ModelViewSet):
    """ViewSet для управления новостями."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'featured']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_at', 'created_at', 'views_count']
    ordering = ['-published_at', '-created_at']

    def get_queryset(self):
        """Фильтруем новости в зависимости от роли."""
        user = self.request.user
        
        if user.role == 'admin':
            # Админы видят все новости
            return News.objects.all()
        else:
            # Остальные видят только опубликованные новости
            return News.objects.filter(status=NewsStatus.PUBLISHED)

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия."""
        if self.action == 'list':
            return NewsListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return NewsCreateUpdateSerializer
        elif self.action == 'featured':
            return NewsFeaturedSerializer
        return NewsDetailSerializer

    def get_permissions(self):
        """Настраиваем права доступа."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Только админы могут создавать/редактировать новости
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            # Все могут читать опубликованные новости
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        """При создании новости устанавливаем автора."""
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """Получить избранные новости для главной страницы."""
        featured_news = News.objects.filter(
            status=NewsStatus.PUBLISHED,
            featured=True
        ).order_by('-published_at')[:5]
        
        serializer = self.get_serializer(featured_news, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def view(self, request, pk=None):
        """Увеличить счетчик просмотров."""
        news = self.get_object()
        news.increment_views()
        return Response({'views_count': news.views_count})

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_category(self, request):
        """Получить новости по категории."""
        category = request.query_params.get('category')
        if not category:
            return Response(
                {'error': 'Параметр category обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        news = News.objects.filter(
            status=NewsStatus.PUBLISHED,
            category=category
        ).order_by('-published_at')
        
        page = self.paginate_queryset(news)
        if page is not None:
            serializer = NewsListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = NewsListSerializer(news, many=True)
        return Response(serializer.data)
