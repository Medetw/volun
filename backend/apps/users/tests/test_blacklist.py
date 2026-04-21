"""
Tests for the Blacklist (ЧС) feature.

Coverage:
  - Model: is_currently_banned() logic
  - Serializer: validation (reason required, non-volunteer, duplicate ban)
  - API – list/create/unban/check endpoints
  - Permissions: volunteer & org cannot access; mod & admin can
"""
import pytest
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Blacklist, User, ModeratorProfile


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _auth(client: APIClient, user: User) -> APIClient:
    """Attach a JWT token to the given API client."""
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def volunteer(db):
    return User.objects.create_user(
        username="vol1", email="vol1@example.com",
        password="pass123", role="volunteer",
    )


@pytest.fixture
def volunteer2(db):
    return User.objects.create_user(
        username="vol2", email="vol2@example.com",
        password="pass123", role="volunteer",
    )


@pytest.fixture
def organization(db):
    return User.objects.create_user(
        username="org1", email="org1@example.com",
        password="pass123", role="organization",
    )


@pytest.fixture
def moderator(db):
    user = User.objects.create_user(
        username="mod1", email="mod1@example.com",
        password="pass123", role="moderator",
    )
    ModeratorProfile.objects.create(user=user)
    return user


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username="adm1", email="adm1@example.com",
        password="pass123", role="admin",
    )


@pytest.fixture
def active_ban(db, volunteer, admin):
    return Blacklist.objects.create(
        volunteer=volunteer,
        reason="Нарушение правил",
        banned_by=admin,
        is_active=True,
    )


