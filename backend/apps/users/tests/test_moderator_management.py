"""
Block 7: admin создаёт/удаляет модераторов.
"""
import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, ModeratorProfile


URL = "/api/users/moderators/"


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


def _auth(c, u):
    token = RefreshToken.for_user(u)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin(db):
    return User.objects.create_user(username="adm", email="a@e.com", password="p", role="admin")


@pytest.fixture
def moderator(db):
    u = User.objects.create_user(username="mod", email="m@e.com", password="p", role="moderator")
    ModeratorProfile.objects.create(user=u, department="Общий")
    return u


@pytest.fixture
def volunteer(db):
    return User.objects.create_user(username="vol", email="v@e.com", password="p", role="volunteer")


class TestListModerators:

    def test_admin_can_list(self, api_client, admin, moderator):
        _auth(api_client, admin)
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["username"] == "mod"
        assert resp.data[0]["department"] == "Общий"

    def test_moderator_cannot_list(self, api_client, moderator):
        _auth(api_client, moderator)
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_volunteer_cannot_list(self, api_client, volunteer):
        _auth(api_client, volunteer)
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_denied(self, api_client):
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateModerator:

    VALID = {
        "username": "newmod",
        "email": "nm@e.com",
        "password": "strong_pass_123",
        "department": "IT",
    }

    def test_admin_creates_moderator(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.post(URL, self.VALID, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newmod", role="moderator").exists()
        assert ModeratorProfile.objects.filter(user__username="newmod").exists()

    def test_created_user_can_login(self, api_client, admin):
        _auth(api_client, admin)
        api_client.post(URL, self.VALID, format="json")
        u = User.objects.get(username="newmod")
        assert u.check_password("strong_pass_123")

    def test_non_admin_cannot_create(self, api_client, moderator):
        _auth(api_client, moderator)
        resp = api_client.post(URL, self.VALID, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_reject_short_password(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.post(URL, {**self.VALID, "password": "short"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_reject_duplicate_username(self, api_client, admin, moderator):
        _auth(api_client, admin)
        resp = api_client.post(URL, {**self.VALID, "username": "mod"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_reject_duplicate_email(self, api_client, admin, moderator):
        _auth(api_client, admin)
        resp = api_client.post(URL, {**self.VALID, "email": "m@e.com"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_reject_missing_fields(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.post(URL, {"username": "x"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_custom_rbac_flags(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.post(URL, {
            **self.VALID,
            "can_view_volunteers": False,
            "can_manage_hours": True,
            "can_manage_certificates": False,
        }, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        p = ModeratorProfile.objects.get(user__username="newmod")
        assert p.can_view_volunteers is False
        assert p.can_manage_hours is True
        assert p.can_manage_certificates is False


class TestDeleteModerator:

    def test_admin_removes_moderator(self, api_client, admin, moderator):
        _auth(api_client, admin)
        resp = api_client.delete(f"{URL}{moderator.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        moderator.refresh_from_db()
        assert moderator.role == "volunteer"  # soft downgrade
        assert not ModeratorProfile.objects.filter(user=moderator).exists()

    def test_non_admin_cannot_remove(self, api_client, moderator):
        _auth(api_client, moderator)
        resp = api_client.delete(f"{URL}{moderator.id}/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_remove_nonexistent(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.delete(f"{URL}99999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_non_moderator_user_404(self, api_client, admin, volunteer):
        """Волонтёра нельзя удалить через этот endpoint."""
        _auth(api_client, admin)
        resp = api_client.delete(f"{URL}{volunteer.id}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
