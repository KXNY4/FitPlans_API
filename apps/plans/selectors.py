from decimal import Decimal
from uuid import UUID

from django.db.models import Count, Q, QuerySet

from apps.plans.models import Plan
from apps.purchases.models import Purchase
from apps.users.models import User


class PlanSelector:
    """Запросы для планов."""

    @staticmethod
    def get_published_plans(
        search: str | None = None,
        category: str | None = None,
        difficulty: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        trainer_id: UUID | None = None,
        is_free: bool | None = None,
        ordering: str = "-created_at",
    ) -> QuerySet[Plan]:
        """Получить опубликованные планы с фильтрами."""

        qs = (
            Plan.objects.filter(status=Plan.Status.PUBLISHED)
            .select_related(
                "trainer",
                "trainer__user",
                "category",
            )
            .annotate(purchases_count=Count("purchases", filter=Q(purchases__status=Purchase.Status.COMPLETED)))
        )

        # Фильтры
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if category:
            qs = qs.filter(category__slug=category)

        if difficulty:
            qs = qs.filter(difficulty=difficulty)

        if min_price is not None:
            qs = qs.filter(price__gte=min_price)

        if max_price is not None:
            qs = qs.filter(price__lte=max_price)

        if trainer_id:
            qs = qs.filter(trainer_id=trainer_id)

        if is_free is True:
            qs = qs.filter(price=0)
        elif is_free is False:
            qs = qs.filter(price__gt=0)

        # Сортировка
        if ordering:
            qs = qs.order_by(ordering)

        return qs

    @staticmethod
    def get_plan_with_access(plan_id: UUID, user: User | None) -> dict:
        """Получить план с проверкой доступа."""

        plan = (
            Plan.objects.select_related(
                "trainer",
                "trainer__user",
                "category",
            )
            .prefetch_related("files")
            .get(id=plan_id)
        )

        # Определение доступа
        has_access = False
        is_purchased = False

        if user:
            # Автор плана
            if plan.trainer.user_id == user.id or user.is_admin:
                has_access = True
            # Покупатель
            else:
                is_purchased = Purchase.objects.filter(
                    user=user,
                    plan=plan,
                    status=Purchase.Status.COMPLETED,
                ).exists()
                has_access = is_purchased

        # Фильтрация файлов
        if has_access:
            files = list(plan.files.all())
        else:
            files = list(plan.files.filter(is_preview=True))

        return {
            "id": plan.id,
            "title": plan.title,
            "description": plan.description,
            "short_description": plan.short_description,
            "cover_image": plan.cover_image.url if plan.cover_image else None,
            "price": plan.price,
            "is_free": plan.is_free,
            "difficulty": plan.difficulty,
            "duration_weeks": plan.duration_weeks,
            "category": plan.category,
            "trainer": plan.trainer,
            "files": files,
            "status": plan.status,
            "has_access": has_access,
            "is_purchased": is_purchased,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at,
        }
