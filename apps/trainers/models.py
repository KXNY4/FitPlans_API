from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import UUIDModel, TimeStampedModel
from apps.users.models import User


class Trainer(UUIDModel, TimeStampedModel):
    """Профиль тренера."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="trainer_profile"
    )
    bio = models.TextField()
    experience_years = models.PositiveIntegerField(default=0)
    specializations = models.JSONField(default=list)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "trainers"

    def update_rating(self) -> None:
        """Пересчёт рейтинга."""
        from django.db.models import Avg
        avg = self.reviews.aggregate(Avg("rating"))["rating__avg"]
        self.rating = avg or 0
        self.save(update_fields=["rating"])


class TrainerReview(TimeStampedModel):
    """Отзыв о тренере."""
    
    trainer = models.ForeignKey(
        Trainer, 
        on_delete=models.CASCADE, 
        related_name="reviews"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, default="")

    class Meta:
        db_table = "trainer_reviews"
        unique_together = ["trainer", "user"]
