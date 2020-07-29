from graphene_django.types import DjangoObjectType

from django.contrib.auth import get_user_model

from ..models import Turn, Store
from ..models import User as UserModel


class TurnType(DjangoObjectType):
    class Meta:
        model = Turn


class StoreType(DjangoObjectType):
    class Meta:
        model = Store


class UserType(DjangoObjectType):
    class Meta:
        model = UserModel


class AuthUserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
