import factory
from factory.django import DjangoModelFactory
from apps.trainers.models import Trainer
from apps.users.tests.factories import UserFactory

class TrainerFactory(DjangoModelFactory):
    class Meta:
        model = Trainer
    
    user = factory.SubFactory(UserFactory, role="TRAINER")
    bio = factory.Faker("text")
    experience_years = 5
    specializations = ["Strength", "Cardio"]
    is_verified = True
