from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.admin_panel.serializers import UserAdminSerializer
from apps.users.serializers import UserSerializer
from apps.core.logging import security_logger

User = get_user_model()


class AdminUserViewSet(viewsets.ModelViewSet):
    """ViewSet для администрирования пользователей."""

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["date_joined", "last_login", "username"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        """Только админы могут управлять пользователями."""
        if self.request.user.role != "admin":
            return User.objects.none()
        return User.objects.all()

    def get_serializer_class(self):
        """Разные сериализаторы для разных действий."""
        if self.action in ["create", "update", "partial_update"]:
            return UserAdminSerializer
        return UserSerializer

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def block(self, request, pk=None):
        """Заблокировать пользователя."""
        if request.user.role != "admin":
            return Response(
                {"error": "Только администратор может блокировать пользователей"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()
        if user.role == "admin":
            return Response(
                {"error": "Нельзя заблокировать администратора"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save(update_fields=["is_active"])
        security_logger.security_event(
            event="USER_BLOCKED",
            user_id=request.user.id,
            details={'target_user_id': user.id, 'target_username': user.username}
        )
        return Response({
            'message': (
                f'Пользователь {user.username} заблокирован'
            ),
            'user': UserSerializer(user).data
        })

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def unblock(self, request, pk=None):
        """Разблокировать пользователя."""
        if request.user.role != "admin":
            return Response(
                {"error": "Только администратор может разблокировать пользователей"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        security_logger.security_event(
            event="USER_UNBLOCKED",
            user_id=request.user.id,
            details={'target_user_id': user.id, 'target_username': user.username}
        )
        return Response(
            {
                "message": f"Пользователь {user.username} разблокирован",
                "user": UserSerializer(user).data,
            }
        )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def verify_organization(self, request, pk=None):
        """Верифицировать организацию."""
        if request.user.role != "admin":
            return Response(
                {"error": "Только администратор может верифицировать организации"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()
        if user.role != "organization":
            return Response(
                {"error": "Можно верифицировать только организации"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hasattr(user, "organization_profile"):
            user.organization_profile.is_verified = True
            user.organization_profile.save(update_fields=["is_verified"])
            security_logger.security_event(
                event="ORG_VERIFIED",
                user_id=request.user.id,
                details={'org_user_id': user.id, 'org_name': user.organization_profile.name}
            )
            return Response({
                'message': (
                    f'Организация {user.organization_profile.name} верифицирована'
                ),
                'user': UserSerializer(user).data
            })
        else:
            return Response(
                {"error": "Профиль организации не найден"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def revoke_verification(self, request, pk=None):
        """Отозвать верификацию организации."""
        if request.user.role != "admin":
            return Response(
                {"error": "Только администратор может отзывать верификацию"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()
        if user.role != "organization":
            return Response(
                {"error": "Можно отзывать верификацию только у организаций"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hasattr(user, "organization_profile"):
            user.organization_profile.is_verified = False
            user.organization_profile.save(update_fields=["is_verified"])
            security_logger.security_event(
                event="ORG_VERIFICATION_REVOKED",
                user_id=request.user.id,
                details={'org_user_id': user.id, 'org_name': user.organization_profile.name}
            )
            return Response(
                {
                    "message": (
                        f"Верификация организации "
                        f"{user.organization_profile.name} отозвана"
                    ),
                    "user": UserSerializer(user).data,
                }
            )
        else:
            return Response(
                {"error": "Профиль организации не найден"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def stats(self, request):
        """Статистика пользователей."""
        if request.user.role != "admin":
            return Response(
                {"error": "Только администратор может просматривать статистику"},
                status=status.HTTP_403_FORBIDDEN,
            )

        stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "blocked_users": User.objects.filter(is_active=False).count(),
            "volunteers": User.objects.filter(role="volunteer").count(),
            "organizations": User.objects.filter(role="organization").count(),
            "admins": User.objects.filter(role="admin").count(),
            "verified_organizations": User.objects.filter(
                role="organization", organization_profile__is_verified=True
            ).count(),
            "unverified_organizations": User.objects.filter(
                role="organization", organization_profile__is_verified=False
            ).count(),
        }

        return Response(stats)
