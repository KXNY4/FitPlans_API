from celery import shared_task

from apps.notifications.models import Notification
from apps.purchases.models import Purchase


@shared_task
def send_purchase_notification(purchase_id):
    """Отправить уведомление о покупке."""
    try:
        purchase = Purchase.objects.select_related("user", "plan").get(id=purchase_id)

        Notification.objects.create(
            user=purchase.user,
            message=f"Вы успешно купили план '{purchase.plan.title}'!",
        )

        # Также можно отправить email
        # send_mail(...)

    except Purchase.DoesNotExist:
        pass
