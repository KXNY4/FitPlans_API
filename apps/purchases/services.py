from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.plans.models import Plan
from apps.plans.schemas import PurchaseResultOut
from apps.purchases.models import Purchase
from apps.users.models import User


class PurchaseService:
    """Сервис покупок."""

    @staticmethod
    def has_purchased(user: User, plan: Plan) -> bool:
        """Проверить, купил ли пользователь план."""
        return Purchase.objects.filter(
            user=user,
            plan=plan,
            status=Purchase.Status.COMPLETED,
        ).exists()

    @staticmethod
    @transaction.atomic
    def create_purchase(user: User, plan_id: UUID) -> PurchaseResultOut:
        """Создать покупку."""

        plan = Plan.objects.select_related("trainer").get(id=plan_id)

        # Проверка: план опубликован?
        if plan.status != Plan.Status.PUBLISHED:
            raise ValidationError("План недоступен для покупки")

        # Проверка: не свой план?
        if plan.trainer.user_id == user.id:
            raise ValidationError("Нельзя купить собственный план")

        # Проверка: уже куплен?
        existing = Purchase.objects.filter(user=user, plan=plan).first()
        if existing:
            if existing.status == Purchase.Status.COMPLETED:
                raise ValidationError("Вы уже купили этот план")
            # Если PENDING — удаляем и создаём заново
            existing.delete()

        # Создание покупки
        purchase = Purchase.objects.create(
            user=user,
            plan=plan,
            price=plan.price,
            status=Purchase.Status.PENDING,
        )

        # Если бесплатный — сразу завершаем
        if plan.is_free:
            purchase.status = Purchase.Status.COMPLETED
            purchase.save(update_fields=["status"])

            # Отправить уведомление
            from apps.notifications.tasks import send_purchase_notification

            send_purchase_notification.delay(str(purchase.id))

            return PurchaseResultOut(
                status="completed",
                purchase_id=purchase.id,
                message="План добавлен в вашу библиотеку",
            )

        # Создание платежа (интеграция с платёжной системой)
        payment_url = PurchaseService._create_payment(purchase)

        return PurchaseResultOut(
            status="pending",
            purchase_id=purchase.id,
            message="Перейдите по ссылке для оплаты",
            payment_url=payment_url,
        )

    @staticmethod
    def _create_payment(purchase: Purchase) -> str:
        """Создать платёж в платёжной системе."""
        # TODO: Интеграция со Stripe/YooKassa
        return f"https://payment.example.com/pay/{purchase.id}"

    @staticmethod
    @transaction.atomic
    def complete_purchase(purchase_id: UUID, payment_id: str) -> Purchase:
        """Завершить покупку после оплаты."""

        purchase = Purchase.objects.select_related("plan", "user").get(id=purchase_id)

        if purchase.status != Purchase.Status.PENDING:
            raise ValidationError("Покупка уже обработана")

        purchase.status = Purchase.Status.COMPLETED
        purchase.payment_id = payment_id
        purchase.save(update_fields=["status", "payment_id"])

        # Уведомления
        from apps.notifications.tasks import send_purchase_notification

        send_purchase_notification.delay(str(purchase.id))

        return purchase
