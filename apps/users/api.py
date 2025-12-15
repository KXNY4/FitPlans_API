from ninja import Router, File, Form
from ninja.files import UploadedFile
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from typing import List

from api.auth import JWTAuth, create_tokens
from apps.users.models import User, UserProgress
from apps.users.schemas import (
    RegisterIn, LoginIn, AuthOut, 
    UserOut, UserUpdateIn,
    UserProgressIn, UserProgressOut,
)
from apps.users.services import UserService


auth_router = Router()
users_router = Router()


@auth_router.post("/register", response={201: AuthOut}, auth=None)
def register(request, data: RegisterIn):
    user = UserService.create_user(
        email=data.email,
        username=data.username,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    
    tokens = create_tokens(user)
    
    return 201, {
        "user": UserOut.model_validate(user),
        "tokens": tokens,
    }


@auth_router.post("/login", response={200: AuthOut, 401: dict}, auth=None)
def login(request, data: LoginIn):
    user = authenticate(email=data.email, password=data.password)
    
    if not user:
        return 401, {"error": {"code": "INVALID_CREDENTIALS", "message": "Неверный email или пароль"}}
    
    if not user.is_active:
        return 401, {"error": {"code": "USER_INACTIVE", "message": "Аккаунт деактивирован"}}
    
    tokens = create_tokens(user)
    
    return 200, {
        "user": UserOut.model_validate(user),
        "tokens": tokens,
    }


@auth_router.post("/refresh", auth=None)
def refresh_token(request, refresh: str):
    from ninja_jwt.tokens import RefreshToken
    
    try:
        refresh_token = RefreshToken(refresh)
        return {
            "access": str(refresh_token.access_token),
            "refresh": str(refresh_token),
        }
    except Exception:
        return {"error": {"code": "INVALID_TOKEN", "message": "Невалидный refresh токен"}}


@auth_router.post("/logout", auth=JWTAuth())
def logout(request, refresh: str):
    from ninja_jwt.tokens import RefreshToken
    
    try:
        token = RefreshToken(refresh)
        token.blacklist()
        return {"message": "Успешный выход"}
    except Exception:
        return {"error": {"code": "INVALID_TOKEN", "message": "Ошибка выхода"}}


@users_router.get("/me", response=UserOut, auth=JWTAuth())
def get_me(request):
    return UserOut.model_validate(request.auth)


@users_router.patch("/me", response=UserOut, auth=JWTAuth())
def update_me(request, data: UserUpdateIn):
    user = UserService.update_user(
        user=request.auth,
        **data.model_dump(exclude_unset=True)
    )
    return UserOut.model_validate(user)


@users_router.post("/me/avatar", response={200: UserOut, 400: dict}, auth=JWTAuth())
def upload_avatar(request, file: UploadedFile = File(...)):
    try:
        user = UserService.update_avatar(request.auth, file)
        return 200, UserOut.model_validate(user)
    except ValidationError as e:
        msg = e.message_dict if hasattr(e, 'message_dict') else e.messages
        return 400, {"error": {"code": "VALIDATION_ERROR", "message": msg}}
    except Exception:
        return 400, {"error": {"code": "UPLOAD_ERROR", "message": "Ошибка загрузки файла"}}


@users_router.get("/me/progress", response=List[UserProgressOut], auth=JWTAuth())
def get_progress(request, days: int = 90):
    from datetime import date, timedelta
    
    date_from = date.today() - timedelta(days=days)
    progress = UserProgress.objects.filter(
        user=request.auth,
        date__gte=date_from
    ).order_by("-date")
    
    return [UserProgressOut.model_validate(p) for p in progress]


@users_router.post("/me/progress", response={201: UserProgressOut}, auth=JWTAuth())
def add_progress(request, data: UserProgressIn):
    progress = UserService.add_progress(
