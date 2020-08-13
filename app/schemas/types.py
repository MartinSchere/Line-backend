import graphene
from graphene_django.types import DjangoObjectType
import graphql_geojson

from django.contrib.auth import get_user_model

from ..models import Turn, Store
from ..models import User as UserModel


class TurnType(DjangoObjectType):
    class Meta:
        model = Turn


class StoreType(graphql_geojson.GeoJSONType):
    average_wait_time = graphene.String()

    class Meta:
        model = Store
        geojson_field = 'location'
        convert_choices_to_enum = False


class UserType(DjangoObjectType):
    class Meta:
        model = UserModel


class AuthUserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
