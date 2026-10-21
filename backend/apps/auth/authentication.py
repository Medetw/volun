from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailAuthBackend(BaseBackend):
    """
    Authentication backend supporting email or username (case-insensitive).
    Safely handles duplicate emails without throwing MultipleObjectsReturned.
    """

    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        identifier = email or username or kwargs.get("username")
        if not identifier or not password:
            return None

        identifier = str(identifier).strip()

        # Match either email or username (case-insensitive)
        users = User.objects.filter(
            Q(email__iexact=identifier) | Q(username__iexact=identifier)
        )

        for user in users:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
