"""
Block 2: admin/moderator могут создавать/редактировать проекты.
"""
import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, ModeratorProfile
from apps.projects.models import Project, Category, Region


URL = "/api/projects/projects/"


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
    ModeratorProfile.objects.create(user=u)
    return u


@pytest.fixture
def organization(db):
    return User.objects.create_user(username="org", email="o@e.com", password="p", role="organization")


@pytest.fixture
def volunteer(db):
    return User.objects.create_user(username="vol", email="v@e.com", password="p", role="volunteer")


@pytest.fixture
def category(db):
    return Category.objects.create(name="Cat")


@pytest.fixture
def region(db):
    return Region.objects.create(name="Reg")


@pytest.fixture
def existing_project(db, organization, category, region):
    return Project.objects.create(
        title="P", description="d", category=category, region=region,
        volunteers_needed=5, status="active", organization=organization,
    )


class TestProjectCreate:

    def _payload(self, category, region):
        return {
            "title": "New project", "description": "d",
            "category_id": category.id, "region_id": region.id,
            "format": "offline", "volunteers_needed": 5,
            "status": "active",
        }

    def test_organization_can_create(self, api_client, organization, category, region):
        _auth(api_client, organization)
        resp = api_client.post(URL, self._payload(category, region), format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_admin_can_create(self, api_client, admin, category, region):
        _auth(api_client, admin)
        resp = api_client.post(URL, self._payload(category, region), format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_moderator_can_create(self, api_client, moderator, category, region):
        _auth(api_client, moderator)
        resp = api_client.post(URL, self._payload(category, region), format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_volunteer_cannot_create(self, api_client, volunteer, category, region):
        _auth(api_client, volunteer)
        resp = api_client.post(URL, self._payload(category, region), format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_created_project_shows_username(self, api_client, admin, category, region):
        """Проект от admin (без organization_profile) отображает username в organization_name."""
        _auth(api_client, admin)
        resp = api_client.post(URL, self._payload(category, region), format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        # Теперь проверим list
        list_resp = api_client.get(URL)
        found = [p for p in list_resp.data["results"] if p["title"] == "New project"][0]
        assert found["organization_name"] == "adm"  # username


class TestProjectUpdate:

    def test_admin_can_update_any(self, api_client, admin, existing_project):
        _auth(api_client, admin)
        resp = api_client.patch(f"{URL}{existing_project.id}/", {"title": "Fixed"}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_moderator_can_update_any(self, api_client, moderator, existing_project):
        _auth(api_client, moderator)
        resp = api_client.patch(f"{URL}{existing_project.id}/", {"title": "Mod fix"}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_owner_can_update(self, api_client, organization, existing_project):
        _auth(api_client, organization)
        resp = api_client.patch(f"{URL}{existing_project.id}/", {"title": "Own"}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_volunteer_cannot_update(self, api_client, volunteer, existing_project):
        _auth(api_client, volunteer)
        resp = api_client.patch(f"{URL}{existing_project.id}/", {"title": "x"}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