@pytest.fixture
def expired_ban(db, volunteer, admin):
    return Blacklist.objects.create(
        volunteer=volunteer,
        reason="Нарушение правил",
        banned_by=admin,
        is_active=True,
        banned_until=timezone.now() - timedelta(days=1),
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestBlacklistModel:

    def test_indefinite_ban_is_currently_banned(self, active_ban):
        """Бессрочный активный бан — is_currently_banned() == True."""
        assert active_ban.is_currently_banned() is True

    def test_future_ban_is_currently_banned(self, db, volunteer, admin):
        """Срочный бан с будущей датой — True."""
        ban = Blacklist.objects.create(
            volunteer=volunteer,
            reason="Нарушение",
            banned_by=admin,
            is_active=True,
            banned_until=timezone.now() + timedelta(days=7),
        )
        assert ban.is_currently_banned() is True

    def test_expired_ban_not_banned(self, expired_ban):
        """Срок бана истёк — False."""
        assert expired_ban.is_currently_banned() is False

    def test_inactive_ban_not_banned(self, db, volunteer, admin):
        """Бан снят (is_active=False) — False."""
        ban = Blacklist.objects.create(
            volunteer=volunteer,
            reason="Нарушение",
            banned_by=admin,
            is_active=False,
        )
        assert ban.is_currently_banned() is False

    def test_str_representation(self, active_ban):
        assert "vol1" in str(active_ban)
        assert "active=True" in str(active_ban)

    def test_unique_active_ban_constraint(self, active_ban, admin):
        """Два активных бана на одного волонтёра — IntegrityError."""
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Blacklist.objects.create(
                volunteer=active_ban.volunteer,
                reason="Другое нарушение",
                banned_by=admin,
                is_active=True,
            )

    def test_can_have_multiple_inactive_bans(self, db, volunteer, admin):
        """Несколько неактивных банов на одного волонтёра — OK."""
        Blacklist.objects.create(volunteer=volunteer, reason="R1", banned_by=admin, is_active=False)
        Blacklist.objects.create(volunteer=volunteer, reason="R2", banned_by=admin, is_active=False)
        assert Blacklist.objects.filter(volunteer=volunteer).count() == 2


# ---------------------------------------------------------------------------
# Serializer tests
# ---------------------------------------------------------------------------

class TestBlacklistSerializer:

    def test_reason_required(self, db, volunteer, admin):
        from apps.users.serializers import BlacklistSerializer
        s = BlacklistSerializer(data={"volunteer": volunteer.id, "reason": ""})
        assert not s.is_valid()
        assert "reason" in s.errors

    def test_reason_whitespace_rejected(self, db, volunteer):
        from apps.users.serializers import BlacklistSerializer
        s = BlacklistSerializer(data={"volunteer": volunteer.id, "reason": "   "})
        assert not s.is_valid()
        assert "reason" in s.errors

    def test_ban_non_volunteer_rejected(self, db, organization):
        from apps.users.serializers import BlacklistSerializer
        s = BlacklistSerializer(data={"volunteer": organization.id, "reason": "Test"})
        assert not s.is_valid()
        assert "volunteer" in s.errors

    def test_duplicate_active_ban_rejected(self, active_ban, volunteer2):
        from apps.users.serializers import BlacklistSerializer
        # Пробуем добавить уже забаненного волонтёра снова
        s = BlacklistSerializer(data={"volunteer": active_ban.volunteer.id, "reason": "Снова"})
        assert not s.is_valid()
        assert "volunteer" in s.errors

    def test_valid_ban_serializer(self, db, volunteer):
        from apps.users.serializers import BlacklistSerializer
        s = BlacklistSerializer(data={
            "volunteer": volunteer.id,
            "reason": "Нарушение правил платформы",
        })
        assert s.is_valid(), s.errors

    def test_is_currently_banned_field(self, active_ban):
        from apps.users.serializers import BlacklistSerializer
        data = BlacklistSerializer(active_ban).data
        assert data["is_currently_banned"] is True

    def test_banned_by_name_field(self, active_ban):
        from apps.users.serializers import BlacklistSerializer
        data = BlacklistSerializer(active_ban).data
        assert data["banned_by_name"] == "adm1"


# ---------------------------------------------------------------------------
# API permission tests
# ---------------------------------------------------------------------------

BLACKLIST_URL = "/api/users/blacklist/"


class TestBlacklistPermissions:

    def test_unauthenticated_denied(self, api_client, db):
        resp = api_client.get(BLACKLIST_URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_volunteer_denied(self, api_client, volunteer):
        _auth(api_client, volunteer)
        resp = api_client.get(BLACKLIST_URL)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_organization_denied(self, api_client, organization):
        _auth(api_client, organization)
        resp = api_client.get(BLACKLIST_URL)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_moderator_allowed(self, api_client, moderator):
        _auth(api_client, moderator)
        resp = api_client.get(BLACKLIST_URL)
        assert resp.status_code == status.HTTP_200_OK

    def test_admin_allowed(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.get(BLACKLIST_URL)
        assert resp.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# API functional tests
# ---------------------------------------------------------------------------

class TestBlacklistAPI:

    # --- List ---

    def test_list_returns_all_entries(self, api_client, admin, active_ban):
        _auth(api_client, admin)
        resp = api_client.get(BLACKLIST_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 1

    # --- Create (ban) ---

    def test_admin_can_ban_volunteer(self, api_client, admin, volunteer2):
        _auth(api_client, admin)
        resp = api_client.post(BLACKLIST_URL, {
            "volunteer": volunteer2.id,
            "reason": "Нарушение правил платформы",
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["is_active"] is True
        assert resp.data["banned_by"] == admin.id

    def test_moderator_can_ban_volunteer(self, api_client, moderator, volunteer2):
        _auth(api_client, moderator)
        resp = api_client.post(BLACKLIST_URL, {
            "volunteer": volunteer2.id,
            "reason": "Систематические опоздания",
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_ban_without_reason_rejected(self, api_client, admin, volunteer2):
        _auth(api_client, admin)
        resp = api_client.post(BLACKLIST_URL, {"volunteer": volunteer2.id, "reason": ""})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "reason" in resp.data

    def test_ban_with_deadline(self, api_client, admin, volunteer2):
        """Бан на конкретный срок."""
        _auth(api_client, admin)
        deadline = (timezone.now() + timedelta(days=30)).isoformat()
        resp = api_client.post(BLACKLIST_URL, {
            "volunteer": volunteer2.id,
            "reason": "Временное нарушение",
            "banned_until": deadline,
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["banned_until"] is not None

    def test_duplicate_ban_rejected(self, api_client, admin, active_ban):
        """Нельзя добавить уже забаненного волонтёра."""
        _auth(api_client, admin)
        resp = api_client.post(BLACKLIST_URL, {
            "volunteer": active_ban.volunteer.id,
            "reason": "Повторное нарушение",
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_ban_non_volunteer(self, api_client, admin, organization):
        _auth(api_client, admin)
        resp = api_client.post(BLACKLIST_URL, {
            "volunteer": organization.id,
            "reason": "Проверка",
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # --- Unban ---

    def test_admin_can_unban(self, api_client, admin, active_ban):
        _auth(api_client, admin)
        resp = api_client.post(f"{BLACKLIST_URL}{active_ban.id}/unban/")
        assert resp.status_code == status.HTTP_200_OK
        active_ban.refresh_from_db()
        assert active_ban.is_active is False

    def test_unban_already_inactive_returns_400(self, api_client, admin, db, volunteer):
        ban = Blacklist.objects.create(
            volunteer=volunteer, reason="R", banned_by=admin, is_active=False
        )
        _auth(api_client, admin)
        resp = api_client.post(f"{BLACKLIST_URL}{ban.id}/unban/")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # --- Check ---

    def test_check_banned_volunteer(self, api_client, admin, active_ban):
        _auth(api_client, admin)
        resp = api_client.get(f"{BLACKLIST_URL}check/?volunteer_id={active_ban.volunteer.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_banned"] is True

    def test_check_unbanned_volunteer(self, api_client, admin, volunteer2):
        _auth(api_client, admin)
        resp = api_client.get(f"{BLACKLIST_URL}check/?volunteer_id={volunteer2.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_banned"] is False

    def test_check_expired_ban(self, api_client, admin, expired_ban):
        _auth(api_client, admin)
        resp = api_client.get(f"{BLACKLIST_URL}check/?volunteer_id={expired_ban.volunteer.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_banned"] is False

    def test_check_missing_volunteer_id(self, api_client, admin):
        _auth(api_client, admin)
        resp = api_client.get(f"{BLACKLIST_URL}check/")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_check_invalid_volunteer_id_type(self, api_client, admin):
        """Нечисловой volunteer_id возвращает 400."""
        _auth(api_client, admin)
        resp = api_client.get(f"{BLACKLIST_URL}check/?volunteer_id=abc")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_ban_with_past_deadline_rejected(self, api_client, admin, volunteer2):
        """Дата блокировки в прошлом — 400."""
        _auth(api_client, admin)
        past = (timezone.now() - timedelta(hours=1)).isoformat()
        resp = api_client.post(BLACKLIST_URL, {
            "volunteer": volunteer2.id,
            "reason": "Нарушение",
            "banned_until": past,
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "banned_until" in resp.data

    def test_perform_create_sets_banned_by(self, api_client, admin, volunteer2):
        """banned_by всегда устанавливается из request.user, нельзя передать извне."""
        _auth(api_client, admin)
        resp = api_client.post(BLACKLIST_URL, {
            "volunteer": volunteer2.id,
            "reason": "Тест",
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["banned_by"] == admin.id

    def test_unban_race_condition_protection(self, api_client, admin, db, volunteer):
        """Повторный unban той же записи возвращает 400 (атомарная защита)."""
        ban = Blacklist.objects.create(
            volunteer=volunteer, reason="R", banned_by=admin, is_active=True
        )
        _auth(api_client, admin)
        # Первый unban — OK
        resp1 = api_client.post(f"{BLACKLIST_URL}{ban.id}/unban/")
        assert resp1.status_code == status.HTTP_200_OK
        # Второй unban — 400
        resp2 = api_client.post(f"{BLACKLIST_URL}{ban.id}/unban/")
        assert resp2.status_code == status.HTTP_400_BAD_REQUEST
