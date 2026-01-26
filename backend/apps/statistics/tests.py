from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project, ProjectStatus
from apps.applications.models import Application, ApplicationStatus

User = get_user_model()


class StatisticsAPITest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password',
            role='admin'
        )
        
        self.volunteer_user = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='password',
            role='volunteer'
        )
        
        self.organization_user = User.objects.create_user(
            username='organization',
            email='organization@example.com',
            password='password',
            role='organization'
        )
        
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            organization=self.organization_user,
            volunteers_needed=5,
            status=ProjectStatus.ACTIVE
        )
        
        self.application = Application.objects.create(
            volunteer=self.volunteer_user,
            project=self.project,
            status=ApplicationStatus.APPROVED,
            hours_committed=10
        )

    def test_statistics_for_admin(self):
        """Тест статистики для админа."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/statistics/')
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        self.assertIn('users', data)
        self.assertIn('projects', data)
        self.assertIn('applications', data)
        self.assertIn('recent_activity', data)
        self.assertIn('top_projects', data)
        self.assertIn('monthly_growth', data)
        
        # Проверяем базовую статистику
        self.assertEqual(data['users']['total'], 3)
        self.assertEqual(data['users']['volunteers'], 1)
        self.assertEqual(data['users']['organizations'], 1)
        self.assertEqual(data['projects']['total'], 1)
        self.assertEqual(data['applications']['total'], 1)

    def test_statistics_for_volunteer(self):
        """Тест статистики для волонтера."""
        self.client.force_authenticate(user=self.volunteer_user)
        response = self.client.get('/api/statistics/')
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        self.assertIn('my_applications', data)
        self.assertIn('recommended_projects', data)
        
        # Проверяем статистику заявок волонтера
        self.assertEqual(data['my_applications']['total'], 1)
        self.assertEqual(data['my_applications']['approved'], 1)
        self.assertEqual(data['my_applications']['total_hours'], 10)

    def test_statistics_for_organization(self):
        """Тест статистики для организации."""
        self.client.force_authenticate(user=self.organization_user)
        response = self.client.get('/api/statistics/')
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        self.assertIn('my_projects', data)
        self.assertIn('my_applications', data)
        
        # Проверяем статистику проектов организации
        self.assertEqual(data['my_projects']['total'], 1)
        self.assertEqual(data['my_projects']['active'], 1)
        
        # Проверяем статистику заявок на проекты организации
        self.assertEqual(data['my_applications']['total'], 1)
        self.assertEqual(data['my_applications']['approved'], 1)

    def test_statistics_unauthorized(self):
        """Тест доступа без авторизации."""
        response = self.client.get('/api/statistics/')
        self.assertEqual(response.status_code, 401)
