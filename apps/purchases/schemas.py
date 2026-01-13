from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AliasPath, Field

from apps.common.schemas import BaseSchema, ImageStr
from apps.plans.schemas import PlanListOut


class PurchaseOut(BaseSchema):
    """Схема покупки."""

    id: UUID
    plan: PlanListOut
    price: Decimal
    status: str
    created_at: datetime


class PurchaseListOut(BaseSchema):
    """Схема для списка покупок."""

    id: UUID
    plan_id: UUID
    plan_title: str = Field(validation_alias=AliasPath("plan", "title"))
    plan_cover: ImageStr = Field(validation_alias=AliasPath("plan", "cover_image"))
    price: Decimal
    status: str
    created_at: datetime
