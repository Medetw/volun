from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import transaction, models
from django.core.cache import cache

from apps.news.models import News, NewsStatus
from apps.news.serializers_v2 import (
    NewsListSerializer,
    NewsDetailSerializer, 
    NewsCreateUpdateSerializer,
    NewsFeaturedSerializer
)


class NewsViewSet(viewsets.ModelViewSet):
    """ViewSet для управления новостями с оптимизацией."""
    
    def get_permissions(self):
        """Разные права для разных действий."""
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'featured']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_at', 'created_at', 'views_count']
    ordering = ['-published_at', '-created_at']
    
    # Кэширование для популярных запросов
    cache_timeout = 300  # 5 минут

    def get_queryset(self):
        """Оптимизированный queryset с select_related."""
        user = self.request.user
        
        # Базовый queryset с оптимизацией
        queryset = News.objects.select_related('author').all()
        
        # Для анонимных пользователей показываем только опубликованные новости
        if not user.is_authenticated:
            return queryset.filter(status=NewsStatus.PUBLISHED)
        
        # Для админов показываем все новости
        if user.is_authenticated and hasattr(user, 'role') and user.role == 'admin':
            return queryset
        else:
            return queryset.filter(status=NewsStatus.PUBLISHED)

    def get_serializer_class(self):
        """Динамический выбор сериализатора."""
        if self.action == 'list':
            return self._get_serializer_class(NewsListSerializer)
        elif self.action in ['create', 'update', 'partial_update']:
            return self._get_serializer_class(NewsCreateUpdateSerializer)
        elif self.action == 'featured':
            return self._get_serializer_class(NewsFeaturedSerializer)
        return self._get_serializer_class(NewsDetailSerializer)

    def _get_serializer_class(self, serializer_class):
        """Динамически устанавливает модель для сериализатора."""
        class DynamicSerializer(serializer_class):
            class Meta:
                model = News
                fields = serializer_class.Meta.fields
        return DynamicSerializer

    def perform_create(self, serializer):
        """Создание новости с транзакцией."""
        with transaction.atomic():
            serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Получение новости с кэшированием и увеличением просмотров."""
        instance = self.get_object()
        
        # Увеличиваем счетчик просмотров асинхронно
        self._increment_views(instance.pk)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _increment_views(self, news_id):
        """Асинхронное увеличение счетчика просмотров."""
        News.objects.filter(pk=news_id).update(views_count=models.F('views_count') + 1)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """Избранные новости с кэшированием."""
        cache_key = 'featured_news'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        featured_news = News.objects.filter(
            status=NewsStatus.PUBLISHED,
            featured=True
        ).select_related('author').order_by('-published_at')[:5]
        
        serializer = self.get_serializer(featured_news, many=True)
        cache.set(cache_key, serializer.data, self.cache_timeout)
        
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def view(self, request, pk=None):
        """Увеличить счетчик просмотров."""
        news = self.get_object()
        self._increment_views(news.pk)
        
        return Response({'views_count': news.views_count + 1})

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_category(self, request):
        """Новости по категории с пагинацией."""
        category = request.query_params.get('category')
        if not category:
            return Response(
                {'error': 'Параметр category обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Кэширование по категории
        cache_key = f'news_category_{category}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        news = News.objects.filter(
            status=NewsStatus.PUBLISHED,
            category=category
        ).select_related('author').order_by('-published_at')
        
        page = self.paginate_queryset(news)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, self.cache_timeout)
            return response
        
        serializer = self.get_serializer(news, many=True)
        cache.set(cache_key, serializer.data, self.cache_timeout)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def recent(self, request):
        """Последние новости с кэшированием."""
        cache_key = 'recent_news'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        recent_news = News.objects.filter(
            status=NewsStatus.PUBLISHED
        ).select_related('author').order_by('-published_at')[:10]
        
        serializer = NewsListSerializer(recent_news, many=True)
        cache.set(cache_key, serializer.data, self.cache_timeout)
        
        return Response(serializer.data)
