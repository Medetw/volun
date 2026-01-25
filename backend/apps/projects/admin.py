from django.contrib import admin
from apps.projects.models import Project, Category, Region


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'category', 'status', 'format', 'volunteers_needed', 'created_at']
    list_filter = ['status', 'category', 'format', 'created_at']
    search_fields = ['title', 'description', 'organization__username']
    readonly_fields = ['created_at', 'updated_at', 'volunteers_count']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization":
            # Фильтруем только пользователей с ролью organization
            kwargs["queryset"] = db_field.related_model.objects.filter(role='organization')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'organization')
        }),
        ('Детали', {
            'fields': ('format', 'region', 'start_date', 'end_date', 'volunteers_needed', 'status')
        }),
        ('Дополнительно', {
            'fields': ('image', 'requirements', 'contact_info')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at', 'volunteers_count'),
            'classes': ('collapse',)
        }),
    )
