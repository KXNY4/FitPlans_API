from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from apps.common.schemas import BaseSchema
from apps.users.schemas import UserShortOut

# === Input ===


class BecomeTrainerIn(BaseModel):
    """Схема заявки на тренера."""

    bio: str = Field(..., min_length=100, max_length=5000)
    experience_years: int = Field(..., ge=0, le=50)
    specializations: list[str] = Field(..., min_length=1, max_length=10)

    @field_validator("specializations")
    @classmethod
    def validate_specializations(cls, v: list[str]) -> list[str]:
        return [s.strip().lower() for s in v if s.strip()]


class TrainerReviewIn(BaseModel):
    """Схема отзыва."""

    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(default="", max_length=2000)


class TrainerSearchListIn(BaseModel):
    """Схема параметров поиска тренеров."""

    search: str | None
    is_verified: bool | None
    min_rating: float | None
    ordering: str = Field(default="-rating")


# === Output ===


class TrainerOut(BaseSchema):
    """Полная схема тренера."""

    id: UUID
    user: UserShortOut
    bio: str
    experience_years: int
    specializations: list[str]
    rating: Decimal
    reviews_count: int = 0
    plans_count: int = 0
    is_verified: bool
    created_at: datetime


class TrainerListOut(BaseSchema):
    """Схема тренера для списка."""

    id: UUID
    user: UserShortOut
    bio: str  # truncated in selector
    experience_years: int
    specializations: list[str]
    rating: Decimal
    reviews_count: int = 0
    is_verified: bool


class TrainerReviewOut(BaseSchema):
    """Схема отзыва."""

    id: int
    user: UserShortOut
    rating: int
    comment: str
    created_at: datetime
