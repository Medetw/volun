from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, permissions, views, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from apps.users.models import User, UserRole, VolunteerCertificate, VolunteerHoursLog, VolunteerProfile
from apps.users.serializers import VolunteerCertificateSerializer, VolunteerHoursLogSerializer
from apps.core.logging import logger


class VolunteerCertificateViewSet(viewsets.ModelViewSet):
    """ViewSet для управления сертификатами волонтёра."""
    serializer_class = VolunteerCertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """Волонтёр видит только свои сертификаты, админ — все."""
        user = self.request.user
        if user.role == 'admin':
            return VolunteerCertificate.objects.all()
        return VolunteerCertificate.objects.filter(volunteer=user)

    def perform_create(self, serializer):
        """При создании устанавливаем волонтёра."""
        serializer.save(volunteer=self.request.user)
        logger.user_action(
            action="CERTIFICATE_UPLOADED",
            user_id=self.request.user.id,
            details={'title': serializer.instance.title}
        )

    def perform_destroy(self, instance):
        """Логируем удаление сертификата."""
        logger.user_action(
            action="CERTIFICATE_DELETED",
            user_id=self.request.user.id,
            details={'title': instance.title, 'certificate_id': instance.id}
        )
        instance.delete()


class VolunteerHoursViewSet(viewsets.ModelViewSet):
    """ViewSet для учёта волонтёрских часов (только модератор/админ создаёт)."""
    serializer_class = VolunteerHoursLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (UserRole.MODERATOR, UserRole.ADMIN):
            # Модератор и админ видят все записи; можно фильтровать по волонтёру
            volunteer_id = self.request.query_params.get('volunteer_id')
            qs = VolunteerHoursLog.objects.select_related('volunteer', 'moderator')
            if volunteer_id:
                qs = qs.filter(volunteer_id=volunteer_id)
            return qs
        # Волонтёр видит только свои записи
        return VolunteerHoursLog.objects.filter(volunteer=user).select_related('moderator')

    def create(self, request, *args, **kwargs):
        if request.user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            return Response(
                {'error': 'Только модератор или администратор может вносить часы'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save(moderator=self.request.user)
        # Обновляем счётчик часов в профиле волонтёра
        profile = getattr(instance.volunteer, 'volunteer_profile', None)
        if profile:
            total = VolunteerHoursLog.objects.filter(
                volunteer=instance.volunteer
            ).aggregate(total=Sum('hours'))['total'] or 0
            profile.volunteer_hours = total
            profile.save(update_fields=['volunteer_hours'])

    def update(self, request, *args, **kwargs):
        if request.user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            return Response(
                {'error': 'Только модератор или администратор может изменять записи'},
                status=status.HTTP_403_FORBIDDEN
            )
        response = super().update(request, *args, **kwargs)
        # Пересчитываем часы
        instance = self.get_object()
        profile = getattr(instance.volunteer, 'volunteer_profile', None)
        if profile:
            total = VolunteerHoursLog.objects.filter(
                volunteer=instance.volunteer
            ).aggregate(total=Sum('hours'))['total'] or 0
            profile.volunteer_hours = total
            profile.save(update_fields=['volunteer_hours'])
        return response

    def destroy(self, request, *args, **kwargs):
        if request.user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            return Response(
                {'error': 'Только модератор или администратор может удалять записи'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        volunteer = instance.volunteer
        instance.delete()
        profile = getattr(volunteer, 'volunteer_profile', None)
        if profile:
            total = VolunteerHoursLog.objects.filter(
                volunteer=volunteer
            ).aggregate(total=Sum('hours'))['total'] or 0
            profile.volunteer_hours = total
            profile.save(update_fields=['volunteer_hours'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class VolunteerListView(views.APIView):
    """Список волонтёров для выбора в форме модератора."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            return Response(
                {'error': 'Доступ только для модераторов и администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        volunteers = User.objects.filter(
            role=UserRole.VOLUNTEER, is_active=True
        ).select_related('volunteer_profile').order_by('username')

        data = []
        for v in volunteers:
            profile = getattr(v, 'volunteer_profile', None)
            name = ''
            if profile:
                name = f"{profile.first_name} {profile.last_name}".strip()
            data.append({
                'id': v.id,
                'username': v.username,
                'name': name or v.username,
                'volunteer_hours': profile.volunteer_hours if profile else 0,
            })
        return Response(data)


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
