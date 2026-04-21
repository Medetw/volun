"""
Tests for News CRUD permissions (Block 3).
admin: всё. moderator: свои новости. featured (реклама) — только admin.
"""
import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, ModeratorProfile
from apps.news.models import News, NewsStatus, NewsCategory


URL = "/api/news/news/"


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


def _auth(client, user):
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin(db):
    return User.objects.create_user(username="admin1", email="a@e.com", password="p", role="admin")


@pytest.fixture
def moderator(db):
    u = User.objects.create_user(username="mod1", email="m@e.com", password="p", role="moderator")
    ModeratorProfile.objects.create(user=u)
    return u


@pytest.fixture
def moderator2(db):
    u = User.objects.create_user(username="mod2", email="m2@e.com", password="p", role="moderator")
    ModeratorProfile.objects.create(user=u)
    return u


@pytest.fixture
def volunteer(db):
    return User.objects.create_user(username="vol", email="v@e.com", password="p", role="volunteer")


@pytest.fixture
def news_by_mod(db, moderator):
    return News.objects.create(
        title="By mod", slug="by-mod", content="x",
        status=NewsStatus.PUBLISHED, category=NewsCategory.GENERAL,
        author=moderator, featured=False,
    )


class TestNewsCreate:

    def test_admin_can_create(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.post(URL, {
            "title": "T", "slug": "t-admin", "content": "c",
            "status": "published", "category": "general",
        }, format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_moderator_can_create(self, api_client, moderator):
        _auth(api_client, moderator)
        resp = api_client.post(URL, {
            "title": "M", "slug": "m-mod", "content": "c",
            "status": "published", "category": "general",
        }, format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_volunteer_cannot_create(self, api_client, volunteer):
        _auth(api_client, volunteer)
        resp = api_client.post(URL, {
            "title": "V", "slug": "v", "content": "c",
            "status": "published", "category": "general",
        }, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create(self, api_client):
        resp = api_client.post(URL, {"title": "X"}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_moderator_cannot_create_featured(self, api_client, moderator):
        """Реклама (featured) — только admin."""
        _auth(api_client, moderator)
        resp = api_client.post(URL, {
            "title": "Ad", "slug": "ad-test", "content": "c",
            "status": "published", "category": "general",
            "featured": True,
        }, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_featured(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.post(URL, {
            "title": "Ad admin", "slug": "ad-admin", "content": "c",
            "status": "published", "category": "general",
            "featured": True,
        }, format="json")
        assert resp.status_code == status.HTTP_201_CREATED


class TestNewsUpdate:

    def test_admin_can_update_any(self, api_client, admin, news_by_mod):
        _auth(api_client, admin)
        resp = api_client.patch(f"{URL}{news_by_mod.id}/", {"title": "Updated"}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_moderator_can_update_own(self, api_client, moderator, news_by_mod):
        _auth(api_client, moderator)
        resp = api_client.patch(f"{URL}{news_by_mod.id}/", {"title": "Mod updated"}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_moderator_cannot_update_others(self, api_client, moderator2, news_by_mod):
        _auth(api_client, moderator2)
        resp = api_client.patch(f"{URL}{news_by_mod.id}/", {"title": "Hack"}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_moderator_cannot_set_featured_on_own(self, api_client, moderator, news_by_mod):
        _auth(api_client, moderator)
        resp = api_client.patch(f"{URL}{news_by_mod.id}/", {"featured": True}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestNewsDelete:

    def test_admin_can_delete_any(self, api_client, admin, news_by_mod):
        _auth(api_client, admin)
        resp = api_client.delete(f"{URL}{news_by_mod.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_moderator_can_delete_own(self, api_client, moderator, news_by_mod):
        _auth(api_client, moderator)
        resp = api_client.delete(f"{URL}{news_by_mod.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_moderator_cannot_delete_others(self, api_client, moderator2, news_by_mod):
        _auth(api_client, moderator2)
        resp = api_client.delete(f"{URL}{news_by_mod.id}/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
