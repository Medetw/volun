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
        """Проверяем, что проект активен и есть свободные места."""
        if not value.is_active:
            raise serializers.ValidationError("Нельзя подать заявку на неактивный проект.")
        
        if value.volunteers_remaining <= 0:
            raise serializers.ValidationError("В проекте больше нет свободных мест.")
        
        return value
    
    def validate(self, attrs):
        """Проверяем, что волонтер еще не подавал заявку на этот проект."""
        user = self.context['request'].user
        project = attrs['project']
        
        if Application.objects.filter(volunteer=user, project=project).exists():
            raise serializers.ValidationError(
                "Вы уже подали заявку на этот проект."
            )
        
        return attrs


class ApplicationReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для рассмотрения заявок организацией."""
    class Meta:
        model = Application
        fields = ['status', 'review_comment']
    
    def validate_status(self, value):
        """Проверяем, что статус можно изменить."""
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
