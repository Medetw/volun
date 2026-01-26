from rest_framework import serializers
from django.utils import timezone
from apps.news.fields import NewsCategoryField, NewsStatusField


class BaseNewsSerializer(serializers.ModelSerializer):
    """Базовый сериализатор с общими полями."""
    category_display = NewsCategoryField(source='category', read_only=True)
    status_display = NewsStatusField(source='status', read_only=True)
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        abstract = True
        fields = [
            'id', 'title', 'slug', 'category', 'category_display',
            'status', 'status_display', 'reading_time'
        ]


class NewsListSerializer(BaseNewsSerializer):
    """Сериализатор для списка новостей."""
    excerpt = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    published_at = serializers.DateTimeField(read_only=True)
    
    class Meta(BaseNewsSerializer.Meta):
        model = None  # Will be set dynamically
        fields = BaseNewsSerializer.Meta.fields + [
            'excerpt', 'image', 'views_count', 'author_name', 'published_at'
        ]


class NewsDetailSerializer(BaseNewsSerializer):
    """Сериализатор для детальной информации о новости."""
    content = serializers.CharField(read_only=True)
    meta_title = serializers.CharField(read_only=True)
    meta_description = serializers.CharField(read_only=True)
    featured = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta(BaseNewsSerializer.Meta):
        model = None  # Will be set dynamically
        fields = BaseNewsSerializer.Meta.fields + [
            'content', 'meta_title', 'meta_description', 'featured',
            'created_at', 'updated_at'
        ]


class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления новостей."""
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'title', 'slug', 'content', 'excerpt', 'category', 'status',
            'image', 'meta_title', 'meta_description', 'featured', 'published_at'
        ]
    
    def validate_slug(self, value):
        """Проверяем уникальность slug."""
        # Dynamic validation will be handled in the view
        return value
    
    def validate(self, attrs):
        """Валидация данных."""
        if attrs.get('status') == 'published' and not attrs.get('published_at'):
            attrs['published_at'] = timezone.now()
        return attrs


class NewsFeaturedSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных новостей."""
    category_display = NewsCategoryField(source='category', read_only=True)
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'id', 'title', 'slug', 'excerpt', 'category_display',
            'image', 'reading_time', 'published_at'
        ]
