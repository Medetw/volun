from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User, VolunteerProfile, OrganizationProfile


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
