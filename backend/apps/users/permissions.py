from rest_framework.permissions import BasePermission


class IsAdminOrModerator(BasePermission):
    """Разрешён доступ только для admin и moderator."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ('admin', 'moderator')
        )


class ModeratorPermission(BasePermission):
    """
    Проверяет конкретное RBAC-разрешение у модератора.
    Использование: ModeratorPermission.for_perm('can_manage_hours')
    Админ проходит всегда.
    """
    perm_name: str = ''

    @classmethod
    def for_perm(cls, perm: str):
        """Возвращает класс разрешения для конкретного флага."""
        return type(f'ModeratorPerm_{perm}', (cls,), {'perm_name': perm})

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        if request.user.role != 'moderator':
            return False
        profile = getattr(request.user, 'moderator_profile', None)
        if not profile:
            return False
        return profile.has_permission(self.perm_name)
