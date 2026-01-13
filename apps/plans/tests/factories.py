import random
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from apps.plans.models import Category, Plan, PlanFile
from apps.trainers.tests.factories import TrainerFactory


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.LazyAttribute(lambda o: o.name.lower().replace(" ", "-"))


class PlanFactory(DjangoModelFactory):
    class Meta:
        model = Plan

    trainer = factory.SubFactory(TrainerFactory)
    category = factory.SubFactory(CategoryFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph", nb_sentences=10)
    short_description = factory.Faker("sentence")
    price = factory.LazyFunction(lambda: Decimal(str(random.randint(0, 5000))))
    difficulty = "BEGINNER"
    duration_weeks = 4
    status = "DRAFT"


class PlanFileFactory(DjangoModelFactory):
    class Meta:
        model = PlanFile

    plan = factory.SubFactory(PlanFactory)
    title = factory.Faker("sentence", nb_words=3)
    file = factory.django.FileField(filename="test.pdf")
    file_type = "PDF"
    is_preview = False
