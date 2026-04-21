"""
Tests for project close + participants endpoints (Block 5).
"""
import pytest
import tempfile
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture(autouse=True)
def _clear_ratelimit_cache():
    """Reset django_ratelimit cache between tests."""
    cache.clear()
    yield
    cache.clear()


# Use a temp MEDIA_ROOT so FileField/ImageField don't touch the real filesystem.
_tmp_media = tempfile.mkdtemp(prefix="test_media_")


@pytest.fixture(autouse=True)
def _tmp_media_root(settings):
    settings.MEDIA_ROOT = _tmp_media

from apps.users.models import (
    User, VolunteerProfile, ModeratorProfile,
    Blacklist, VolunteerHoursLog, VolunteerCertificate,
)
from apps.projects.models import Project, Category, Region
from apps.applications.models import Application


def _auth(client, user):
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


# ---------- Fixtures ----------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username="admin1", email="a@e.com", password="p", role="admin"
    )


@pytest.fixture
def moderator(db):
    u = User.objects.create_user(
        username="mod1", email="m@e.com", password="p", role="moderator"
    )
    ModeratorProfile.objects.create(user=u)
    return u


@pytest.fixture
def organization(db):
    return User.objects.create_user(
        username="org1", email="o@e.com", password="p", role="organization"
    )


@pytest.fixture
def other_organization(db):
    return User.objects.create_user(
        username="org2", email="o2@e.com", password="p", role="organization"
    )


@pytest.fixture
def volunteer(db):
    u = User.objects.create_user(
        username="vol1", email="v1@e.com", password="p", role="volunteer"
    )
    VolunteerProfile.objects.create(user=u, first_name="Иван", last_name="Иванов")
    return u


@pytest.fixture
def volunteer2(db):
    u = User.objects.create_user(
        username="vol2", email="v2@e.com", password="p", role="volunteer"
    )
    VolunteerProfile.objects.create(user=u, first_name="Петр", last_name="Петров")
    return u


@pytest.fixture
def category(db):
    return Category.objects.create(name="Cat")


@pytest.fixture
def region(db):
    return Region.objects.create(name="Reg")


@pytest.fixture
def active_project(db, organization, category, region):
    return Project.objects.create(
        title="P1", description="d", category=category, region=region,
        volunteers_needed=5, status="active", organization=organization,
    )


@pytest.fixture
def project_with_volunteers(active_project, volunteer, volunteer2):
    Application.objects.create(
        volunteer=volunteer, project=active_project,
        status="approved", hours_committed=10,
    )
    Application.objects.create(
        volunteer=volunteer2, project=active_project,
        status="approved", hours_committed=5,
    )
    return active_project


# ---------- close endpoint ----------

CLOSE_URL = lambda pid: f"/api/projects/projects/{pid}/close/"
PARTICIPANTS_URL = lambda pid: f"/api/projects/projects/{pid}/participants/"


class TestProjectClose:

    def test_admin_can_close(self, api_client, admin, active_project):
        _auth(api_client, admin)
        resp = api_client.post(CLOSE_URL(active_project.id))
        assert resp.status_code == status.HTTP_200_OK
        active_project.refresh_from_db()
        assert active_project.status == "completed"

    def test_moderator_can_close(self, api_client, moderator, active_project):
        _auth(api_client, moderator)
        resp = api_client.post(CLOSE_URL(active_project.id))
        assert resp.status_code == status.HTTP_200_OK

    def test_owner_organization_can_close(self, api_client, organization, active_project):
        _auth(api_client, organization)
        resp = api_client.post(CLOSE_URL(active_project.id))
        assert resp.status_code == status.HTTP_200_OK

    def test_other_organization_cannot_close(self, api_client, other_organization, active_project):
        _auth(api_client, other_organization)
        resp = api_client.post(CLOSE_URL(active_project.id))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_volunteer_cannot_close(self, api_client, volunteer, active_project):
        _auth(api_client, volunteer)
        resp = api_client.post(CLOSE_URL(active_project.id))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_close(self, api_client, active_project):
        resp = api_client.post(CLOSE_URL(active_project.id))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_close_already_closed(self, api_client, admin, active_project):
        active_project.status = "completed"
        active_project.save()
        _auth(api_client, admin)
        resp = api_client.post(CLOSE_URL(active_project.id))
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_close_returns_participants(self, api_client, admin, project_with_volunteers):
        _auth(api_client, admin)
        resp = api_client.post(CLOSE_URL(project_with_volunteers.id))
        assert resp.status_code == status.HTTP_200_OK
        assert "participants" in resp.data
        assert len(resp.data["participants"]) == 2


