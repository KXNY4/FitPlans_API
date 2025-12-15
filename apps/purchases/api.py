from ninja import Router
from ninja.pagination import paginate
from typing import List, Optional
from uuid import UUID

from api.auth import JWTAuth
from apps.purchases.models import Purchase
from apps.purchases.schemas import PurchaseOut, PurchaseListOut
from apps.purchases.selectors import PurchaseSelector


router = Router()


@router.get("/", response=List[PurchaseListOut], auth=JWTAuth())
@paginate
def list_purchases(
    request,
    status: Optional[str] = None,
):
    """
    Мои покупки.
    
    Фильтр по статусу: COMPLETED, PENDING, REFUNDED
    """
    return PurchaseSelector.get_user_purchases(
        user=request.auth,
        status=status,
    )


@router.get("/{purchase_id}", response=PurchaseOut, auth=JWTAuth())
def get_purchase(request, purchase_id: UUID):
    """Детали покупки."""
    purchase = Purchase.objects.select_related(
        "plan", "plan__trainer", "plan__trainer__user", "plan__category"
    ).get(id=purchase_id, user=request.auth)
    
    return PurchaseOut.model_validate(purchase)
