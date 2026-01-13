import io
from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from ninja.files import UploadedFile
from PIL import Image

from apps.users.models import User


class UserService:
    """Сервис для работы с пользователями."""

    @staticmethod
    @transaction.atomic
    def create_user(
        email: str,
        username: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """Создать нового пользователя."""
        email_lower = email.lower()
        if User.objects.filter(email__iexact=email_lower).exists():
            raise ValidationError({"email": "Пользователь с таким email уже существует"})

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError({"username": "Это имя пользователя уже занято"})

        user = User(
            email=email_lower,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()

        return user

    @staticmethod
    def update_user(user: User, **data) -> User:
        """Обновить профиль пользователя."""
        allowed_fields = {"first_name", "last_name", "height", "weight", "goal"}

        for field, value in data.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        user.save()
        return user

    @staticmethod
    def update_avatar(user: User, file: UploadedFile) -> User:
        """Загрузить и обработать аватар."""
        if not file.content_type.startswith("image/"):
            raise ValidationError({"avatar": "Файл должен быть изображением"})

        if file.size > 5 * 1024 * 1024:
            raise ValidationError({"avatar": "Максимальный размер 5MB"})

        image = Image.open(file)
        image = image.convert("RGB")
        image.thumbnail((300, 300))

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        from django.core.files.uploadedfile import InMemoryUploadedFile

        user.avatar.save(
            f"{user.id}.jpg", InMemoryUploadedFile(buffer, None, f"{user.id}.jpg", "image/jpeg", buffer.tell(), None)
        )

        return user

    @staticmethod
    def add_progress(user: User, weight: float, date_val: date | None = None, notes: str = ""):
        from apps.users.models import UserProgress

        progress = UserProgress.objects.create(
            user=user,
            weight=weight,
            date=date_val or date.today(),
            notes=notes,
        )
        return progress
