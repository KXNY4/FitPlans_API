from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel
from apps.trainers.models import Trainer


class Category(models.Model):
    """Категория планов."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        db_table = "categories"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Plan(UUIDModel, TimeStampedModel):
    """Тренировочный план."""

    class Difficulty(models.TextChoices):
        BEGINNER = "BEGINNER", "Начинающий"
        INTERMEDIATE = "INTERMEDIATE", "Средний"
        ADVANCED = "ADVANCED", "Продвинутый"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Черновик"
        PUBLISHED = "PUBLISHED", "Опубликован"
        ARCHIVED = "ARCHIVED", "В архиве"

    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="plans")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="plans")
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    duration_weeks = models.PositiveIntegerField(default=4)
    cover_image = models.ImageField(upload_to="plan_covers/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        db_table = "plans"
        ordering = ["-created_at"]

    @property
    def is_free(self) -> bool:
        return self.price == 0


class PlanFile(TimeStampedModel):
    """Файл плана."""

    class FileType(models.TextChoices):
        PDF = "PDF", "PDF"
        VIDEO = "VIDEO", "Видео"
        IMAGE = "IMAGE", "Изображение"

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="files")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="plan_files/")
    file_type = models.CharField(max_length=20, choices=FileType.choices, default=FileType.PDF)
    is_preview = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "plan_files"
        ordering = ["order"]
