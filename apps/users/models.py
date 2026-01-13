from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import UUIDModel


class User(UUIDModel, AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "Пользователь"
        TRAINER = "TRAINER", "Тренер"
        ADMIN = "ADMIN", "Администратор"

    class Goal(models.TextChoices):
        WEIGHT_LOSS = "WEIGHT_LOSS", "Похудение"
        MUSCLE_GAIN = "MUSCLE_GAIN", "Набор массы"
        STRENGTH = "STRENGTH", "Сила"
        ENDURANCE = "ENDURANCE", "Выносливость"
        MAINTENANCE = "MAINTENANCE", "Поддержание"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    height = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    goal = models.CharField(max_length=20, choices=Goal.choices, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"

    @property
    def is_trainer(self) -> bool:
        return self.role == self.Role.TRAINER

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress_records")
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "user_progress"
        ordering = ["-date"]
        unique_together = ["user", "date"]
