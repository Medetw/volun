from django.contrib import admin
from apps.statistics.models import UserStats, ProjectStats, ApplicationStats


@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = [
        'total_users', 'volunteers', 'organizations', 
        'admins', 'active_users', 'updated_at'
    ]
    readonly_fields = ['updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ProjectStats)
class ProjectStatsAdmin(admin.ModelAdmin):
    list_display = [
        'total_projects', 'active_projects', 'completed_projects',
        'total_volunteers_needed', 'updated_at'
    ]
    readonly_fields = ['updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ApplicationStats)
class ApplicationStatsAdmin(admin.ModelAdmin):
    list_display = [
        'total_applications', 'pending_applications', 
        'approved_applications', 'total_hours', 'updated_at'
    ]
    readonly_fields = ['updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
