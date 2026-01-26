from django.contrib import admin
from django.utils import timezone
from apps.news.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'status', 'featured', 
        'views_count', 'author', 'published_at', 'created_at'
    ]
    list_filter = [
        'status', 'category', 'featured', 'created_at', 'published_at'
    ]
    search_fields = [
        'title', 'content', 'excerpt'
    ]
    readonly_fields = [
        'views_count', 'created_at', 'updated_at'
    ]
    
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title', 'slug', 'content', 'excerpt', 'image'
            )
        }),
        ('Категоризация', {
            'fields': (
                'category', 'status', 'featured'
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title', 'meta_description'
            ),
            'classes': ('collapse',)
        }),
        ('Публикация', {
            'fields': (
                'author', 'published_at'
            )
        }),
        ('Метаданные', {
            'fields': (
                'views_count', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'admin':
            return qs
        return qs.filter(author=request.user)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Только при создании
            obj.author = request.user
        
        # Автоматически устанавливаем дату публикации
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        
        super().save_model(request, obj, form, change)
