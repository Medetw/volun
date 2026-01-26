from rest_framework import permissions


class IsVolunteerOrOrganization(permissions.BasePermission):
    """Разрешение для волонтеров и организаций."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ['volunteer', 'organization']
        )


class IsOwnerOrOrganization(permissions.BasePermission):
    """Разрешение для владельца (волонтера) или организации-владельца проекта."""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Волонтер может управлять только своими заявками
        if request.user.role == 'volunteer':
            return obj.volunteer == request.user
        
        # Организация может управлять заявками на свои проекты
        if request.user.role == 'organization':
            return obj.project.organization == request.user
        
        # Админ может всё
        return request.user.role == 'admin'
