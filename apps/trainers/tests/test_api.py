from decimal import Decimal

from ninja.testing import TestClient

from api.main import api
from apps.trainers.models import Trainer
from apps.trainers.tests.factories import TrainerFactory
from apps.users.tests.factories import UserFactory

client = TestClient(api)


class TestBecomeTrainer:
    """Тесты становления тренером."""

    def test_become_trainer_success(self, db):
        """Успешная заявка."""
        user = UserFactory(role="USER")
        from api.auth import create_tokens

        tokens = create_tokens(user)
        client.cookies["access_token"] = tokens["access"]

        data = {
            "bio": "I am a pro trainer " * 10,
            "experience_years": 5,
            "specializations": ["Strength", "Cardio"],
        }

        response = client.post("/trainers/become", json=data)

        assert response.status_code == 201
        assert Trainer.objects.filter(user=user).exists()
        user.refresh_from_db()
        assert user.role == "TRAINER"

    def test_already_trainer(self, db):
        """Уже тренер."""
        user = UserFactory(role="TRAINER")
        TrainerFactory(user=user)
        from api.auth import create_tokens

        tokens = create_tokens(user)
        client.cookies["access_token"] = tokens["access"]

        response = client.post(
            "/trainers/become",
            json={"bio": "test " * 20, "experience_years": 1, "specializations": ["Yoga"]},
        )

        assert response.status_code == 400
        assert "Вы уже являетесь тренером" in response.json()["error"]["message"]


class TestTrainerReviews:
    """Тесты отзывов."""

    def test_leave_review(self, db):
        """Оставить отзыв."""
        trainer_user = UserFactory(role="TRAINER")
        trainer = TrainerFactory(user=trainer_user)

        user = UserFactory()
        from api.auth import create_tokens

        tokens = create_tokens(user)
        client.cookies["access_token"] = tokens["access"]

        # Покупаем план тренера
        from apps.plans.tests.factories import PlanFactory
        from apps.purchases.tests.factories import PurchaseFactory

        plan = PlanFactory(trainer=trainer)
        PurchaseFactory(user=user, plan=plan, status="COMPLETED")

        response = client.post(
            f"/trainers/{trainer.id}/reviews",
            json={"rating": 5, "comment": "Great trainer!"},
        )

        # Если проверка покупки есть, тест упадет. Если нет - пройдет.
        # Проверим код сервиса.
        assert response.status_code == 201
        assert trainer.reviews.count() == 1

        trainer.refresh_from_db()
        assert trainer.rating == Decimal("5.00")
