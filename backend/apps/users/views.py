from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, permissions, views, status
from rest_framework.decorators import action
from django.db import models
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from apps.users.models import User, UserRole, VolunteerCertificate, VolunteerHoursLog, VolunteerProfile, ModeratorProfile, Blacklist
from apps.users.serializers import (
    UserSerializer,
    VolunteerCertificateSerializer, VolunteerHoursLogSerializer,
    ModeratorProfileSerializer, BlacklistSerializer,
)
from apps.users.permissions import IsAdminOrModerator, ModeratorPermission, IsAdminRole
from apps.core.logging import logger


class VolunteerCertificateViewSet(viewsets.ModelViewSet):
    """ViewSet для управления сертификатами волонтёра."""
    serializer_class = VolunteerCertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _is_moderator_with_perm(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.MODERATOR:
            profile = getattr(user, 'moderator_profile', None)
            return profile and profile.can_manage_certificates
        return False

    def get_queryset(self):
        user = self.request.user
        if user.role in (UserRole.ADMIN, UserRole.MODERATOR):
            qs = VolunteerCertificate.objects.select_related('volunteer')
            volunteer_id = self.request.query_params.get('volunteer_id')
            if volunteer_id:
                qs = qs.filter(volunteer_id=volunteer_id)
            return qs
        return VolunteerCertificate.objects.filter(volunteer=user)

    def perform_create(self, serializer):
        """Волонтёр создаёт себе, модератор/админ указывает volunteer явно."""
        user = self.request.user
        if self._is_moderator_with_perm():
            # volunteer должен прийти в теле запроса
            if 'volunteer' not in serializer.validated_data:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'volunteer': 'Укажите волонтёра.'})
            serializer.save()
        else:
            serializer.save(volunteer=user)
        logger.user_action(
            action="CERTIFICATE_UPLOADED",
            user_id=user.id,
            details={'title': serializer.instance.title}
        )

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role == UserRole.MODERATOR and not self._is_moderator_with_perm():
            return Response(
                {'error': 'У вас нет разрешения на управление сертификатами'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_destroy(self, instance):
        logger.user_action(
            action="CERTIFICATE_DELETED",
            user_id=self.request.user.id,
            details={'title': instance.title, 'certificate_id': instance.id}
        )
        instance.delete()


def _recalc_volunteer_hours(volunteer):
    """Пересчитать и сохранить volunteer_hours в профиле."""
    profile = getattr(volunteer, 'volunteer_profile', None)
    if profile:
        total = VolunteerHoursLog.objects.filter(
            volunteer=volunteer
        ).aggregate(total=Sum('hours'))['total'] or 0
        profile.volunteer_hours = total
        profile.save(update_fields=['volunteer_hours'])


class VolunteerHoursViewSet(viewsets.ModelViewSet):
    """ViewSet для учёта волонтёрских часов.
    Создание/изменение/удаление — только модератор с can_manage_hours или админ.
    Чтение — волонтёр видит свои, модератор/админ — все.
    """
    serializer_class = VolunteerHoursLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _check_hours_perm(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.MODERATOR:
            profile = getattr(user, 'moderator_profile', None)
            return profile and profile.can_manage_hours
        return False

    def get_queryset(self):
        user = self.request.user
        if user.role in (UserRole.MODERATOR, UserRole.ADMIN):
            volunteer_id = self.request.query_params.get('volunteer_id')
            qs = VolunteerHoursLog.objects.select_related('volunteer', 'moderator')
            if volunteer_id:
                qs = qs.filter(volunteer_id=volunteer_id)
            return qs
        return VolunteerHoursLog.objects.filter(volunteer=user).select_related('moderator')

    def create(self, request, *args, **kwargs):
        if not self._check_hours_perm():
            return Response(
                {'error': 'У вас нет разрешения на учёт рабочего времени'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save(moderator=self.request.user)
        _recalc_volunteer_hours(instance.volunteer)

    def update(self, request, *args, **kwargs):
        if not self._check_hours_perm():
            return Response(
                {'error': 'У вас нет разрешения на учёт рабочего времени'},
                status=status.HTTP_403_FORBIDDEN
            )
        response = super().update(request, *args, **kwargs)
        _recalc_volunteer_hours(self.get_object().volunteer)
        return response

    def destroy(self, request, *args, **kwargs):
        if not self._check_hours_perm():
            return Response(
                {'error': 'У вас нет разрешения на учёт рабочего времени'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        volunteer = instance.volunteer
        instance.delete()
        _recalc_volunteer_hours(volunteer)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VolunteerListView(views.APIView):
    """Список волонтёров — только для модератора с can_view_volunteers или админа."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == UserRole.ADMIN:
            pass  # разрешено
        elif user.role == UserRole.MODERATOR:
            profile = getattr(user, 'moderator_profile', None)
            if not profile or not profile.can_view_volunteers:
                return Response(
                    {'error': 'У вас нет разрешения на просмотр волонтёров'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': 'Доступ только для модераторов и администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )

        search = request.query_params.get('search', '').strip()
        volunteers = User.objects.filter(
            role=UserRole.VOLUNTEER, is_active=True
        ).select_related('volunteer_profile').order_by('username')
        if search:
            # Экранируем LIKE-wildcards чтобы пользователь не мог вводить % и _ как шаблон
            escaped = search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            volunteers = volunteers.filter(
                models.Q(username__icontains=escaped) |
                models.Q(email__icontains=escaped) |
                models.Q(volunteer_profile__first_name__icontains=escaped) |
                models.Q(volunteer_profile__last_name__icontains=escaped)
            )

        # Получаем активные баны одним запросом
        from apps.users.models import Blacklist
        from django.utils import timezone as tz
        now = tz.now()
        banned_ids = set(
            Blacklist.objects.filter(
                volunteer__in=volunteers,
                is_active=True,
            ).filter(
                models.Q(banned_until__isnull=True) | models.Q(banned_until__gt=now)
            ).values_list('volunteer_id', flat=True)
        )

        data = []
        for v in volunteers:
            profile = getattr(v, 'volunteer_profile', None)
            name = f"{profile.first_name} {profile.last_name}".strip() if profile else ''
            data.append({
                'id': v.id,
                'username': v.username,
                'name': name or v.username,
                'email': v.email,
                'city': profile.city if profile else '',
                'region': profile.region if profile else '',
                'volunteer_hours': profile.volunteer_hours if profile else 0,
                'is_banned': v.id in banned_ids,
            })
        return Response(data)


class ModeratorProfileView(views.APIView):
    """Получить/обновить RBAC-профиль текущего модератора."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != UserRole.MODERATOR:
            return Response({'error': 'Только для модераторов'}, status=status.HTTP_403_FORBIDDEN)
        profile, _ = ModeratorProfile.objects.get_or_create(user=request.user)
        return Response(ModeratorProfileSerializer(profile).data)

    def patch(self, request):
        if request.user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)
        profile, _ = ModeratorProfile.objects.get_or_create(user=request.user)
        serializer = ModeratorProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ModeratorManagementView(views.APIView):
    """
    Блок 7: управление модераторами (только админ).
    GET  /moderators/        — список всех модераторов
    POST /moderators/        — создать нового модератора
    """
    permission_classes = [permissions.IsAuthenticated]

    def _check_admin(self, request):
        if request.user.role != UserRole.ADMIN:
            return Response(
                {'error': 'Только администраторы могут управлять модераторами.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def get(self, request):
        denied = self._check_admin(request)
        if denied:
            return denied
        mods = User.objects.filter(role=UserRole.MODERATOR, is_active=True) \
            .select_related('moderator_profile').order_by('username')
        result = []
        for u in mods:
            p = getattr(u, 'moderator_profile', None)
            result.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'department': p.department if p else '',
                'can_view_volunteers': p.can_view_volunteers if p else False,
                'can_manage_hours': p.can_manage_hours if p else False,
                'can_manage_certificates': p.can_manage_certificates if p else False,
                'created_at': p.created_at.isoformat() if p else None,
            })
        return Response(result)

    def post(self, request):
        denied = self._check_admin(request)
        if denied:
            return denied

        username = (request.data.get('username') or '').strip()
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        department = (request.data.get('department') or '').strip()

        if not username or not email or not password:
            return Response(
                {'error': 'username, email и password обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(password) < 8:
            return Response(
                {'error': 'Пароль должен быть не короче 8 символов'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username уже занят'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email уже занят'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, email=email, password=password,
            role=UserRole.MODERATOR, is_active=True,
        )
        profile = ModeratorProfile.objects.create(
            user=user,
            department=department,
            can_view_volunteers=bool(request.data.get('can_view_volunteers', True)),
            can_manage_hours=bool(request.data.get('can_manage_hours', True)),
            can_manage_certificates=bool(request.data.get('can_manage_certificates', True)),
        )
        logger.user_action(
            action="MODERATOR_CREATED",
            user_id=request.user.id,
            details={'new_moderator_id': user.id, 'username': user.username}
        )
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'department': profile.department,
        }, status=status.HTTP_201_CREATED)


class ModeratorDetailView(views.APIView):
    """DELETE /moderators/{id}/ — понижение модератора до волонтёра (только admin)."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        if request.user.role != UserRole.ADMIN:
            return Response(
                {'error': 'Только администраторы могут удалять модераторов.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            mod = User.objects.get(pk=pk, role=UserRole.MODERATOR)
        except User.DoesNotExist:
            return Response({'error': 'Модератор не найден'}, status=status.HTTP_404_NOT_FOUND)
        # Мягкое удаление: понижаем до volunteer, чтобы не терять историю действий
        mod.role = UserRole.VOLUNTEER
        mod.save(update_fields=['role'])
        ModeratorProfile.objects.filter(user=mod).delete()
        logger.user_action(
            action="MODERATOR_REMOVED",
            user_id=request.user.id,
            details={'former_moderator_id': mod.id}
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlacklistViewSet(viewsets.ModelViewSet):
    """
    ЧС — чёрный список волонтёров.
    Доступ: только admin / moderator.
    POST   /blacklist/          — добавить волонтёра (reason обязателен)
    GET    /blacklist/          — список всех записей
    GET    /blacklist/{id}/     — конкретная запись
    POST   /blacklist/{id}/unban/ — снять с ЧС
    GET    /blacklist/check/?volunteer_id=N — проверить статус
    """
    serializer_class = BlacklistSerializer
    permission_classes = [IsAdminOrModerator]

    def get_queryset(self):
        return Blacklist.objects.select_related(
            'volunteer__volunteer_profile', 'banned_by'
        ).all()

    def perform_create(self, serializer):
        serializer.save(banned_by=self.request.user, is_active=True)
        logger.user_action(
            action="BLACKLIST_BAN",
            user_id=self.request.user.id,
            details={
                'volunteer_id': serializer.instance.volunteer_id,
                'reason': serializer.instance.reason,
                'banned_until': str(serializer.instance.banned_until),
            }
        )

    @action(detail=False, methods=['get'])
    def check(self, request):
        """Проверить, находится ли волонтёр в ЧС. ?volunteer_id=N"""
        raw = request.query_params.get('volunteer_id')
        if not raw:
            return Response(
                {'error': 'Параметр volunteer_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            volunteer_id = int(raw)
        except (TypeError, ValueError):
            return Response(
                {'error': 'volunteer_id должен быть целым числом'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # is_currently_banned() проверяет и is_active, и banned_until
        # Фильтр is_active=True — оптимизация: не загружать неактивные записи
        entry = Blacklist.objects.filter(
            volunteer_id=volunteer_id, is_active=True
        ).select_related('volunteer__volunteer_profile', 'banned_by').first()

        if entry and entry.is_currently_banned():
            return Response({
                'is_banned': True,
                'entry': BlacklistSerializer(entry).data,
            })
        return Response({'is_banned': False})

    @action(detail=True, methods=['post'])
    def unban(self, request, pk=None):
        """Снять волонтёра с ЧС (атомарно — защита от race condition)."""
        entry = self.get_object()
        updated = Blacklist.objects.filter(id=entry.id, is_active=True).update(is_active=False)
        if updated == 0:
            return Response(
                {'error': 'Запись уже неактивна'},
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.user_action(
            action="BLACKLIST_UNBAN",
            user_id=request.user.id,
            details={'volunteer_id': entry.volunteer_id, 'ban_id': entry.id}
        )
        return Response({'message': 'Волонтёр удалён из ЧС.'})


class VolunteerOfWeekAPIView(views.APIView):
    """Публичный endpoint: волонтёр недели по суммарным часам за текущую неделю."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Начало текущей недели (понедельник)
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        top = (
            VolunteerHoursLog.objects
            .filter(date__gte=week_start)
            .values('volunteer')
            .annotate(week_hours=Sum('hours'))
            .order_by('-week_hours')
            .first()
        )

        if not top:
            return Response({'volunteer': None, 'week_hours': 0})

        try:
            volunteer = User.objects.select_related('volunteer_profile').get(pk=top['volunteer'])
        except User.DoesNotExist:
            return Response({'volunteer': None, 'week_hours': 0})

        profile = getattr(volunteer, 'volunteer_profile', None)
        name = ''
        if profile:
            name = f"{profile.first_name} {profile.last_name}".strip()

        avatar_url = None
        if volunteer.avatar:
            request_obj = request._request if hasattr(request, '_request') else request
            avatar_url = request_obj.build_absolute_uri(volunteer.avatar.url)

        return Response({
            'volunteer': {
                'id': volunteer.id,
                'name': name or volunteer.username,
                'avatar': avatar_url,
            },
            'week_hours': top['week_hours'],
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра пользователей (admin / self)."""
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        if getattr(user, 'role', None) == UserRole.ADMIN or getattr(user, 'is_staff', False):
            return User.objects.all().order_by('id')
        return User.objects.filter(id=user.id)
