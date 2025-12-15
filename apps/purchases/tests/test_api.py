import pytest
from ninja.testing import TestClient
from decimal import Decimal
from unittest.mock import patch

from api.main import api
from apps.plans.models import Plan
from apps.purchases.models import Purchase
from apps.plans.tests.factories import PlanFactory
from apps.users.tests.factories import UserFactory
from apps.purchases.tests.factories import PurchaseFactory


client = TestClient(api)


class TestPurchasePlan:
    """Тесты покупки плана."""
    
    def test_purchase_free_plan(self, db):
        """Покупка бесплатного плана."""
        user = UserFactory()
        plan = PlanFactory(price=Decimal("0"), status=Plan.Status.PUBLISHED)
        
        from api.auth import create_tokens
        tokens = create_tokens(user)
        
        with patch("apps.notifications.tasks.send_purchase_notification.delay") as mock_notify:
            response = client.post(
                f"/plans/{plan.id}/purchase",
                headers={"Authorization": f"Bearer {tokens['access']}"}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "completed"
            assert Purchase.objects.filter(user=user, plan=plan, status="COMPLETED").exists()
            mock_notify.assert_called_once()
    
    def test_purchase_paid_plan(self, db):
        """Покупка платного плана."""
        user = UserFactory()
        plan = PlanFactory(price=Decimal("1000"), status=Plan.Status.PUBLISHED)
        
        from api.auth import create_tokens
        tokens = create_tokens(user)
        
        response = client.post(
            f"/plans/{plan.id}/purchase",
            headers={"Authorization": f"Bearer {tokens['access']}"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "pending"
        assert response.json()["payment_url"] is not None
        assert Purchase.objects.filter(user=user, plan=plan, status="PENDING").exists()
    
    def test_cannot_purchase_own_plan(self, db):
        """Нельзя купить свой план."""
        user = UserFactory(role="TRAINER")
        from apps.trainers.tests.factories import TrainerFactory
        trainer = TrainerFactory(user=user)
        plan = PlanFactory(trainer=trainer, status=Plan.Status.PUBLISHED)
        
        from api.auth import create_tokens
        tokens = create_tokens(user)
        
        response = client.post(
            f"/plans/{plan.id}/purchase",
            headers={"Authorization": f"Bearer {tokens['access']}"}
        )
        
        assert response.status_code == 400
        assert "Нельзя купить собственный план" in response.json()["error"]["message"]


class TestListPurchases:
    """Тесты списка покупок."""
    
    def test_list_my_purchases(self, db):
        """Список моих покупок."""
        user = UserFactory()
        PurchaseFactory(user=user)
        PurchaseFactory(user=user)
        PurchaseFactory()  # чужая покупка
        
        from api.auth import create_tokens
        tokens = create_tokens(user)
        
        response = client.get(
            "/purchases/",
            headers={"Authorization": f"Bearer {tokens['access']}"}
        )
        
        assert response.status_code == 200
        assert len(response.json()["items"]) == 2
