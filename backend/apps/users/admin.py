from django.contrib import admin
from apps.users.models import User, VolunteerProfile, OrganizationProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'city', 'volunteer_hours']
    list_filter = ['city', 'region']
    search_fields = ['user__username', 'first_name', 'last_name']


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization_type', 'region', 'is_verified']
    list_filter = ['organization_type', 'is_verified', 'region']
    search_fields = ['name', 'user__username']
