from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User, VolunteerProfile, OrganizationProfile, VolunteerHoursLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'role')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'city', 'region', 'volunteer_hours']
    list_filter = ['city', 'region', 'gender']
    search_fields = ['user__username', 'first_name', 'last_name']
    readonly_fields = ['user']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'first_name', 'last_name', 'birth_date', 'gender')
        }),
        ('Местоположение', {
            'fields': ('city', 'region')
        }),
        ('Навыки и интересы', {
            'fields': ('skills', 'interests')
        }),
        ('Статистика', {
            'fields': ('volunteer_hours',)
        }),
    )


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization_type', 'region', 'is_verified', 'user']
    list_filter = ['organization_type', 'is_verified', 'region']
    search_fields = ['name', 'user__username']
    readonly_fields = ['user']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'organization_type', 'description')
        }),
        ('Контакты и местоположение', {
            'fields': ('region', 'contacts')
        }),
        ('Статус', {
            'fields': ('is_verified',)
        }),
    )


@admin.register(VolunteerHoursLog)
class VolunteerHoursLogAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'hours', 'date', 'moderator', 'description', 'created_at']
    list_filter = ['date', 'moderator']
    search_fields = ['volunteer__username', 'volunteer__volunteer_profile__first_name',
                     'volunteer__volunteer_profile__last_name', 'description']
    autocomplete_fields = ['volunteer', 'moderator']
    readonly_fields = ['created_at', 'moderator']
    date_hierarchy = 'date'

    fieldsets = (
        ('Запись', {
            'fields': ('volunteer', 'hours', 'date', 'description')
        }),
        ('Служебное', {
            'fields': ('moderator', 'created_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.moderator_id:
            obj.moderator = request.user
        super().save_model(request, obj, form, change)
        # Пересчитываем часы волонтёра
        from django.db.models import Sum
        profile = getattr(obj.volunteer, 'volunteer_profile', None)
        if profile:
            total = VolunteerHoursLog.objects.filter(
                volunteer=obj.volunteer
            ).aggregate(total=Sum('hours'))['total'] or 0
            profile.volunteer_hours = total
            profile.save(update_fields=['volunteer_hours'])
