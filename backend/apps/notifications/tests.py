from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.notifications.models import Notification, NotificationPreference, NotificationType
from apps.projects.models import Project, Category
from apps.applications.models import Application, ApplicationStatus

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='volunteer'
        )
        
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.SYSTEM,
            title='Test Notification',
            message='Test message'
        )

    def test_notification_creation(self):
        """Тест создания уведомления."""
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertEqual(self.notification.recipient, self.user)
        self.assertTrue(self.notification.is_unread)

    def test_mark_as_read(self):
        """Тест отметки как прочитанное."""
        self.notification.mark_as_read()
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)

    def test_mark_as_archived(self):
        """Тест архивирования."""
        self.notification.mark_as_archived()
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'archived')


class NotificationPreferenceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='volunteer'
        )

    def test_preferences_creation(self):
        """Тест создания настроек."""
        preferences = NotificationPreference.objects.create(user=self.user)
        self.assertEqual(preferences.user, self.user)
        self.assertTrue(preferences.email_application_approved)


class NotificationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='volunteer'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )

    def test_get_notifications_unauthorized(self):
        """Тест доступа без авторизации."""
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_notifications_authorized(self):
        """Тест получения уведомлений с авторизацией."""
        self.client.force_authenticate(user=self.user)
        
        # Создаем тестовое уведомление
        Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.SYSTEM,
            title='Test',
            message='Test message'
        )
        
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_mark_notification_as_read(self):
        """Тест отметки уведомления как прочитанного."""
        self.client.force_authenticate(user=self.user)
        
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.SYSTEM,
            title='Test',
            message='Test message'
        )
        
        response = self.client.post(f'/api/notifications/{notification.id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'read')

    def test_notification_stats(self):
        """Тест получения статистики."""
        self.client.force_authenticate(user=self.user)
        
        # Создаем несколько уведомлений
        Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.SYSTEM,
            title='Test 1',
            message='Test message 1'
        )
        Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.SYSTEM,
            title='Test 2',
            message='Test message 2',
            status='read'
        )
        
        response = self.client.get('/api/notifications/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(response.data['unread'], 1)
        self.assertEqual(response.data['read'], 1)

    def test_notification_preferences(self):
        """Тест настроек уведомлений."""
        self.client.force_authenticate(user=self.user)
        
        # Получаем настройки
        response = self.client.get('/api/notification-preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Обновляем настройки
        response = self.client.patch('/api/notification-preferences/', {
            'email_new_projects': True
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем изменения
        preferences = NotificationPreference.objects.get(user=self.user)
        self.assertTrue(preferences.email_new_projects)

    def test_admin_broadcast(self):
        """Тест рассылки уведомлений админом."""
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.post('/api/admin/notifications/broadcast/', {
            'title': 'System Maintenance',
            'message': 'System will be under maintenance',
            'notification_type': NotificationType.SYSTEM
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем что уведомления созданы для всех пользователей
        notifications_count = Notification.objects.filter(
            notification_type=NotificationType.SYSTEM
        ).count()
        self.assertGreater(notifications_count, 0)


class NotificationSignalTest(TestCase):
    def setUp(self):
        self.volunteer = User.objects.create_user(
            username='volunteer',
            email='volunteer@example.com',
            password='testpass123',
            role='volunteer'
        )
        
        self.organization = User.objects.create_user(
            username='organization',
            email='org@example.com',
            password='testpass123',
            role='organization'
        )
        
        self.category = Category.objects.create(name='Test Category')
        
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            organization=self.organization,
            category=self.category,
            volunteers_needed=5
        )

    def test_application_status_change_notification(self):
        """Тест уведомления при изменении статуса заявки."""
        # Создаем заявку
        application = Application.objects.create(
            volunteer=self.volunteer,
            project=self.project,
            status=ApplicationStatus.PENDING
        )
        
        # Изменяем статус
        application.status = ApplicationStatus.APPROVED
        application.save()
        
        # Проверяем что уведомление создано
        notification = Notification.objects.filter(
            recipient=self.volunteer,
            notification_type=NotificationType.APPLICATION_APPROVED
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertIn('одобрена', notification.title.lower())

    def test_new_project_notification(self):
        """Тест уведомления о новом проекте."""
        # Создаем новый активный проект
        new_project = Project.objects.create(
            title='New Project',
            description='New Description',
            organization=self.organization,
            category=self.category,
            volunteers_needed=3,
            status='active'
        )
        
        # Проверяем что уведомление создано
        notification = Notification.objects.filter(
            recipient=self.volunteer,
            notification_type=NotificationType.NEW_PROJECT,
            content_type__model='project',
            object_id=new_project.id
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertIn('Новый проект', notification.title)
