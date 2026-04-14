from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from django.db.models.functions import TruncMonth

from apps.users.models import User, UserRole
from apps.projects.models import Project, ProjectStatus
from apps.applications.models import Application, ApplicationStatus


class StatisticsAPIView(views.APIView):
    """Оптимизированный API для получения статистики платформы."""
    permission_classes = [permissions.IsAuthenticated]
    
    # Кэширование статистики
    cache_timeout = 600  # 10 минут

    def get(self, request):
        """Получить статистику с кэшированием."""
        user = request.user
        cache_key = f'stats_{user.role}_{user.id}'
        
        # Пытаемся получить из кэша
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return Response(cached_stats)
        
        # Генерируем статистику
        stats = self._generate_stats(user)
        
        # Сохраняем в кэш
        cache.set(cache_key, stats, self.cache_timeout)
        
        return Response(stats)

    def _generate_stats(self, user):
        """Генерация статистики в зависимости от роли."""
        base_stats = {
            'users': self._get_users_stats(),
            'projects': self._get_projects_stats(),
            'applications': self._get_applications_stats(),
        }
        
        if user.role in (UserRole.ADMIN, 'moderator'):
            base_stats.update({
                'recent_activity': self._get_recent_activity(),
                'top_projects': self._get_top_projects(),
                'monthly_growth': self._get_monthly_growth(),
                'engagement_metrics': self._get_engagement_metrics(),
            })
        elif user.role == UserRole.ORGANIZATION:
            base_stats.update({
                'my_projects': self._get_organization_projects_stats(user),
                'my_applications': self._get_organization_applications_stats(user),
                'performance_metrics': self._get_organization_performance(user),
            })
        elif user.role == UserRole.VOLUNTEER:
            base_stats.update({
                'my_applications': self._get_volunteer_applications_stats(user),
                'recommended_projects': self._get_recommended_projects(user),
                'achievements': self._get_volunteer_achievements(user),
            })
        
        return base_stats

    def _get_users_stats(self):
        """Оптимизированная статистика пользователей."""
        cache_key = 'stats_users'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Один запрос вместо нескольких
        users_stats = User.objects.aggregate(
            total=Count('id'),
            volunteers=Count('id', filter=Q(role=UserRole.VOLUNTEER)),
            organizations=Count('id', filter=Q(role=UserRole.ORGANIZATION)),
            admins=Count('id', filter=Q(role=UserRole.ADMIN)),
            active=Count('id', filter=Q(is_active=True)),
            recent=Count('id', filter=Q(date_joined__gte=timezone.now() - timedelta(days=30)))
        )
        
        result = {
            'total': users_stats['total'],
            'volunteers': users_stats['volunteers'],
            'organizations': users_stats['organizations'],
            'admins': users_stats['admins'],
            'active': users_stats['active'],
            'recent': users_stats['recent'],
        }
        
        cache.set(cache_key, result, self.cache_timeout)
        return result

    def _get_projects_stats(self):
        """Оптимизированная статистика проектов."""
        cache_key = 'stats_projects'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        projects_stats = Project.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(status=ProjectStatus.ACTIVE)),
            draft=Count('id', filter=Q(status=ProjectStatus.DRAFT)),
            completed=Count('id', filter=Q(status=ProjectStatus.COMPLETED)),
            cancelled=Count('id', filter=Q(status=ProjectStatus.CANCELLED)),
            recent=Count('id', filter=Q(created_at__gte=timezone.now() - timedelta(days=30))),
            total_volunteers_needed=Sum('volunteers_needed')
        )
        
        result = {
            'total': projects_stats['total'],
            'active': projects_stats['active'],
            'draft': projects_stats['draft'],
            'completed': projects_stats['completed'],
            'cancelled': projects_stats['cancelled'],
            'recent': projects_stats['recent'],
            'total_volunteers_needed': projects_stats['total_volunteers_needed'] or 0,
        }
        
        cache.set(cache_key, result, self.cache_timeout)
        return result

    def _get_applications_stats(self):
        """Оптимизированная статистика заявок."""
        cache_key = 'stats_applications'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        apps_stats = Application.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=ApplicationStatus.PENDING)),
            approved=Count('id', filter=Q(status=ApplicationStatus.APPROVED)),
            rejected=Count('id', filter=Q(status=ApplicationStatus.REJECTED)),
            cancelled=Count('id', filter=Q(status=ApplicationStatus.CANCELLED)),
            recent=Count('id', filter=Q(created_at__gte=timezone.now() - timedelta(days=30))),
            total_hours=Sum('hours_committed', filter=Q(status=ApplicationStatus.APPROVED))
        )
        
        result = {
            'total': apps_stats['total'],
            'pending': apps_stats['pending'],
            'approved': apps_stats['approved'],
            'rejected': apps_stats['rejected'],
            'cancelled': apps_stats['cancelled'],
            'recent': apps_stats['recent'],
            'total_hours': apps_stats['total_hours'] or 0,
        }
        
        cache.set(cache_key, result, self.cache_timeout)
        return result

    def _get_recent_activity(self):
        """Статистика последней активности."""
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

    def _get_top_projects(self):
        """Топ проекты с оптимизацией."""
        return list(
            Project.objects.filter(
                status=ProjectStatus.ACTIVE
            ).annotate(
                applications_count=Count('applications')
            ).order_by('-applications_count')[:10]
            .values('id', 'title', 'applications_count', 'volunteers_needed')
        )

    def _get_monthly_growth(self):
        """Месячный рост с оптимизацией."""
        six_months_ago = timezone.now() - timedelta(days=180)
        
        # Оптимизированный запрос с TruncMonth
        monthly_data = User.objects.filter(
            date_joined__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date_joined')
        ).values('month').annotate(
            users=Count('id')
        ).order_by('month')
        
        projects_monthly = Project.objects.filter(
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            projects=Count('id')
        ).order_by('month')
        
        return {
            'users': [
                {'month': item['month'].strftime('%Y-%m'), 'users': item['users']}
                for item in monthly_data
            ],
            'projects': [
                {'month': item['month'].strftime('%Y-%m'), 'projects': item['projects']}
                for item in projects_monthly
            ]
        }

    def _get_engagement_metrics(self):
        """Метрики вовлеченности для админа."""
        return {
            'avg_applications_per_project': Application.objects.count() / max(Project.objects.count(), 1),
            'approval_rate': self._calculate_approval_rate(),
            'active_volunteers': User.objects.filter(
                role=UserRole.VOLUNTEER,
                applications__status=ApplicationStatus.APPROVED
            ).distinct().count(),
        }

    def _calculate_approval_rate(self):
        """Расчет рейтинга одобрения."""
        total = Application.objects.count()
        approved = Application.objects.filter(status=ApplicationStatus.APPROVED).count()
        return round((approved / max(total, 1)) * 100, 2)

    def _get_organization_projects_stats(self, user):
        """Статистика проектов организации."""
        projects = Project.objects.filter(organization=user)
        
        return {
            'total': projects.count(),
            'active': projects.filter(status=ProjectStatus.ACTIVE).count(),
            'completed': projects.filter(status=ProjectStatus.COMPLETED).count(),
            'total_volunteers_needed': projects.aggregate(
                total=Sum('volunteers_needed')
            )['total'] or 0,
            'total_volunteers_joined': Application.objects.filter(
                project__organization=user,
                status=ApplicationStatus.APPROVED
            ).count(),
        }

    def _get_organization_applications_stats(self, user):
        """Статистика заявок организации."""
        applications = Application.objects.filter(project__organization=user)
        
        return {
            'total': applications.count(),
            'pending': applications.filter(status=ApplicationStatus.PENDING).count(),
            'approved': applications.filter(status=ApplicationStatus.APPROVED).count(),
            'rejected': applications.filter(status=ApplicationStatus.REJECTED).count(),
        }

    def _get_organization_performance(self, user):
        """Метрики производительности организации."""
        projects = Project.objects.filter(organization=user)
        
        return {
            'avg_time_to_approve': self._calculate_avg_approval_time(user),
            'completion_rate': self._calculate_completion_rate(user),
            'volunteer_satisfaction': self._calculate_satisfaction_rate(user),
        }

    def _get_volunteer_applications_stats(self, user):
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

    def _get_recommended_projects(self, user):
        """Рекомендованные проекты для волонтера."""
        volunteer_profile = getattr(user, 'volunteer_profile', None)
        
        if not volunteer_profile:
            return []
        
        # Оптимизированный запрос
        projects = Project.objects.filter(
            status=ProjectStatus.ACTIVE
        ).annotate(
            volunteers_count=Count('applications', filter=Q(applications__status=ApplicationStatus.APPROVED)),
            volunteers_remaining=F('volunteers_needed') - Count('applications', filter=Q(applications__status=ApplicationStatus.APPROVED))
        ).filter(
            volunteers_remaining__gt=0
        )
        
        if volunteer_profile.region:
            projects = projects.filter(region__name=volunteer_profile.region)
        
        # Исключаем проекты с уже поданными заявками
        applied_projects = Application.objects.filter(
            volunteer=user
        ).values_list('project_id', flat=True)
        
        projects = projects.exclude(id__in=applied_projects)
        
        return list(
            projects[:5].values(
                'id', 'title', 'description', 'category__name', 
                'region__name', 'volunteers_remaining'
            )
        )

    def _get_volunteer_achievements(self, user):
        """Достижения волонтера."""
        from apps.reports.models import VolunteerContribution

        applications = Application.objects.filter(
            volunteer=user,
            status=ApplicationStatus.APPROVED
        )

        avg_rating = VolunteerContribution.objects.filter(
            volunteer=user
        ).aggregate(avg=Avg('performance_rating'))['avg']

        return {
            'total_projects': applications.values('project').distinct().count(),
            'total_hours': applications.aggregate(
                total=Sum('hours_committed')
            )['total'] or 0,
            'average_rating': round(avg_rating, 1) if avg_rating else 0,
            'longest_streak': self._calculate_longest_streak(user),
            'diversity_score': self._calculate_diversity_score(user),
        }

    def _calculate_avg_approval_time(self, user):
        """Среднее время одобрения для организации."""
        # Реализация расчета среднего времени
        return 24  # часов (заглушка)

    def _calculate_completion_rate(self, user):
        """Рейтинг завершения проектов."""
        total = Project.objects.filter(organization=user).count()
        completed = Project.objects.filter(
            organization=user, 
            status=ProjectStatus.COMPLETED
        ).count()
        return round((completed / max(total, 1)) * 100, 2)

    def _calculate_satisfaction_rate(self, user):
        """Рейтинг удовлетворенности волонтеров."""
        return 85.5  # заглушка

    def _calculate_longest_streak(self, user):
        """Самый длинный streak участия."""
        return 7  # дней (заглушка)

    def _calculate_diversity_score(self, user):
        """Оценка разнообразия категорий."""
        return 8.5  # из 10 (заглушка)
