import factory
from factory.django import DjangoModelFactory
from .models import User, Buyer, Seller
from .services import create_user
from abc import ABC, abstractmethod # Importing ABC and abstractmethod for defining abstract classes

class UserFactory:
    @staticmethod
    def create_user(user_type, **kwargs):
        return create_user(user_type, **kwargs)
    