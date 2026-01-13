from django.db.models import QuerySet

from apps.purchases.models import Purchase
from apps.users.models import User


class PurchaseSelector:
    """Запросы для покупок."""

    @staticmethod
    def get_user_purchases(
        user: User,
        status: str | None = None,
    ) -> QuerySet[Purchase]:
        """Получить покупки пользователя."""

        qs = (
            Purchase.objects.filter(user=user)
            .select_related(
                "plan",
                "plan__trainer",
                "plan__trainer__user",
                "plan__category",
            )
            .order_by("-created_at")
        )

        if status:
            qs = qs.filter(status=status)

        return qs
