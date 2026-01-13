from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from apps.purchases.models import Purchase
from apps.trainers.models import Trainer, TrainerReview
from apps.users.models import User


class TrainerService:
    """Сервис для работы с тренерами."""

    @staticmethod
    @transaction.atomic
    def create_trainer(
        user: User,
        bio: str,
        experience_years: int,
        specializations: list,
    ) -> Trainer:
        """Создать профиль тренера."""

        # Проверка: уже тренер?
        if hasattr(user, "trainer_profile"):
            raise ValidationError("Вы уже являетесь тренером")

        # Создание профиля
        trainer = Trainer.objects.create(
            user=user,
            bio=bio,
            experience_years=experience_years,
            specializations=specializations,
        )

        # Обновление роли
        user.role = User.Role.TRAINER
        user.save(update_fields=["role"])

        # TODO: Отправить уведомление админу для верификации

        return trainer

    @staticmethod
    @transaction.atomic
    def create_review(
        trainer_id: UUID,
        user: User,
        rating: int,
        comment: str,
    ) -> TrainerReview:
        """Создать отзыв о тренере."""

        trainer = Trainer.objects.get(id=trainer_id)

        # Проверка: нельзя оценить себя
        if trainer.user_id == user.id:
            raise ValidationError("Нельзя оставить отзыв о себе")

        # Проверка: покупал ли план этого тренера
        has_purchase = Purchase.objects.filter(
            user=user,
            plan__trainer=trainer,
            status=Purchase.Status.COMPLETED,
        ).exists()

        if not has_purchase:
            raise PermissionDenied("Оставить отзыв можно только после покупки плана")

        # Проверка: уже оставлял отзыв
        if TrainerReview.objects.filter(trainer=trainer, user=user).exists():
            raise ValidationError("Вы уже оставили отзыв")

        review = TrainerReview.objects.create(
            trainer=trainer,
            user=user,
            rating=rating,
            comment=comment,
        )

        # Пересчёт рейтинга
        trainer.update_rating()

        return review
