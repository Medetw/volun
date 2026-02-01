from django.contrib import admin
from apps.applications.models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'project', 'status', 'hours_committed', 'created_at', 'reviewed_at']
    list_filter = ['status', 'created_at', 'reviewed_at']
    search_fields = ['volunteer__username', 'project__title', 'cover_letter']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('volunteer', 'project', 'status')
        }),
        ('Детали заявки', {
            'fields': ('cover_letter', 'hours_committed')
        }),
        ('Рассмотрение', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_comment')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
