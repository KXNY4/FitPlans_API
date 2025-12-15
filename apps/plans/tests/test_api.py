import pytest
from ninja.testing import TestClient
from decimal import Decimal

from api.main import api
from apps.plans.models import Plan
from apps.plans.tests.factories import PlanFactory, CategoryFactory
from apps.trainers.tests.factories import TrainerFactory
from apps.users.tests.factories import UserFactory


client = TestClient(api)


@pytest.fixture
def trainer_user(db):
    user = UserFactory(role="TRAINER")
    TrainerFactory(user=user)
    return user


@pytest.fixture
def published_plan(db, trainer_user):
    return PlanFactory(
        trainer=trainer_user.trainer_profile,
        status=Plan.Status.PUBLISHED,
    )


class TestListPlans:
    """Тесты списка планов."""
    
    def test_list_returns_only_published(self, db):
        """Возвращаются только опубликованные планы."""
        PlanFactory(status=Plan.Status.PUBLISHED)
        PlanFactory(status=Plan.Status.DRAFT)
        PlanFactory(status=Plan.Status.ARCHIVED)
        
        response = client.get("/plans/")
        
        assert response.status_code == 200
        assert len(response.json()["items"]) == 1
    
    def test_filter_by_category(self, db):
        """Фильтрация по категории."""
        category = CategoryFactory(slug="strength")
        PlanFactory(category=category, status=Plan.Status.PUBLISHED)
        PlanFactory(status=Plan.Status.PUBLISHED)  # другая категория
        
        response = client.get("/plans/?category=strength")
        
        assert len(response.json()["items"]) == 1
    
    def test_filter_by_price_range(self, db):
        """Фильтрация по цене."""
        PlanFactory(price=Decimal("100"), status=Plan.Status.PUBLISHED)
        PlanFactory(price=Decimal("500"), status=Plan.Status.PUBLISHED)
        PlanFactory(price=Decimal("1000"), status=Plan.Status.PUBLISHED)
        
        response = client.get("/plans/?min_price=200&max_price=600")
        
        assert len(response.json()["items"]) == 1


class TestPlanDetail:
    """Тесты детального просмотра плана."""
    
    def test_anonymous_no_access(self, published_plan):
        """Анонимный пользователь не имеет доступа к файлам."""
        response = client.get(f"/plans/{published_plan.id}")
        
        assert response.status_code == 200
        assert response.json()["has_access"] is False
    
    def test_owner_has_access(self, published_plan, trainer_user):
        """Владелец имеет доступ."""
        from api.auth import create_tokens
        tokens = create_tokens(trainer_user)
        
        response = client.get(
            f"/plans/{published_plan.id}",
            headers={"Authorization": f"Bearer {tokens['access']}"}
        )
        
        assert response.json()["has_access"] is True


class TestCreatePlan:
    """Тесты создания плана."""
    
    def test_trainer_can_create(self, trainer_user):
        """Тренер может создать план."""
        from api.auth import create_tokens
        tokens = create_tokens(trainer_user)
        
        data = {
            "title": "Test Plan",
            "description": "A" * 100,  # min 100 chars
            "price": 1990,
            "difficulty": "BEGINNER",
            "duration_weeks": 4,
        }
        
        response = client.post(
            "/plans/",
            json=data,
            headers={"Authorization": f"Bearer {tokens['access']}"}
        )
        
        assert response.status_code == 201
        assert response.json()["status"] == "DRAFT"
    
    def test_user_cannot_create(self, db):
        """Обычный пользователь не может создать план."""
        user = UserFactory()
        from api.auth import create_tokens
        tokens = create_tokens(user)
        
        data = {
            "title": "Test Plan",
            "description": "A" * 100,
            "price": 1990,
            "difficulty": "BEGINNER",
            "duration_weeks": 4,
        }
        
        response = client.post(
            "/plans/",
            json=data,
            headers={"Authorization": f"Bearer {tokens['access']}"}
        )
        
        assert response.status_code == 403

from django.core.files.uploadedfile import SimpleUploadedFile

class TestPlanFiles:
    """Тесты работы с файлами плана."""
    
    def test_upload_file(self, trainer_user):
        """Загрузка файла к плану."""
        plan = PlanFactory(trainer=trainer_user.trainer_profile)
        
        from api.auth import create_tokens
        tokens = create_tokens(trainer_user)
        
        file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        
        response = client.post(
            f"/plans/{plan.id}/files",
            data={
                "title": "Test File",
                "file_type": "PDF",
                "is_preview": "false",
            },
            FILES={"file": file},
            headers={"Authorization": f"Bearer {tokens['access']}"}
        )
        
        assert response.status_code == 201
        assert response.json()["title"] == "Test File"
        assert plan.files.count() == 1
