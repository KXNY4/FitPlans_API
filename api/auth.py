from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import APIKeyCookie
from ninja_jwt.tokens import RefreshToken

User = get_user_model()


class JWTAuth(APIKeyCookie):
    """
    Обязательная JWT аутентификация через HttpOnly Cookies.
    """

    param_name = settings.AUTH_COOKIE

    def authenticate(self, request, token: str) -> Any | None:
        try:
            from ninja_jwt.tokens import AccessToken

            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)
            if not user.is_active:
                return None
            return user
        except Exception:
            return None


class OptionalJWTAuth(APIKeyCookie):
    """
    Опциональная JWT аутентификация через Cookies.
    """

    param_name = settings.AUTH_COOKIE

    def authenticate(self, request, token: str) -> Any | None:
        if not token:
            return "Anonymous"
        try:
            from ninja_jwt.tokens import AccessToken

            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            return User.objects.get(id=user_id)
        except Exception:
            return None


def create_tokens(user: Any) -> dict:
    """Создать пару токенов для пользователя."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
