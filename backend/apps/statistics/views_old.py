from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, UserRole
from apps.projects.models import Project, ProjectStatus
from apps.applications.models import Application, ApplicationStatus


class StatisticsAPIView(views.APIView):
    """API для получения статистики платформы."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Получить общую статистику платформы."""
        user = request.user
        
        # Базовая статистика для всех
        stats = {
            'users': self.get_users_stats(),
            'projects': self.get_projects_stats(),
            'applications': self.get_applications_stats(),
        }
        
        # Дополнительная статистика для админов
        if user.role == UserRole.ADMIN:
            stats.update({
                'recent_activity': self.get_recent_activity(),
                'top_projects': self.get_top_projects(),
                'monthly_growth': self.get_monthly_growth(),
            })
        
        # Статистика для организаций
        elif user.role == UserRole.ORGANIZATION:
            stats.update({
                'my_projects': self.get_organization_projects_stats(user),
                'my_applications': self.get_organization_applications_stats(user),
            })
        
        # Статистика для волонтеров
        elif user.role == UserRole.VOLUNTEER:
            stats.update({
                'my_applications': self.get_volunteer_applications_stats(user),
                'recommended_projects': self.get_recommended_projects(user),
            })
        
        return Response(stats)

    def get_users_stats(self):
        """Статистика пользователей."""
        return {
            'total': User.objects.count(),
            'volunteers': User.objects.filter(role=UserRole.VOLUNTEER).count(),
            'organizations': User.objects.filter(role=UserRole.ORGANIZATION).count(),
            'admins': User.objects.filter(role=UserRole.ADMIN).count(),
            'active': User.objects.filter(is_active=True).count(),
            'recent': User.objects.filter(
                date_joined__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }

    def get_projects_stats(self):
        """Статистика проектов."""
        return {
            'total': Project.objects.count(),
            'active': Project.objects.filter(status=ProjectStatus.ACTIVE).count(),
            'draft': Project.objects.filter(status=ProjectStatus.DRAFT).count(),
            'completed': Project.objects.filter(status=ProjectStatus.COMPLETED).count(),
            'cancelled': Project.objects.filter(status=ProjectStatus.CANCELLED).count(),
            'recent': Project.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }

    def get_applications_stats(self):
        """Статистика заявок."""
        return {
            'total': Application.objects.count(),
            'pending': Application.objects.filter(status=ApplicationStatus.PENDING).count(),
            'approved': Application.objects.filter(status=ApplicationStatus.APPROVED).count(),
            'rejected': Application.objects.filter(status=ApplicationStatus.REJECTED).count(),
            'cancelled': Application.objects.filter(status=ApplicationStatus.CANCELLED).count(),
            'recent': Application.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }

    def get_recent_activity(self):
        """Последняя активность на платформе."""
        return {
            'new_users': User.objects.filter(
                date_joined__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'new_projects': Project.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'new_applications': Application.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }

    def get_top_projects(self):
        """Топ проекты по количеству заявок."""
        return list(
            Project.objects.filter(
                status=ProjectStatus.ACTIVE
            ).annotate(
                applications_count=Count('applications')
            ).order_by('-applications_count')[:10]
            .values('id', 'title', 'applications_count', 'volunteers_needed')
        )

    def get_monthly_growth(self):
        """Месячный рост платформы."""
        six_months_ago = timezone.now() - timedelta(days=180)
        
        users_growth = []
        projects_growth = []
        
        for i in range(6):
            month_start = six_months_ago + timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            
            users_count = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lt=month_end
            ).count()
            
            projects_count = Project.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            users_growth.append({
                'month': month_start.strftime('%Y-%m'),
                'users': users_count
            })
            
            projects_growth.append({
                'month': month_start.strftime('%Y-%m'),
                'projects': projects_count
            })
        
        return {
            'users': users_growth,
            'projects': projects_growth
        }

    def get_organization_projects_stats(self, user):
        """Статистика проектов организации."""
        projects = Project.objects.filter(organization=user)
        
        return {
            'total': projects.count(),
            'active': projects.filter(status=ProjectStatus.ACTIVE).count(),
            'completed': projects.filter(status=ProjectStatus.COMPLETED).count(),
            'total_volunteers_needed': projects.aggregate(
                total=Sum('volunteers_needed')
            )['total'] or 0,
            'total_volunteers_joined': sum(
                project.applications.filter(status=ApplicationStatus.APPROVED).count()
                for project in projects
            ),
        }

    def get_organization_applications_stats(self, user):
        """Статистика заявок на проекты организации."""
        applications = Application.objects.filter(project__organization=user)
        
        return {
            'total': applications.count(),
            'pending': applications.filter(status=ApplicationStatus.PENDING).count(),
            'approved': applications.filter(status=ApplicationStatus.APPROVED).count(),
            'rejected': applications.filter(status=ApplicationStatus.REJECTED).count(),
        }

    def get_volunteer_applications_stats(self, user):
        """Статистика заявок волонтера."""
        applications = Application.objects.filter(volunteer=user)
        
        return {
            'total': applications.count(),
            'pending': applications.filter(status=ApplicationStatus.PENDING).count(),
            'approved': applications.filter(status=ApplicationStatus.APPROVED).count(),
            'rejected': applications.filter(status=ApplicationStatus.REJECTED).count(),
            'total_hours': applications.filter(
                status=ApplicationStatus.APPROVED
            ).aggregate(total=Sum('hours_committed'))['total'] or 0,
        }

    def get_recommended_projects(self, user):
        """Рекомендованные проекты для волонтера."""
        # Простая рекомендация на основе интересов и региона
        volunteer_profile = getattr(user, 'volunteer_profile', None)
        
        if not volunteer_profile:
            return []
        
        projects = Project.objects.filter(
            status=ProjectStatus.ACTIVE
        ).filter(
            volunteers_remaining__gt=0
        )
        
        # Фильтрация по региону если указан
        if volunteer_profile.region:
            projects = projects.filter(region__name=volunteer_profile.region)
        
        # Исключаем проекты на которые уже подана заявка
        applied_projects = Application.objects.filter(
            volunteer=user
        ).values_list('project_id', flat=True)
        
        projects = projects.exclude(id__in=applied_projects)
        
        return list(
            projects[:5].values(
                'id', 'title', 'excerpt', 'category__name', 
                'region__name', 'volunteers_remaining'
            )
        )