# ---------- participants endpoint ----------

class TestProjectParticipants:

    def test_participants_only_approved(self, api_client, admin, active_project, volunteer, volunteer2):
        Application.objects.create(volunteer=volunteer, project=active_project, status="approved", hours_committed=1)
        Application.objects.create(volunteer=volunteer2, project=active_project, status="pending", hours_committed=1)
        _auth(api_client, admin)
        resp = api_client.get(PARTICIPANTS_URL(active_project.id))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["volunteer_id"] == volunteer.id

    def test_participants_include_totals(self, api_client, admin, project_with_volunteers, volunteer):
        """total_hours считается из VolunteerHoursLog."""
        VolunteerHoursLog.objects.create(volunteer=volunteer, hours=3, date="2026-04-01", description="x")
        VolunteerHoursLog.objects.create(volunteer=volunteer, hours=4, date="2026-04-02", description="y")
        _auth(api_client, admin)
        resp = api_client.get(PARTICIPANTS_URL(project_with_volunteers.id))
        entry = next(p for p in resp.data if p["volunteer_id"] == volunteer.id)
        assert entry["total_hours"] == 7
        assert entry["hours_committed"] == 10

    def test_participants_include_is_banned(self, api_client, admin, project_with_volunteers, volunteer):
        Blacklist.objects.create(volunteer=volunteer, reason="X", banned_by=admin, is_active=True)
        _auth(api_client, admin)
        resp = api_client.get(PARTICIPANTS_URL(project_with_volunteers.id))
        entry = next(p for p in resp.data if p["volunteer_id"] == volunteer.id)
        assert entry["is_banned"] is True

    def test_participants_include_has_certificate(
        self, api_client, admin, project_with_volunteers, volunteer
    ):
        from django.core.files.uploadedfile import SimpleUploadedFile
        VolunteerCertificate.objects.create(
            volunteer=volunteer, title="Cert",
            project=project_with_volunteers,
            file=SimpleUploadedFile("test.pdf", b"x", content_type="application/pdf"),
        )
        _auth(api_client, admin)
        resp = api_client.get(PARTICIPANTS_URL(project_with_volunteers.id))
        entry = next(p for p in resp.data if p["volunteer_id"] == volunteer.id)
        assert entry["has_certificate"] is True

    def test_participants_moderator_allowed(self, api_client, moderator, project_with_volunteers):
        _auth(api_client, moderator)
        resp = api_client.get(PARTICIPANTS_URL(project_with_volunteers.id))
        assert resp.status_code == status.HTTP_200_OK

    def test_participants_volunteer_forbidden(self, api_client, volunteer, project_with_volunteers):
        _auth(api_client, volunteer)
        resp = api_client.get(PARTICIPANTS_URL(project_with_volunteers.id))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_participants_other_org_forbidden(
        self, api_client, other_organization, project_with_volunteers
    ):
        _auth(api_client, other_organization)
        resp = api_client.get(PARTICIPANTS_URL(project_with_volunteers.id))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_other_org_cannot_see_draft_via_status_filter(
        self, api_client, other_organization, organization, category, region
    ):
        """Организация не может видеть чужие draft через ?status=draft."""
        Project.objects.create(
            title="secret draft", description="x", category=category, region=region,
            volunteers_needed=1, status="draft", organization=organization,
        )
        _auth(api_client, other_organization)
        resp = api_client.get("/api/projects/projects/?status=draft")
        assert resp.status_code == status.HTTP_200_OK
        # Фильтр queryset'а отсекает чужие draft'ы
        assert resp.data["count"] == 0

    def test_participants_expired_ban_not_banned(
        self, api_client, admin, project_with_volunteers, volunteer
    ):
        from datetime import timedelta
        from django.utils import timezone as tz
        Blacklist.objects.create(
            volunteer=volunteer, reason="X", banned_by=admin, is_active=True,
            banned_until=tz.now() - timedelta(days=1),
        )
        _auth(api_client, admin)
        resp = api_client.get(PARTICIPANTS_URL(project_with_volunteers.id))
        entry = next(p for p in resp.data if p["volunteer_id"] == volunteer.id)
        assert entry["is_banned"] is False
