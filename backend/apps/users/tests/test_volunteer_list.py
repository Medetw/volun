"""
Tests for VolunteerListView (Block 6): search, is_banned, permissions.
"""
import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import (
    User, VolunteerProfile, ModeratorProfile, Blacklist,
)


URL = "/api/users/volunteers/"


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


def _auth(client, user):
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin(db):
    return User.objects.create_user(username="admin", email="a@e.com", password="p", role="admin")


@pytest.fixture
def moderator(db):
    u = User.objects.create_user(username="mod", email="m@e.com", password="p", role="moderator")
    ModeratorProfile.objects.create(user=u, can_view_volunteers=True)
    return u


@pytest.fixture
def moderator_no_view(db):
    u = User.objects.create_user(username="mod2", email="m2@e.com", password="p", role="moderator")
    ModeratorProfile.objects.create(user=u, can_view_volunteers=False)
    return u


@pytest.fixture
def organization(db):
    return User.objects.create_user(username="org", email="o@e.com", password="p", role="organization")


@pytest.fixture
def volunteers(db):
    v1 = User.objects.create_user(username="ivan", email="ivan@e.com", password="p", role="volunteer")
    VolunteerProfile.objects.create(user=v1, first_name="Иван", last_name="Петров", city="Алматы")
    v2 = User.objects.create_user(username="maria", email="maria@e.com", password="p", role="volunteer")
    VolunteerProfile.objects.create(user=v2, first_name="Мария", last_name="Сидорова", city="Астана")
    v3 = User.objects.create_user(username="alex", email="alex@e.com", password="p", role="volunteer")
    VolunteerProfile.objects.create(user=v3, first_name="Алекс", last_name="Иванов", city="Шымкент")
    return [v1, v2, v3]


# ---------- Permissions ----------

class TestVolunteerListPermissions:

    def test_unauthenticated_denied(self, api_client):
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_organization_denied(self, api_client, organization):
        _auth(api_client, organization)
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_moderator_without_permission_denied(self, api_client, moderator_no_view):
        _auth(api_client, moderator_no_view)
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_moderator_with_permission_allowed(self, api_client, moderator, volunteers):
        _auth(api_client, moderator)
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_200_OK

    def test_admin_allowed(self, api_client, admin, volunteers):
        _auth(api_client, admin)
        resp = api_client.get(URL)
        assert resp.status_code == status.HTTP_200_OK


# ---------- Data ----------

class TestVolunteerListData:

    def test_returns_all_volunteers(self, api_client, admin, volunteers):
        _auth(api_client, admin)
        resp = api_client.get(URL)
        assert len(resp.data) == 3

    def test_does_not_include_non_volunteers(self, api_client, admin, volunteers, moderator):
        _auth(api_client, admin)
        resp = api_client.get(URL)
        usernames = {u["username"] for u in resp.data}
        assert "mod" not in usernames

    def test_is_banned_field_present(self, api_client, admin, volunteers):
        Blacklist.objects.create(volunteer=volunteers[0], reason="X", banned_by=admin, is_active=True)
        _auth(api_client, admin)
        resp = api_client.get(URL)
        banned = [u for u in resp.data if u["username"] == "ivan"][0]
        not_banned = [u for u in resp.data if u["username"] == "maria"][0]
        assert banned["is_banned"] is True
        assert not_banned["is_banned"] is False

    def test_expired_ban_is_not_marked(self, api_client, admin, volunteers):
        from datetime import timedelta
        from django.utils import timezone as tz
        Blacklist.objects.create(
            volunteer=volunteers[0], reason="X", banned_by=admin, is_active=True,
            banned_until=tz.now() - timedelta(days=1),
        )
        _auth(api_client, admin)
        resp = api_client.get(URL)
        row = [u for u in resp.data if u["username"] == "ivan"][0]
        assert row["is_banned"] is False


# ---------- Search ----------

class TestVolunteerListSearch:

    def test_search_by_first_name(self, api_client, admin, volunteers):
        _auth(api_client, admin)
        resp = api_client.get(f"{URL}?search=Иван")
        usernames = {u["username"] for u in resp.data}
        # "Иван" matches first_name "Иван" AND last_name "Иванов"
        assert "ivan" in usernames
        assert "alex" in usernames

    def test_search_by_email(self, api_client, admin, volunteers):
        _auth(api_client, admin)
        resp = api_client.get(f"{URL}?search=maria@")
        assert len(resp.data) == 1
        assert resp.data[0]["username"] == "maria"

    def test_search_by_username(self, api_client, admin, volunteers):
        _auth(api_client, admin)
        resp = api_client.get(f"{URL}?search=alex")
        assert len(resp.data) == 1

    def test_search_empty_returns_all(self, api_client, admin, volunteers):
        _auth(api_client, admin)
        resp = api_client.get(f"{URL}?search=")
        assert len(resp.data) == 3

    def test_search_no_matches(self, api_client, admin, volunteers):
        _auth(api_client, admin)
        resp = api_client.get(f"{URL}?search=nonexistent")
        assert resp.data == []

    def test_search_wildcards_escaped(self, api_client, admin, volunteers):
        """Пользователь не может использовать % как SQL wildcard."""
        _auth(api_client, admin)
        # % не должен матчить "ivan"
        resp = api_client.get(f"{URL}?search=iv%")
        assert resp.data == []
