from django.db import models
from apps.common.models import UUIDModel, TimeStampedModel
from apps.users.models import User
from apps.plans.models import Plan


class Purchase(UUIDModel, TimeStampedModel):
    """Покупка плана."""
    
    class Status(models.TextChoices):
        PENDING = "PENDING", "Ожидает оплаты"
        COMPLETED = "COMPLETED", "Завершена"
        REFUNDED = "REFUNDED", "Возврат"
        FAILED = "FAILED", "Ошибка"
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="purchases"
    )
    plan = models.ForeignKey(
        Plan, 
        on_delete=models.CASCADE, 
        related_name="purchases"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    payment_id = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "purchases"
        unique_together = ["user", "plan"]
        ordering = ["-created_at"]
