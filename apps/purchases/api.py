from uuid import UUID

from ninja import Router
from ninja.pagination import paginate

from api.auth import JWTAuth
from apps.purchases.models import Purchase
from apps.purchases.schemas import PurchaseListOut, PurchaseOut
from apps.purchases.selectors import PurchaseSelector

router = Router()


@router.get("/", response=list[PurchaseListOut], auth=JWTAuth())
@paginate
def list_purchases(
    request,
    status: str | None = None,
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
    purchase = Purchase.objects.select_related("plan", "plan__trainer", "plan__trainer__user", "plan__category").get(
        id=purchase_id, user=request.auth
    )

    return PurchaseOut.model_validate(purchase)


@router.post("/webhook/mock", auth=None)
def mock_payment_webhook(request, purchase_id: UUID):
    """
    [DEV ONLY] Симуляция успешной оплаты.

    Переводит покупку в статус COMPLETED.
    """
    from apps.purchases.services import PurchaseService

    PurchaseService.complete_purchase(purchase_id, f"mock_{purchase_id.hex[:8]}")
    return {"status": "success", "message": "Payment completed"}
