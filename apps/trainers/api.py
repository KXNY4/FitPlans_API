from ninja import Router, Query
from ninja.pagination import paginate
from typing import List
from uuid import UUID

from api.auth import JWTAuth, OptionalJWTAuth
from apps.trainers.models import Trainer, TrainerReview
from apps.trainers.schemas import (
    BecomeTrainerIn, TrainerOut, TrainerListOut,
    TrainerReviewIn, TrainerReviewOut,
)
from apps.trainers.services import TrainerService
from apps.trainers.selectors import TrainerSelector
from apps.common.schemas import PaginatedResponse


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


@router.get("/", response=List[TrainerListOut])
@paginate
def list_trainers(
    request,
    search: str = None,
    is_verified: bool = None,
    min_rating: float = None,
    ordering: str = "-rating",
):
    """
    Список тренеров.
    
    Фильтрация по верификации, рейтингу.
    Сортировка: rating, -rating, created_at, experience_years
    """
    return TrainerSelector.get_trainers_list(
        search=search,
        is_verified=is_verified,
        min_rating=min_rating,
        ordering=ordering,
    )


@router.get("/{trainer_id}", response=TrainerOut)
def get_trainer(request, trainer_id: UUID):
    """Получить профиль тренера."""
    trainer = TrainerSelector.get_trainer_detail(trainer_id)
    return TrainerOut.model_validate(trainer)


@router.get("/{trainer_id}/reviews", response=List[TrainerReviewOut])
def get_trainer_reviews(request, trainer_id: UUID):
    """Отзывы о тренере."""
    reviews = TrainerReview.objects.filter(
        trainer_id=trainer_id
    ).select_related("user").order_by("-created_at")
    
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
