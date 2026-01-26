from rest_framework import views, permissions
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

# Используем прямые импорты для избежания circular dependencies
from apps.users.models import User, UserRole
from apps.projects.models import Project, ProjectStatus
from apps.applications.models import Application, ApplicationStatus


class StatisticsSimpleAPIView(views.APIView):
    """Простой но рабочий API для статистики."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Базовая статистика без сложных зависимостей."""
        user = request.user
        
        # Базовая статистика
        stats = {
            'users': {
                'total': User.objects.count(),
                'volunteers': User.objects.filter(role=UserRole.VOLUNTEER).count(),
                'organizations': User.objects.filter(role=UserRole.ORGANIZATION).count(),
                'admins': User.objects.filter(role=UserRole.ADMIN).count(),
                'active': User.objects.filter(is_active=True).count(),
                'recent': User.objects.filter(
                    date_joined__gte=timezone.now() - timedelta(days=30)
                ).count(),
            },
            'projects': {
                'total': Project.objects.count(),
                'active': Project.objects.filter(status=ProjectStatus.ACTIVE).count(),
                'draft': Project.objects.filter(status=ProjectStatus.DRAFT).count(),
                'completed': Project.objects.filter(status=ProjectStatus.COMPLETED).count(),
                'recent': Project.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).count(),
            },
            'applications': {
                'total': Application.objects.count(),
                'pending': Application.objects.filter(status=ApplicationStatus.PENDING).count(),
                'approved': Application.objects.filter(status=ApplicationStatus.APPROVED).count(),
                'rejected': Application.objects.filter(status=ApplicationStatus.REJECTED).count(),
                'recent': Application.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).count(),
            }
        }
        
        # Персональная статистика
        if user.role == UserRole.VOLUNTEER:
            apps = Application.objects.filter(volunteer=user)
            stats['my_applications'] = {
                'total': apps.count(),
                'approved': apps.filter(status=ApplicationStatus.APPROVED).count(),
                'total_hours': apps.filter(
                    status=ApplicationStatus.APPROVED
                ).aggregate(total=Sum('hours_committed'))['total'] or 0,
            }
        elif user.role == UserRole.ORGANIZATION:
            projects = Project.objects.filter(organization=user)
            apps = Application.objects.filter(project__organization=user)
            stats['my_projects'] = {
                'total': projects.count(),
                'active': projects.filter(status=ProjectStatus.ACTIVE).count(),
            }
            stats['my_applications'] = {
                'total': apps.count(),
                'pending': apps.filter(status=ApplicationStatus.PENDING).count(),
                'approved': apps.filter(status=ApplicationStatus.APPROVED).count(),
            }
        elif user.role == UserRole.ADMIN:
            stats['admin_stats'] = {
                'recent_activity': {
                    'new_users': User.objects.filter(
                        date_joined__gte=timezone.now() - timedelta(days=7)
                    ).count(),
                    'new_projects': Project.objects.filter(
                        created_at__gte=timezone.now() - timedelta(days=7)
                    ).count(),
                }
            }
        
        return Response(stats)
