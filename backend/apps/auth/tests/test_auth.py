from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import UserRole

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    """Тесты аутентификации."""

    def test_volunteer_registration(self):
        """Тест регистрации волонтера."""
        data = {
            'email': 'volunteer@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Иван',
            'last_name': 'Петров',
            'city': 'Алматы'
        }
        response = self.client.post('/api/auth/register/volunteer/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='volunteer@test.com').exists())
        
        user = User.objects.get(email='volunteer@test.com')
        self.assertEqual(user.role, UserRole.VOLUNTEER)
        self.assertTrue(hasattr(user, 'volunteer_profile'))

    def test_organization_registration(self):
        """Тест регистрации организации."""
        data = {
            'email': 'org@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'name': 'Тестовая организация',
            'organization_type': 'ngo',
            'description': 'Описание'
        }
        response = self.client.post('/api/auth/register/organization/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(email='org@test.com')
        self.assertEqual(user.role, UserRole.ORGANIZATION)
        self.assertTrue(hasattr(user, 'organization_profile'))

    def test_login(self):
        """Тест входа."""
        # Создаем пользователя
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='test@example.com'
        )
        
        data = {'email': 'test@example.com', 'password': 'testpass123'}
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_get_current_user(self):
        """Тест получения текущего пользователя."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='test@example.com'
        )
        
        # Логинимся и получаем токен
        response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        token = response.data['tokens']['access']
        
        # Запрашиваем текущего пользователя
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
