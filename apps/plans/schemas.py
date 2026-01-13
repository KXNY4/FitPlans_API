from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field

from apps.common.schemas import BaseSchema, FileUrl, ImageStr, validate_queryset
from apps.trainers.schemas import TrainerListOut

# === Input ===


class PlanCreateIn(BaseModel):
    """Схема создания плана."""

    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=100, max_length=50000)
    short_description: str = Field(default="", max_length=500)
    price: Decimal = Field(..., ge=0, le=999999.99)
    difficulty: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED"]
    duration_weeks: int = Field(..., ge=1, le=52)
    category_id: int | None = None


class PlanUpdateIn(BaseModel):
    """Схема обновления плана."""

    title: str | None = Field(None, min_length=5, max_length=200)
    description: str | None = Field(None, min_length=100, max_length=50000)
    short_description: str | None = Field(None, max_length=500)
    price: Decimal | None = Field(None, ge=0, le=999999.99)
    difficulty: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED"] | None = None
    duration_weeks: int | None = Field(None, ge=1, le=52)
    category_id: int | None = None


class PlanFileIn(BaseModel):
    """Схема загрузки файла."""

    title: str = Field(..., max_length=255)
    file_type: Literal["PDF", "VIDEO", "IMAGE"]
    is_preview: bool = False


class PlanFilterParams(BaseModel):
    """Параметры фильтрации планов."""

    search: str | None = None
    category: str | None = None
    difficulty: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED"] | None = None
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    trainer_id: UUID | None = None
    is_free: bool | None = None
    ordering: Literal["-created_at", "created_at", "-price", "price", "-purchases_count"] = "-created_at"


# === Output ===


class CategoryOut(BaseSchema):
    """Схема категории."""

    id: int
    name: str
    slug: str
    icon: str = ""
    plans_count: int = 0


class PlanFileOut(BaseSchema):
    """Схема файла плана."""

    id: int
    title: str
    file: FileUrl
    file_type: str
    is_preview: bool
    order: int


class PlanListOut(BaseSchema):
    """Схема плана для списка."""

    id: UUID
    title: str
    short_description: str
    cover_image: ImageStr = None
    price: Decimal
    is_free: bool
    difficulty: str
    duration_weeks: int
    category: CategoryOut | None = None
    trainer: TrainerListOut
    purchases_count: int = 0
    created_at: datetime


class PlanDetailOut(BaseSchema):
    """Полная схема плана."""

    id: UUID
    title: str
    description: str
    short_description: str
    cover_image: ImageStr = None
    price: Decimal
    is_free: bool
    difficulty: str
    duration_weeks: int
    category: CategoryOut | None = None
    trainer: TrainerListOut
    files: Annotated[list[PlanFileOut], BeforeValidator(validate_queryset)] = []
    status: str
    has_access: bool = False
    is_purchased: bool = False
    created_at: datetime
    updated_at: datetime


class PurchaseResultOut(BaseModel):
    """Результат покупки."""

    status: Literal["completed", "pending"]
    purchase_id: UUID
    message: str
    payment_url: str | None = None
