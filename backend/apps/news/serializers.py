from rest_framework import serializers
from django.utils import timezone
from apps.news.models import News, NewsCategory, NewsStatus


class NewsListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка новостей."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'excerpt', 'category', 'category_display',
            'image', 'featured', 'views_count', 'author_name', 'reading_time',
            'published_at', 'created_at'
        ]


class NewsDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о новости."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'category', 'category_display',
            'status', 'status_display', 'image', 'featured', 'meta_title', 'meta_description',
            'views_count', 'author_name', 'reading_time', 'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'views_count', 'created_at', 'updated_at', 'author'
        ]


class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления новостей."""
    
    class Meta:
        model = News
        fields = [
            'title', 'slug', 'content', 'excerpt', 'category', 'status',
            'image', 'meta_title', 'meta_description', 'featured', 'published_at'
        ]
    
    def validate_slug(self, value):
        """Проверяем уникальность slug."""
        if self.instance:
            # При обновлении исключаем текущий объект
            if News.objects.filter(slug=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Новость с таким URL уже существует.")
        else:
            # При создании
            if News.objects.filter(slug=value).exists():
                raise serializers.ValidationError("Новость с таким URL уже существует.")
        return value
    
    def validate(self, attrs):
        """Валидация данных."""
        # Автоматически устанавливаем дату публикации
        if attrs.get('status') == NewsStatus.PUBLISHED and not attrs.get('published_at'):
            attrs['published_at'] = timezone.now()
        
        return attrs


class NewsFeaturedSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных новостей на главной."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'excerpt', 'category_display',
            'image', 'reading_time', 'published_at'
        ]
