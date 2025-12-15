from ninja.security import HttpBearer
from ninja_jwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from typing import Optional, Any

User = get_user_model()


class JWTAuth(HttpBearer):
    """
    Обязательная JWT аутентификация.
    Использование: @router.get("/protected", auth=JWTAuth())
    """
    
    def authenticate(self, request, token: str) -> Optional[Any]:
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


class OptionalJWTAuth(HttpBearer):
    """
    Опциональная JWT аутентификация.
    Возвращает "Anonymous" если токен отсутствует.
    Возвращает User если токен валиден.
    Возвращает None (401) если токен невалиден.
    """
    
    def __call__(self, request):
        headers = request.headers
        auth_value = headers.get(self.header)
        if not auth_value:
            return "Anonymous"
        return super().__call__(request)
    
    def authenticate(self, request, token: str) -> Optional[Any]:
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
