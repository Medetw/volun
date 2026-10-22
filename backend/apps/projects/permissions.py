from rest_framework import permissions
from apps.projects.models import Project


class IsOrganizationOrReadOnly(permissions.BasePermission):
    """
    - Read: всем
    - Write: организация / модератор / админ
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ('organization', 'moderator', 'admin')
        )


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    - Read: всем
    - Update/Delete: владелец проекта, либо admin/moderator
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role in ('admin', 'moderator'):
            return True
        return obj.organization == request.user


class IsAdminUserOrAdminRole(permissions.BasePermission):
    """
    Allow access to staff or users with admin role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (getattr(request.user, 'is_staff', False) or getattr(request.user, 'role', None) == 'admin')
        )

