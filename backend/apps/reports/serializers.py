from rest_framework import serializers
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from apps.reports.models import ProjectReport, ReportStatus, VolunteerContribution
from apps.projects.models import Project
from apps.projects.serializers import ProjectDetailSerializer
from apps.users.serializers import UserSerializer


class VolunteerContributionSerializer(serializers.ModelSerializer):
    """Сериализатор для вклада волонтера."""
    volunteer_name = serializers.CharField(source='volunteer.username', read_only=True)
    report = serializers.PrimaryKeyRelatedField(queryset=ProjectReport.objects.all(), required=False)
    impact_description = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = VolunteerContribution
        fields = [
            'id', 'report', 'volunteer', 'volunteer_name', 'hours_contributed',
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

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'project' in data and 'project_id' not in data:
            data['project_id'] = data.get('project')
        return super().to_internal_value(data)

    def validate_project_id(self, value):
        """Проверяем, что проект существует."""
        try:
            project = Project.objects.get(id=value)
            if self.instance is None and ProjectReport.objects.filter(project=project).exists():
                raise serializers.ValidationError("Отчет для этого проекта уже существует")
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("Проект не найден")


class ProjectReportCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания отчетов."""
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    contributions = VolunteerContributionSerializer(many=True, required=False)
    total_volunteers_participated = serializers.IntegerField(min_value=0, required=False, default=0)
    total_volunteer_hours = serializers.IntegerField(min_value=0, required=False, default=0)
    beneficiaries_count = serializers.IntegerField(min_value=0, required=False, default=0)

    class Meta:
        model = ProjectReport
        fields = [
            'id', 'project', 'title', 'description',
            'goals_achieved', 'challenges_faced',
            'total_volunteers_participated', 'total_volunteer_hours', 'beneficiaries_count',
            'report_file', 'photos',
            'lessons_learned', 'future_plans',
            'contributions'
        ]

    def validate_project(self, project):
        if ProjectReport.objects.filter(project=project).exists():
            raise serializers.ValidationError("Отчет для этого проекта уже существует")
        
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            if user.role == 'organization' and project.organization != user:
                raise serializers.ValidationError("Вы можете создавать отчеты только для своих проектов")
        return project

    def create(self, validated_data):
        """Создаем отчет и связанные вклады волонтеров."""
        contributions_data = validated_data.pop('contributions', [])
        report = ProjectReport.objects.create(**validated_data)
        for contribution_data in contributions_data:
            VolunteerContribution.objects.create(report=report, **contribution_data)
        return report


class ProjectReportUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления отчетов."""
    contributions = VolunteerContributionSerializer(many=True, required=False)

    class Meta:
        model = ProjectReport
        fields = [
            'id', 'title', 'description',
            'goals_achieved', 'challenges_faced',
            'total_volunteers_participated', 'total_volunteer_hours', 'beneficiaries_count',
            'report_file', 'photos',
            'lessons_learned', 'future_plans',
            'status', 'review_comment',
            'contributions'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and getattr(user, 'role', None) != 'admin' and not getattr(user, 'is_staff', False):
            self.fields.pop('status', None)
            self.fields.pop('review_comment', None)

    def update(self, instance, validated_data):
        """Обновляем отчет и связанные вклады волонтеров."""
        contributions_data = validated_data.pop('contributions', None)
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and (getattr(user, 'role', None) == 'admin' or getattr(user, 'is_staff', False)):
            if 'status' in validated_data and validated_data['status'] in [ReportStatus.APPROVED, ReportStatus.REJECTED]:
                instance.reviewed_by = user
                instance.reviewed_at = timezone.now()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if contributions_data is not None:
            instance.contributions.all().delete()
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
