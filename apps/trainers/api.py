from uuid import UUID

from ninja import Router
from ninja.pagination import paginate

from api.auth import JWTAuth
from apps.trainers.models import TrainerReview
from apps.trainers.schemas import (
    BecomeTrainerIn,
    TrainerListOut,
    TrainerOut,
    TrainerReviewIn,
    TrainerReviewOut,
    TrainerSearchListIn,
)
from apps.trainers.selectors import TrainerSelector
from apps.trainers.services import TrainerService

router = Router()


@router.post("/become", response={201: TrainerOut}, auth=JWTAuth())
def become_trainer(request, data: BecomeTrainerIn):
    """
    Стать тренером.

    Создаёт профиль тренера для текущего пользователя.
    """
    trainer = TrainerService.create_trainer(
        user=request.auth,
        bio=data.bio,
        experience_years=data.experience_years,
        specializations=data.specializations,
    )
    return 201, TrainerOut.model_validate(trainer)


@router.get("/", response=list[TrainerListOut])
@paginate
def list_trainers(request, data: TrainerSearchListIn):
    """
    Список тренеров.

    Фильтрация по верификации, рейтингу.
    Сортировка: rating, -rating, created_at, experience_years
    """
    return TrainerSelector.get_trainers_list(
        search=data.search,
        is_verified=data.is_verified,
        min_rating=data.min_rating,
        ordering=data.ordering,
    )


@router.get("/{trainer_id}", response=TrainerOut)
def get_trainer(request, trainer_id: UUID):
    """Получить профиль тренера."""
    trainer = TrainerSelector.get_trainer_detail(trainer_id)
    return TrainerOut.model_validate(trainer)


@router.get("/{trainer_id}/reviews", response=list[TrainerReviewOut])
def get_trainer_reviews(request, trainer_id: UUID):
    """Отзывы о тренере."""
    reviews = TrainerReview.objects.filter(trainer_id=trainer_id).select_related("user").order_by("-created_at")

    return [TrainerReviewOut.model_validate(r) for r in reviews]


@router.post("/{trainer_id}/reviews", response={201: TrainerReviewOut}, auth=JWTAuth())
def create_review(request, trainer_id: UUID, data: TrainerReviewIn):
    """
    Оставить отзыв о тренере.

    Можно только если покупал план этого тренера.
    """
    review = TrainerService.create_review(
        trainer_id=trainer_id,
        user=request.auth,
        rating=data.rating,
        comment=data.comment,
    )
    return 201, TrainerReviewOut.model_validate(review)
