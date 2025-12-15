from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from ninja.files import UploadedFile
from uuid import UUID
from typing import Optional
from django.db import models

from apps.users.models import User
from apps.trainers.models import Trainer
from apps.plans.models import Plan, PlanFile


class PlanService:
    """Сервис для работы с планами."""
    
    MAX_FILE_SIZES = {
        "PDF": 50 * 1024 * 1024,      # 50MB
        "VIDEO": 500 * 1024 * 1024,   # 500MB
        "IMAGE": 10 * 1024 * 1024,    # 10MB
    }
    
    ALLOWED_EXTENSIONS = {
        "PDF": [".pdf"],
        "VIDEO": [".mp4", ".webm", ".mov"],
        "IMAGE": [".jpg", ".jpeg", ".png", ".webp"],
    }
    
    @staticmethod
    @transaction.atomic
    def create_plan(
        trainer: Trainer,
        title: str,
        description: str,
        price: float,
        difficulty: str,
        duration_weeks: int,
        short_description: str = "",
        category_id: Optional[int] = None,
    ) -> Plan:
        """Создать новый план."""
        
        plan = Plan.objects.create(
            trainer=trainer,
            title=title,
            description=description,
            short_description=short_description,
            price=price,
            difficulty=difficulty,
            duration_weeks=duration_weeks,
            category_id=category_id,
            status=Plan.Status.DRAFT,
        )
        
        return plan
    
    @staticmethod
    def update_plan(
        plan_id: UUID,
        user: User,
        **data
    ) -> Plan:
        """Обновить план."""
        
        plan = Plan.objects.select_related("trainer").get(id=plan_id)
        
        # Проверка прав
        if plan.trainer.user_id != user.id and not user.is_admin:
            raise PermissionDenied("Нет прав для редактирования")
        
        # Обновление полей
        for field, value in data.items():
            if hasattr(plan, field) and value is not None:
                setattr(plan, field, value)
        
        plan.save()
        return plan
    
    @staticmethod
    @transaction.atomic
    def publish_plan(plan_id: UUID, user: User) -> Plan:
        """Опубликовать план."""
        
        plan = Plan.objects.prefetch_related("files").get(id=plan_id)
        
        # Проверка владельца
        if plan.trainer.user_id != user.id:
            raise PermissionDenied("Нет прав для публикации")
        
        # Проверка статуса
        if plan.status != Plan.Status.DRAFT:
            raise ValidationError("Можно публиковать только черновики")
        
        # Проверка требований
        errors = []
        
        if not plan.cover_image:
            errors.append("Добавьте обложку плана")
        
        content_files = plan.files.filter(is_preview=False)
        if not content_files.exists():
            errors.append("Добавьте хотя бы один файл с контентом")
        
        if errors:
            raise ValidationError(errors)
        
        plan.status = Plan.Status.PUBLISHED
        plan.save(update_fields=["status", "updated_at"])
        
        return plan
    
    @staticmethod
    def archive_plan(plan_id: UUID, user: User) -> None:
        """Архивировать план."""
        
        plan = Plan.objects.get(id=plan_id)
        
        if plan.trainer.user_id != user.id and not user.is_admin:
            raise PermissionDenied("Нет прав для удаления")
        
        plan.status = Plan.Status.ARCHIVED
        plan.save(update_fields=["status"])
    
    @staticmethod
    @transaction.atomic
    def add_file(
        plan_id: UUID,
        user: User,
        title: str,
        file: UploadedFile,
        file_type: str,
        is_preview: bool = False,
    ) -> PlanFile:
        """Добавить файл к плану."""
        
        plan = Plan.objects.get(id=plan_id)
        
        # Проверка владельца
        if plan.trainer.user_id != user.id:
            raise PermissionDenied("Нет прав для добавления файлов")
        
        # Проверка размера
        max_size = PlanService.MAX_FILE_SIZES.get(file_type, 0)
        if file.size > max_size:
            raise ValidationError(f"Максимальный размер файла: {max_size // (1024*1024)}MB")
        
        # Проверка расширения
        import os
        ext = os.path.splitext(file.name)[1].lower()
        allowed = PlanService.ALLOWED_EXTENSIONS.get(file_type, [])
        if ext not in allowed:
            raise ValidationError(f"Недопустимый формат. Разрешены: {', '.join(allowed)}")
        
        # Определение порядка
        last_order = plan.files.aggregate(max=models.Max("order"))["max"] or 0
        
        plan_file = PlanFile.objects.create(
            plan=plan,
            title=title,
            file=file,
            file_type=file_type,
            is_preview=is_preview,
            order=last_order + 1,
        )
        
        return plan_file
    
    @staticmethod
    def remove_file(plan_id: UUID, file_id: int, user: User) -> None:
        """Удалить файл плана."""
        
        plan_file = PlanFile.objects.select_related("plan__trainer").get(
            id=file_id,
            plan_id=plan_id,
        )
        
        if plan_file.plan.trainer.user_id != user.id:
            raise PermissionDenied("Нет прав для удаления")
        
        plan_file.file.delete()  # Удаляем из storage
        plan_file.delete()
