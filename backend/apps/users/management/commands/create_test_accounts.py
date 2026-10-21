"""
Management command: create_test_accounts
========================================
Creates / updates a fixed set of test accounts covering every role in the
platform so that developers and QA can immediately log in and test
role-specific behaviour without running the full setup_test_data.sh script.

Usage
-----
    python manage.py create_test_accounts            # create accounts
    python manage.py create_test_accounts --reset    # delete & recreate

Accounts created
----------------
Role          | Username          | Email                          | Password
------------- | ----------------- | ------------------------------ | ------------
admin         | test_admin        | test_admin@volun.test          | Admin@12345
moderator     | test_moderator    | test_moderator@volun.test      | Mod@12345
moderator     | test_mod_limited  | test_mod_limited@volun.test    | Mod@12345
organization  | test_org          | test_org@volun.test            | Org@12345
volunteer     | test_volunteer    | test_volunteer@volun.test      | Vol@12345
volunteer     | test_volunteer2   | test_volunteer2@volun.test     | Vol@12345

Notes
-----
- ``test_mod_limited`` has all RBAC permissions disabled – useful for testing
  that restricted moderators are properly blocked.
- All accounts are idempotent: re-running the command without --reset simply
  ensures the accounts exist with the correct role (passwords are NOT reset).
- With ``--reset`` the listed accounts are deleted first, then recreated.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import (
    UserRole,
    VolunteerProfile,
    OrganizationProfile,
    ModeratorProfile,
)

User = get_user_model()

# ---------------------------------------------------------------------------
# Account definitions
# ---------------------------------------------------------------------------

ADMIN_ACCOUNTS = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin12345",
        "role": UserRole.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "test_admin@volun.test",  # username = email (для входа через веб-форму)
        "email": "test_admin@volun.test",
        "password": "Admin@12345",
        "role": UserRole.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    },
]

MODERATOR_ACCOUNTS = [
    {
        "username": "test_moderator@volun.test",
        "email": "test_moderator@volun.test",
        "password": "Mod@12345",
        "role": UserRole.MODERATOR,
        "profile": {
            "department": "Общий отдел",
            "can_view_volunteers": True,
            "can_manage_hours": True,
            "can_manage_certificates": True,
            "notes": "Full-access moderator account for testing.",
        },
    },
    {
        "username": "test_mod_limited@volun.test",
        "email": "test_mod_limited@volun.test",
        "password": "Mod@12345",
        "role": UserRole.MODERATOR,
        "profile": {
            "department": "Ограниченный доступ",
            "can_view_volunteers": False,
            "can_manage_hours": False,
            "can_manage_certificates": False,
            "notes": "Limited moderator – all RBAC permissions disabled. "
                     "Use to verify that restricted moderators are blocked.",
        },
    },
]

ORGANIZATION_ACCOUNTS = [
    {
        "username": "test_org@volun.test",
        "email": "test_org@volun.test",
        "password": "Org@12345",
        "role": UserRole.ORGANIZATION,
        "profile": {
            "name": "Тестовая Организация",
            "organization_type": "ngo",
            "description": (
                "Тестовая организация для проверки функциональности платформы. "
                "Создана автоматически командой create_test_accounts."
            ),
            "region": "Алматы",
            "contacts": {
                "phone": "+7 777 000 0001",
                "email": "test_org@volun.test",
                "website": "https://test-org.volun.test",
            },
            "is_verified": True,
        },
    },
]

VOLUNTEER_ACCOUNTS = [
    {
        "username": "test_volunteer@volun.test",
        "email": "test_volunteer@volun.test",
        "password": "Vol@12345",
        "role": UserRole.VOLUNTEER,
        "profile": {
            "first_name": "Иван",
            "last_name": "Волонтёров",
            "birth_date": "1995-06-15",
            "gender": "male",
            "city": "Алматы",
            "region": "Алматы",
            "skills": ["программирование", "дизайн", "английский язык"],
            "interests": ["образование", "технологии", "экология"],
        },
    },
    {
        "username": "test_volunteer2@volun.test",
        "email": "test_volunteer2@volun.test",
        "password": "Vol@12345",
        "role": UserRole.VOLUNTEER,
        "profile": {
            "first_name": "Айгерим",
            "last_name": "Тестова",
            "birth_date": "2000-03-22",
            "gender": "female",
            "city": "Астана",
            "region": "Астана",
            "skills": ["медицина", "педагогика"],
            "interests": ["здоровье", "дети", "культура"],
        },
    },
]


class Command(BaseCommand):
    help = (
        "Create fixed test accounts for every platform role "
        "(admin, moderator, organization, volunteer). "
        "Use --reset to delete and recreate them."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            default=False,
            help="Delete existing test accounts before recreating them.",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _all_usernames(self):
        names = []
        for accounts in (
            ADMIN_ACCOUNTS,
            MODERATOR_ACCOUNTS,
            ORGANIZATION_ACCOUNTS,
            VOLUNTEER_ACCOUNTS,
        ):
            for a in accounts:
                names.append(a["username"])
        return names

    def _delete_accounts(self):
        usernames = self._all_usernames()
        deleted, _ = User.objects.filter(username__in=usernames).delete()
        self.stdout.write(
            self.style.WARNING(f"  🗑  Deleted {deleted} existing test account(s).")
        )

    def _create_user(self, account: dict) -> tuple:
        """
        Get-or-create the base User.
        Returns (user, created).
        """
        defaults = {
            "email": account["email"],
            "role": account["role"],
            "is_staff": account.get("is_staff", False),
            "is_superuser": account.get("is_superuser", False),
        }
        user, created = User.objects.get_or_create(
            username=account["username"],
            defaults=defaults,
        )
        if created:
            user.set_password(account["password"])
            user.save()
        return user, created

    # ------------------------------------------------------------------
    # Role-specific profile builders
    # ------------------------------------------------------------------

    def _ensure_admin(self, account: dict):
        user, created = self._create_user(account)
        status = "✅ Created" if created else "⏭  Already exists"
        self.stdout.write(
            f"  {status}: ADMIN  {user.username} / {account['email']}"
        )

    def _ensure_moderator(self, account: dict):
        user, created = self._create_user(account)
        p = account["profile"]
        ModeratorProfile.objects.update_or_create(
            user=user,
            defaults={
                "department": p["department"],
                "can_view_volunteers": p["can_view_volunteers"],
                "can_manage_hours": p["can_manage_hours"],
                "can_manage_certificates": p["can_manage_certificates"],
                "notes": p["notes"],
            },
        )
        status = "✅ Created" if created else "⏭  Already exists"
        perms = (
            f"view={p['can_view_volunteers']} "
            f"hours={p['can_manage_hours']} "
            f"certs={p['can_manage_certificates']}"
        )
        self.stdout.write(
            f"  {status}: MODERATOR  {user.username} / {account['email']}  [{perms}]"
        )

    def _ensure_organization(self, account: dict):
        user, created = self._create_user(account)
        p = account["profile"]
        OrganizationProfile.objects.update_or_create(
            user=user,
            defaults={
                "name": p["name"],
                "organization_type": p["organization_type"],
                "description": p["description"],
                "region": p["region"],
                "contacts": p["contacts"],
                "is_verified": p["is_verified"],
            },
        )
        status = "✅ Created" if created else "⏭  Already exists"
        self.stdout.write(
            f"  {status}: ORGANIZATION  {user.username} / {account['email']}"
        )

    def _ensure_volunteer(self, account: dict):
        user, created = self._create_user(account)
        p = account["profile"]
        VolunteerProfile.objects.update_or_create(
            user=user,
            defaults={
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "birth_date": p.get("birth_date"),
                "gender": p["gender"],
                "city": p["city"],
                "region": p["region"],
                "skills": p["skills"],
                "interests": p["interests"],
            },
        )
        status = "✅ Created" if created else "⏭  Already exists"
        self.stdout.write(
            f"  {status}: VOLUNTEER  {user.username} / {account['email']}"
        )

    # ------------------------------------------------------------------
    # Main handler
    # ------------------------------------------------------------------

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\n🔧 create_test_accounts – Volunteering Platform\n")
        )

        if options["reset"]:
            self.stdout.write(self.style.WARNING("--reset flag detected. Removing existing accounts…"))
            self._delete_accounts()

        self.stdout.write("\n👑 Admin accounts:")
        for account in ADMIN_ACCOUNTS:
            self._ensure_admin(account)

        self.stdout.write("\n🛡  Moderator accounts:")
        for account in MODERATOR_ACCOUNTS:
            self._ensure_moderator(account)

        self.stdout.write("\n🏢 Organization accounts:")
        for account in ORGANIZATION_ACCOUNTS:
            self._ensure_organization(account)

        self.stdout.write("\n🙋 Volunteer accounts:")
        for account in VOLUNTEER_ACCOUNTS:
            self._ensure_volunteer(account)

        self.stdout.write(
            self.style.SUCCESS(
                "\n✅ Done! Test credentials summary:\n"
                "\n"
                "  Role          Username            Email                        Password\n"
                "  ------------- ------------------- ---------------------------- -----------\n"
                "  admin         test_admin          test_admin@volun.test        Admin@12345\n"
                "  moderator     test_moderator      test_moderator@volun.test    Mod@12345\n"
                "  mod (limited) test_mod_limited    test_mod_limited@volun.test  Mod@12345\n"
                "  organization  test_org            test_org@volun.test          Org@12345\n"
                "  volunteer     test_volunteer      test_volunteer@volun.test    Vol@12345\n"
                "  volunteer     test_volunteer2     test_volunteer2@volun.test   Vol@12345\n"
            )
        )
