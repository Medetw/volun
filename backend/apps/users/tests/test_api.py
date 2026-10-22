import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User, UserRole


@pytest.mark.django_db
class TestAuthAPI:
    """Test authentication API endpoints."""

    def test_register_volunteer(self, api_client, mock_email_backend):
        """Test volunteer registration."""
        url = reverse('auth-register-volunteer')
        data = {
            'username': 'newvolunteer',
            'email': 'volunteer@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'phone': '+1234567890',
            'first_name': 'John',
            'last_name': 'Doe',
            'city': 'Almaty',
            'region': 'Almaty'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        user = User.objects.get(username='newvolunteer')
        assert user.role == UserRole.VOLUNTEER
        assert hasattr(user, 'volunteer_profile')
        assert user.volunteer_profile.first_name == 'John'
        
        # Check tokens in response
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data

    def test_register_organization(self, api_client, mock_email_backend):
        """Test organization registration."""
        url = reverse('auth-register-organization')
        data = {
            'username': 'neworg',
            'email': 'org@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'phone': '+1234567891',
            'name': 'Test Organization',
            'organization_type': 'ngo',
            'description': 'Test description',
            'city': 'Almaty',
            'region': 'Almaty'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        user = User.objects.get(username='neworg')
        assert user.role == UserRole.ORGANIZATION
        assert hasattr(user, 'organization_profile')
        assert user.organization_profile.name == 'Test Organization'

    def test_login(self, api_client, volunteer_user):
        """Test user login."""
        url = reverse('auth-login')
        data = {
            'username': volunteer_user.username,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == volunteer_user.username

    def test_login_invalid_credentials(self, api_client, volunteer_user):
        """Test login with invalid credentials."""
        url = reverse('auth-login')
        data = {
            'username': volunteer_user.username,
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout(self, auth_volunteer_client, volunteer_user):
        """Test user logout."""
        url = reverse('auth-logout')
        response = auth_volunteer_client.post(url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_current_user(self, auth_volunteer_client, volunteer_user):
        """Test getting current user info."""
        url = reverse('auth-me')
        response = auth_volunteer_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        assert response.data['username'] == volunteer_user.username
        assert response.data['email'] == volunteer_user.email
        assert response.data['role'] == volunteer_user.role

    def test_get_current_user_unauthenticated(self, api_client):
        """Test getting current user without authentication."""
        url = reverse('auth-me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, auth_volunteer_client, volunteer_user):
        """Test updating user profile."""
        url = reverse('auth-me-update')
        data = {
            'phone': '+9876543210',
            'volunteer_profile': {
                'first_name': 'Updated Name',
                'city': 'Updated City'
            }
        }
        
        response = auth_volunteer_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        volunteer_user.refresh_from_db()
        assert volunteer_user.phone == '+9876543210'
        assert volunteer_user.volunteer_profile.first_name == 'Updated Name'

    def test_password_reset_request(self, api_client, volunteer_user, mock_email_backend):
        """Test password reset request."""
        url = reverse('auth-password-reset')
        data = {'email': volunteer_user.email}
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        mock_email_backend.assert_called_once()

    def test_password_reset_confirm(self, api_client, volunteer_user):
        """Test password reset confirmation."""
        # Set reset code
        volunteer_user.password_reset_code = '123456'
        volunteer_user.save()
        
        url = reverse('auth-password-reset-confirm')
        data = {
            'email': volunteer_user.email,
            'reset_code': '123456',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        volunteer_user.refresh_from_db()
        assert volunteer_user.check_password('newpass123')
        assert volunteer_user.password_reset_code is None

    def test_change_password(self, auth_volunteer_client, volunteer_user):
        """Test changing password."""
        url = reverse('auth-password-change')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = auth_volunteer_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        volunteer_user.refresh_from_db()
        assert volunteer_user.check_password('newpass123')

    def test_change_password_wrong_old_password(self, auth_volunteer_client, volunteer_user):
        """Test changing password with wrong old password."""
        url = reverse('auth-password-change')
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = auth_volunteer_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserAPI:
    """Test user-related API endpoints."""

    def test_user_list_admin_only(self, auth_admin_client, admin_user, volunteer_user):
        """Test that only admin can list users."""
        url = reverse('user-list')
        response = auth_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2  # admin + volunteer

    def test_user_list_forbidden(self, auth_volunteer_client):
        """Test that non-admin cannot list users."""
        url = reverse('user-list')
        response = auth_volunteer_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_detail_admin(self, auth_admin_client, volunteer_user):
        """Test getting user detail as admin."""
        url = reverse('user-detail', kwargs={'pk': volunteer_user.pk})
        response = auth_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == volunteer_user.username

    def test_user_detail_self(self, auth_volunteer_client, volunteer_user):
        """Test getting own user detail."""
        url = reverse('user-detail', kwargs={'pk': volunteer_user.pk})
        response = auth_volunteer_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_user_detail_other_forbidden(self, auth_volunteer_client, organization_user):
        """Test getting other user's detail is forbidden."""
        url = reverse('user-detail', kwargs={'pk': organization_user.pk})
        response = auth_volunteer_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # IsFiltered for non-admin
