from rest_framework import permissions
from apps.projects.models import Project


class IsOrganizationOrReadOnly(permissions.BasePermission):
    """
    Permission class:
    - Read-only for everyone (including unauthenticated)
    - Create/Update/Delete only for organizations
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for authenticated organizations
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'organization'
        )


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class:
    - Read-only for everyone
    - Update/Delete only for project owner (organization)
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for project owner
        return obj.organization == request.user
