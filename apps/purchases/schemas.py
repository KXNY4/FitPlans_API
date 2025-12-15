from pydantic import BaseModel, Field, AliasPath
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional

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
