from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from ninja import File, Router
from ninja.files import UploadedFile
from ninja.responses import Response

from api.auth import JWTAuth, create_tokens
from apps.users.models import UserProgress
from apps.users.schemas import (
    LoginIn,
    RegisterIn,
    UserOut,
    UserProgressIn,
    UserProgressOut,
    UserUpdateIn,
)
from apps.users.services import UserService

auth_router = Router()
users_router = Router()


def set_auth_cookies(response: Response, tokens: dict):
    response.set_cookie(
        key=settings.AUTH_COOKIE,
        value=tokens["access"],
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.NINJA_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
    )
    response.set_cookie(
        key=settings.AUTH_COOKIE_REFRESH,
        value=tokens["refresh"],
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.NINJA_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
    )


@auth_router.post("/register", response={201: UserOut}, auth=None)
def register(request, data: RegisterIn):
    """
    Регистрация нового пользователя.

    Создаёт пользователя и устанавливает JWT токены в cookies.
    """
    user = UserService.create_user(
        email=data.email,
        username=data.username,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )

    tokens = create_tokens(user)

    response = Response(UserOut.model_validate(user), status=201)
    set_auth_cookies(response, tokens)
    return response


@auth_router.post("/login", response={200: UserOut, 401: dict}, auth=None)
def login(request, data: LoginIn):
    """
    Вход в систему.

    Проверяет credentials и устанавливает JWT токены в cookies.
    """
    user = authenticate(email=data.email, password=data.password)

    if not user:
        return 401, {"error": {"code": "INVALID_CREDENTIALS", "message": "Неверный email или пароль"}}

    if not user.is_active:
        return 401, {"error": {"code": "USER_INACTIVE", "message": "Аккаунт деактивирован"}}

    tokens = create_tokens(user)

    response = Response(UserOut.model_validate(user), status=200)
    set_auth_cookies(response, tokens)
    return response


@auth_router.post("/refresh", auth=None, response={200: dict, 401: dict})
def refresh_token(request):
    """
    Обновление access токена через refresh cookie.
    """
    from ninja_jwt.tokens import RefreshToken

    refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
    if not refresh_token:
        return 401, {"error": {"code": "NO_TOKEN", "message": "Refresh токен не найден"}}

    try:
        refresh = RefreshToken(refresh_token)

        tokens = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        response = Response({"success": True}, status=200)
        set_auth_cookies(response, tokens)
        return response
    except Exception:
        return 401, {"error": {"code": "INVALID_TOKEN", "message": "Невалидный refresh токен"}}


@auth_router.post("/logout", auth=JWTAuth())
def logout(request, refresh: str):
    """
    Выход из системы.

    Добавляет refresh токен в чёрный список.
    """
    from ninja_jwt.tokens import RefreshToken

    try:
        token = RefreshToken(refresh)
        token.blacklist()
        return {"message": "Успешный выход"}
    except Exception:
        return {"error": {"code": "INVALID_TOKEN", "message": "Ошибка выхода"}}


@users_router.get("/me", response=UserOut, auth=JWTAuth())
def get_me(request):
    """Получить текущего пользователя."""
    return UserOut.model_validate(request.auth)


@users_router.patch("/me", response=UserOut, auth=JWTAuth())
def update_me(request, data: UserUpdateIn):
    """Обновить профиль."""
    user = UserService.update_user(user=request.auth, **data.model_dump(exclude_unset=True))
    return UserOut.model_validate(user)


@users_router.post("/me/avatar", response={200: UserOut, 400: dict}, auth=JWTAuth())
def upload_avatar(request, file: UploadedFile = File(...)):
    """Загрузить аватар."""
    try:
        user = UserService.update_avatar(request.auth, file)
        return 200, UserOut.model_validate(user)
    except ValidationError as e:
        msg = e.message_dict if hasattr(e, "message_dict") else e.messages
        return 400, {"error": {"code": "VALIDATION_ERROR", "message": msg}}
    except Exception:
        return 400, {"error": {"code": "UPLOAD_ERROR", "message": "Ошибка загрузки файла"}}


@users_router.get("/me/progress", response=list[UserProgressOut], auth=JWTAuth())
def get_progress(request, days: int = 90):
    """Получить историю прогресса."""
    from datetime import date, timedelta

    date_from = date.today() - timedelta(days=days)
    progress = UserProgress.objects.filter(user=request.auth, date__gte=date_from).order_by("-date")

    return [UserProgressOut.model_validate(p) for p in progress]


@users_router.post("/me/progress", response={201: UserProgressOut}, auth=JWTAuth())
def add_progress(request, data: UserProgressIn):
    progress = UserService.add_progress(user=request.auth, weight=data.weight, date_val=data.date, notes=data.notes)
    return progress
