from django.contrib import admin
from apps.reports.models import ProjectReport, VolunteerContribution


class VolunteerContributionInline(admin.TabularInline):
    model = VolunteerContribution
    extra = 0
    readonly_fields = ['volunteer', 'hours_contributed']


@admin.register(ProjectReport)
class ProjectReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'project', 'status', 'total_volunteer_hours',
        'total_volunteers_participated', 'created_at', 'submitted_at'
    ]
    list_filter = [
        'status', 'created_at', 'submitted_at', 'project__category'
    ]
    search_fields = [
        'title', 'description', 'project__title',
        'project__organization__username'
    ]
    readonly_fields = ['created_at', 'updated_at', 'submitted_at', 'reviewed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основное', {
            'fields': ('project', 'title', 'description')
        }),
        ('Результаты', {
            'fields': ('goals_achieved', 'challenges_faced')
        }),
        ('Статистика', {
            'fields': (
                'total_volunteers_participated', 'total_volunteer_hours',
                'beneficiaries_count'
            )
        }),
        ('Медиа', {
            'fields': ('report_file', 'photos'),
            'classes': ('collapse',)
        }),
        ('Дополнительная информация', {
            'fields': ('lessons_learned', 'future_plans'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('status', 'reviewed_by', 'review_comment')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'reviewed_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [VolunteerContributionInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'admin':
            return qs
        elif request.user.role == 'organization':
            return qs.filter(project__organization=request.user)
        return qs.none()

    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем организацию при создании."""
        if not change and request.user.role == 'organization':
            # Проверяем что проект принадлежит организации
            if obj.project.organization != request.user:
                from django.contrib import messages
                messages.error(request, 'Вы можете создавать отчеты только для своих проектов')
                return
        super().save_model(request, obj, form, change)


@admin.register(VolunteerContribution)
class VolunteerContributionAdmin(admin.ModelAdmin):
    list_display = [
        'volunteer', 'report', 'hours_contributed',
        'performance_rating', 'tasks_completed'[:50]
    ]
    list_filter = [
        'performance_rating', 'hours_contributed',
        'report__status', 'report__project__category'
    ]
    search_fields = [
        'volunteer__username', 'volunteer__email',
        'report__title', 'tasks_completed', 'impact_description'
    ]
    readonly_fields = ['report']
    
    fieldsets = (
        ('Основное', {
            'fields': ('report', 'volunteer', 'hours_contributed')
        }),
        ('Описание', {
            'fields': ('tasks_completed', 'impact_description')
        }),
        ('Оценка', {
            'fields': ('performance_rating', 'feedback')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'admin':
            return qs
        elif request.user.role == 'organization':
            return qs.filter(report__project__organization=request.user)
        elif request.user.role == 'volunteer':
            return qs.filter(volunteer=request.user)
        return qs.none()
