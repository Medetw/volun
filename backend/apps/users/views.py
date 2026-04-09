from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.users.models import VolunteerCertificate
from apps.users.serializers import VolunteerCertificateSerializer
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
