from django.db.models import QuerySet, Count, Q
from typing import Optional
from uuid import UUID

from apps.trainers.models import Trainer
from apps.plans.models import Plan


class TrainerSelector:
    """Запросы для тренеров."""
    
    @staticmethod
    def get_trainers_list(
        search: Optional[str] = None,
        is_verified: Optional[bool] = None,
        min_rating: Optional[float] = None,
        ordering: str = "-rating",
    ) -> QuerySet[Trainer]:
        """Список тренеров."""
        
        qs = Trainer.objects.select_related(
            "user"
        ).annotate(
            reviews_count=Count("reviews"),
            plans_count=Count(
                "plans",
                filter=Q(plans__status=Plan.Status.PUBLISHED)
            ),
        )
        
        if search:
            qs = qs.filter(
                Q(bio__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        if is_verified is not None:
            qs = qs.filter(is_verified=is_verified)
        
        if min_rating:
            qs = qs.filter(rating__gte=min_rating)
        
        if ordering:
            qs = qs.order_by(ordering)
        
        return qs
    
    @staticmethod
    def get_trainer_detail(trainer_id: UUID) -> Trainer:
        """Детали тренера."""
        
        return Trainer.objects.select_related(
            "user"
        ).prefetch_related(
            "plans",
        ).annotate(
            reviews_count=Count("reviews"),
            plans_count=Count(
                "plans",
                filter=Q(plans__status=Plan.Status.PUBLISHED)
            ),
        ).get(id=trainer_id)
