from datetime import date

import pytest
from ninja.testing import TestClient

from api.main import api
from apps.users.models import UserProgress
from apps.users.tests.factories import UserFactory

client = TestClient(api)


@pytest.mark.django_db
class TestUserProgress:
    """Тесты API для работы с прогрессом пользователя."""

    def test_add_and_get_progress(self):
        """Тест добавления и получения прогресса."""
        user = UserFactory()
        from api.auth import create_tokens

        tokens = create_tokens(user)
        # headers = {"Authorization": f"Bearer {tokens['access']}"}
        # Используем Cookies
        client.cookies["access_token"] = tokens["access"]

        # 1. Добавляем прогресс
        data = {"weight": 75.5, "date": str(date.today()), "notes": "Начало тренировок"}
        response = client.post("/users/me/progress", json=data)

        assert response.status_code == 201
        assert float(response.json()["weight"]) == 75.5
        assert UserProgress.objects.count() == 1

        # 2. Получаем прогресс
        response = client.get("/users/me/progress")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert float(response.json()[0]["weight"]) == 75.5

    def test_get_progress_empty(self):
        """Тест получения пустого списка прогресса."""
        user = UserFactory()
        from api.auth import create_tokens

        tokens = create_tokens(user)
        client.cookies["access_token"] = tokens["access"]

        response = client.get("/users/me/progress")
        assert response.status_code == 200
        assert response.json() == []
