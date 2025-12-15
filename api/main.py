from ninja import NinjaAPI
from ninja.errors import ValidationError, HttpError
from django.core.exceptions import ValidationError as DjangoValidationError

from api.auth import JWTAuth, OptionalJWTAuth
# from api.exceptions import api_exception_handler # Not implemented yet

from apps.users.api import auth_router, users_router
from apps.trainers.api import router as trainers_router
from apps.plans.api import router as plans_router
from apps.purchases.api import router as purchases_router


api = NinjaAPI(
    title="FitPlans API",
    version="1.0.0",
    description="API для платформы продажи тренировочных планов",
    docs_url="/docs",  # Swagger UI
    openapi_url="/openapi.json",
)

# Глобальные обработчики ошибок
@api.exception_handler(DjangoValidationError)
def django_validation_error_handler(request, exc):
    return api.create_response(
        request,
        {"error": {"code": "VALIDATION_ERROR", "message": exc.messages[0]}},
        status=400,
    )

@api.exception_handler(ValidationError)
def validation_error_handler(request, exc):
    return api.create_response(
        request,
        {"error": {"code": "VALIDATION_ERROR", "details": exc.errors}},
        status=400,
    )

@api.exception_handler(HttpError)
def http_error_handler(request, exc):
    return api.create_response(
        request,
        {"error": {"code": exc.message, "message": str(exc)}},
        status=exc.status_code,
    )

# Подключение роутеров
api.add_router("/auth", auth_router, tags=["Auth"])
api.add_router("/users", users_router, tags=["Users"])
api.add_router("/trainers", trainers_router, tags=["Trainers"])
api.add_router("/plans", plans_router, tags=["Plans"])
api.add_router("/purchases", purchases_router, tags=["Purchases"])
