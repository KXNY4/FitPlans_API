from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel
from apps.users.models import User


class Notification(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
