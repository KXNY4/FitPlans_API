import factory
from factory.django import DjangoModelFactory

from apps.plans.tests.factories import PlanFactory
from apps.purchases.models import Purchase
from apps.users.tests.factories import UserFactory


class PurchaseFactory(DjangoModelFactory):
    class Meta:
        model = Purchase

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
    price = factory.SelfAttribute("plan.price")
    status = Purchase.Status.COMPLETED
