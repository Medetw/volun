from rest_framework import serializers
from django.core.validators import MaxValueValidator
from django.utils import timezone
from apps.reports.models import ProjectReport, ReportStatus, VolunteerContribution
from apps.projects.serializers import ProjectDetailSerializer
from apps.users.serializers import UserSerializer


class VolunteerContributionSerializer(serializers.ModelSerializer):
    """Сериализатор для вклада волонтера."""
    volunteer_name = serializers.CharField(source='volunteer.username', read_only=True)
    
    class Meta:
        model = VolunteerContribution
        fields = [
            'id', 'volunteer', 'volunteer_name', 'hours_contributed',
            'tasks_completed', 'impact_description', 'performance_rating', 'feedback'
        ]


class ProjectReportSerializer(serializers.ModelSerializer):
    """Сериализатор для отчетов по проектам."""
    project = ProjectDetailSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contributions = VolunteerContributionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProjectReport
        fields = [
            'id', 'project', 'project_id', 'title', 'description',
            'goals_achieved', 'challenges_faced',
            'total_volunteers_participated', 'total_volunteer_hours', 'beneficiaries_count',
            'report_file', 'photos',
            'lessons_learned', 'future_plans',
            'status', 'status_display',
            'reviewed_by', 'reviewed_by_name', 'review_comment',
            'created_at', 'updated_at', 'submitted_at', 'reviewed_at',
            'contributions', 'is_submitted', 'is_approved'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'submitted_at', 'reviewed_at',
            'reviewed_by', 'reviewed_by_name'
        ]

    def validate_project_id(self, value):
        """Проверяем, что проект существует и принадлежит организации."""
        from apps.projects.models import Project
        
        try:
            project = Project.objects.get(id=value)
            
            # Проверяем, что пользователь - владелец проекта или админ
            user = self.context['request'].user
            if user.role != 'admin' and project.organization != user:
                raise serializers.ValidationError(
                    "Вы можете создавать отчеты только для своих проектов"
                )
            
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("Проект не найден")

    def validate(self, attrs):
        """Валидация данных отчета."""
        # Проверяем, что количество волонтеров не превышает количество заявок
        project_id = attrs.get('project_id')
        if project_id:
            from apps.projects.models import Project
            from apps.applications.models import Application
            
            project = Project.objects.get(id=project_id)
            total_volunteers = attrs.get('total_volunteers_participated', 0)
            approved_applications = Application.objects.filter(
                project=project, status='approved'
            ).count()
            
            if total_volunteers > approved_applications:
                raise serializers.ValidationError({
                    'total_volunteers_participated': 
                    f'Количество волонтеров не может превышать количество одобренных заявок ({approved_applications})'
                })
        
        return attrs


class ProjectReportCreateSerializer(ProjectReportSerializer):
    """Сериализатор для создания отчетов."""
    contributions = VolunteerContributionSerializer(many=True, required=False)

    def create(self, validated_data):
        """Создаем отчет и связанные вклады волонтеров."""
        contributions_data = validated_data.pop('contributions', [])
        
        report = ProjectReport.objects.create(**validated_data)
        
        # Создаем вклады волонтеров
        for contribution_data in contributions_data:
            VolunteerContribution.objects.create(report=report, **contribution_data)
        
        return report


class ProjectReportUpdateSerializer(ProjectReportSerializer):
    """Сериализатор для обновления отчетов."""
    contributions = VolunteerContributionSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        """Обновляем отчет и связанные вклады волонтеров."""
        contributions_data = validated_data.pop('contributions', None)
        
        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновляем вклады волонтеров
        if contributions_data is not None:
            # Удаляем старые вклады
            instance.contributions.all().delete()
            
            # Создаем новые
            for contribution_data in contributions_data:
                VolunteerContribution.objects.create(report=instance, **contribution_data)
        
        return instance


class ReportReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модерации отчетов."""
    class Meta:
        model = ProjectReport
        fields = ['status', 'review_comment']

    def validate_status(self, value):
        """Проверяем, что статус можно изменить."""
        current_status = self.instance.status
        
        if current_status != ReportStatus.SUBMITTED:
            raise serializers.ValidationError(
                "Можно изменять только отправленные отчеты"
            )
        
        if value not in [ReportStatus.APPROVED, ReportStatus.REJECTED]:
            raise serializers.ValidationError(
                "Можно только одобрить или отклонить отчет"
            )
        
        return value


class ReportStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики отчетов."""
    total_reports = serializers.IntegerField(read_only=True)
    draft_reports = serializers.IntegerField(read_only=True)
    submitted_reports = serializers.IntegerField(read_only=True)
    approved_reports = serializers.IntegerField(read_only=True)
    rejected_reports = serializers.IntegerField(read_only=True)
    total_volunteer_hours = serializers.IntegerField(read_only=True)
    total_beneficiaries = serializers.IntegerField(read_only=True)
