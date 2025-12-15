from ninja import Router, File, Form, Query
from ninja.files import UploadedFile
from ninja.pagination import paginate
from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from django.db.models import Count, Q

from api.auth import JWTAuth, OptionalJWTAuth
from apps.plans.models import Plan, Category, PlanFile
from apps.plans.schemas import (
    PlanCreateIn, PlanUpdateIn, PlanFilterParams,
    PlanListOut, PlanDetailOut, 
    CategoryOut, PlanFileIn, PlanFileOut,
    PurchaseResultOut,
)
from apps.plans.services import PlanService
from apps.plans.selectors import PlanSelector
from apps.purchases.services import PurchaseService


router = Router()


# === Categories ===

@router.get("/categories", response=List[CategoryOut], auth=None)
def list_categories(request):
    """Список категорий."""
    categories = Category.objects.annotate(
        plans_count=Count("plans", filter=Q(plans__status="PUBLISHED"))
    )
    return [CategoryOut.model_validate(c) for c in categories]


# === Plans List ===

@router.get("/", response=List[PlanListOut], auth=None)
@paginate
def list_plans(request, filters: PlanFilterParams = Query(...)):
    """
    Каталог планов.
    
    Фильтры:
    - search: поиск по названию и описанию
    - category: slug категории
    - difficulty: BEGINNER, INTERMEDIATE, ADVANCED
    - min_price, max_price: диапазон цен
    - trainer_id: планы конкретного тренера
    - is_free: только бесплатные
    
    Сортировка: -created_at, price, -price, -purchases_count
    """
    return PlanSelector.get_published_plans(
        search=filters.search,
        category=filters.category,
        difficulty=filters.difficulty,
        min_price=filters.min_price,
        max_price=filters.max_price,
        trainer_id=filters.trainer_id,
        is_free=filters.is_free,
        ordering=filters.ordering,
    )


# === Plan Detail ===

@router.get("/{plan_id}", response=PlanDetailOut, auth=OptionalJWTAuth())
def get_plan(request, plan_id: UUID):
    """
    Детали плана.
    
    Возвращает has_access=true если пользователь:
    - Автор плана
    - Купил план
    - Админ
    
    Файлы без is_preview скрыты если нет доступа.
    """
    user = request.auth
    if user == "Anonymous":
        user = None
    
    plan_data = PlanSelector.get_plan_with_access(plan_id, user)
    
    return PlanDetailOut.model_validate(plan_data)


# === Plan CRUD (Trainer) ===

@router.post("/", response={201: PlanDetailOut}, auth=JWTAuth())
def create_plan(request, data: PlanCreateIn):
    """
    Создать план.
    
    Только для тренеров. План создаётся в статусе DRAFT.
    """
    if not getattr(request.auth, "is_trainer", False):
        raise HttpError(403, "Только тренеры могут создавать планы")

    plan = PlanService.create_plan(
        trainer=request.auth.trainer_profile,
        **data.model_dump()
    )
    return 201, PlanDetailOut.model_validate(plan)


@router.patch("/{plan_id}", response=PlanDetailOut, auth=JWTAuth())
def update_plan(request, plan_id: UUID, data: PlanUpdateIn):
    """Обновить план."""
    plan = PlanService.update_plan(
        plan_id=plan_id,
        user=request.auth,
        **data.model_dump(exclude_unset=True)
    )
    return PlanDetailOut.model_validate(plan)


@router.delete("/{plan_id}", response={204: None}, auth=JWTAuth())
def delete_plan(request, plan_id: UUID):
    """Удалить план (переводит в ARCHIVED)."""
    PlanService.archive_plan(plan_id, request.auth)
    return 204, None


@router.post("/{plan_id}/publish", response=PlanDetailOut, auth=JWTAuth())
def publish_plan(request, plan_id: UUID):
    """
    Опубликовать план.
    
    Требования:
    - Все обязательные поля заполнены
    - Есть хотя бы 1 файл (не preview)
    - Есть обложка
    """
    plan = PlanService.publish_plan(plan_id, request.auth)
    return PlanDetailOut.model_validate(plan)


# === Plan Files ===

@router.post("/{plan_id}/files", response={201: PlanFileOut}, auth=JWTAuth())
def upload_file(
    request,
    plan_id: UUID,
    title: str = Form(...),
    file_type: str = Form(...),
    is_preview: bool = Form(False),
    file: UploadedFile = File(...),
):
    """
    Загрузить файл к плану.
    
    Ограничения:
    - PDF: до 50MB
    - VIDEO: до 500MB
    - IMAGE: до 10MB
    """
    plan_file = PlanService.add_file(
        plan_id=plan_id,
        user=request.auth,
        title=title,
        file=file,
        file_type=file_type,
        is_preview=is_preview,
    )
    return 201, PlanFileOut.model_validate(plan_file)


@router.delete("/{plan_id}/files/{file_id}", response={204: None}, auth=JWTAuth())
def delete_file(request, plan_id: UUID, file_id: int):
    """Удалить файл плана."""
    PlanService.remove_file(plan_id, file_id, request.auth)
    return 204, None


# === Purchase ===

@router.post("/{plan_id}/purchase", response=PurchaseResultOut, auth=JWTAuth())
def purchase_plan(request, plan_id: UUID):
    """
    Купить план.
    
    Если план бесплатный — сразу COMPLETED.
    Если платный — возвращает URL для оплаты.
    """
    result = PurchaseService.create_purchase(
        user=request.auth,
        plan_id=plan_id,
    )
    return result
