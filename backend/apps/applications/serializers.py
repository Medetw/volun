from rest_framework import serializers
from apps.applications.models import Application, ApplicationStatus
from apps.users.serializers import UserSerializer
from apps.projects.serializers import ProjectDetailSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для заявок."""
    volunteer = UserSerializer(read_only=True)
    project = ProjectDetailSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'volunteer', 'project', 'status', 'status_display',
            'cover_letter', 'hours_committed', 'created_at', 'updated_at',
            'reviewed_at', 'reviewed_by', 'review_comment',
            'is_pending', 'is_approved', 'can_be_cancelled'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'reviewed_at', 'reviewed_by'
        ]


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания заявок."""
    class Meta:
        model = Application
        fields = ['project', 'cover_letter', 'hours_committed']
    
    def validate_project(self, value):
        """Проверяем, что в проекте есть свободные места."""
        if value.volunteers_needed and value.volunteers_remaining <= 0:
            raise serializers.ValidationError("В проекте больше нет свободных мест.")
        
        return value
    
    def validate(self, attrs):
        """Проверяем, что волонтер еще не подавал заявку на этот проект."""
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        project = attrs.get('project')
        
        if user and project and Application.objects.filter(volunteer=user, project=project).exists():
            raise serializers.ValidationError(
                "Вы уже подали заявку на этот проект."
            )
        
        return attrs

    def create(self, validated_data):
        if 'volunteer' not in validated_data and 'request' in self.context:
            validated_data['volunteer'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для рассмотрения заявок организацией или обновления волонтером."""
    class Meta:
        model = Application
        fields = ['status', 'review_comment', 'cover_letter', 'hours_committed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and getattr(user, 'role', None) == 'volunteer':
            self.fields.pop('status', None)
            self.fields.pop('review_comment', None)
        elif user and getattr(user, 'role', None) in ['organization', 'admin']:
            self.fields.pop('cover_letter', None)
            self.fields.pop('hours_committed', None)

    def validate_status(self, value):
        """Проверяем, что статус можно изменить."""
        if not self.instance:
            return value
        current_status = self.instance.status
        
        if current_status != ApplicationStatus.PENDING:
            raise serializers.ValidationError(
                "Можно изменять только заявки со статусом 'Ожидает рассмотрения'."
            )
        
        if value not in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]:
            raise serializers.ValidationError(
                "Можно только принять или отклонить заявку."
            )
        
        return value

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and getattr(user, 'role', None) in ['organization', 'admin']:
            if 'status' in validated_data:
                instance.reviewed_by = user
                from django.utils import timezone
                instance.reviewed_at = timezone.now()
        return super().update(instance, validated_data)


class ApplicationListSerializer(serializers.ModelSerializer):
    """Сериализатор для списков заявок (минимальные данные)."""
    volunteer_name = serializers.CharField(source='volunteer.username', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'volunteer_name', 'project_title', 'status', 'status_display',
            'hours_committed', 'created_at', 'is_pending', 'is_approved'
        ]
