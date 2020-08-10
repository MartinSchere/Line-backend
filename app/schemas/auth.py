
import graphene

from . import schema
from graphql import GraphQLError
from .types import UserType, StoreType

from ..models import User, Store, Turn
from django.contrib.auth import get_user_model

from django.contrib.gis.geos import Point


class Query(graphene.ObjectType):
    user = graphene.Field(UserType)
    store = graphene.Field(StoreType)

    def resolve_user(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in! ')
        return User.objects.get(user=info.context.user)

    def resolve_store(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in! ')
        return Store.objects.get(user=info.context.user)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = get_user_model()(
            username=username,
        )
        user.set_password(password)
        user.save()
        user_model = User(user=user, full_name=user.username)
        user_model.save()
        return CreateUser(user=user_model)


class Weekdays(graphene.Enum):
    MO = "Mo"
    TU = "Tu"
    WE = "We"
    TH = "Th"
    FR = "Fr"
    SA = "Sa"
    SU = "Su"


class CreateStore(graphene.Mutation):
    store = graphene.Field(StoreType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        latitude = graphene.Float(required=True)
        longitude = graphene.Float(required=True)
        opening_time = graphene.DateTime(required=True)
        closing_time = graphene.DateTime(required=True)
        opening_days = graphene.Argument(graphene.List(Weekdays))

    def mutate(self, info, username, password, latitude, longitude, opening_time, closing_time, opening_days):
        user = get_user_model()(
            username=username,
        )
        user.set_password(password)
        store = Store(user=user, name=username,
                      # X = lng, Y = lat
                      location=Point(latitude, longitude, srid=4326),
                      opening_time=opening_time, closing_time=closing_time, opening_days=opening_days)
        user.save()
        store.save()
        return CreateStore(store=store)


class ModifyStore(graphene.Mutation):
    store = graphene.Field(StoreType)

    class Arguments:
        new_name = graphene.String()

    def mutate(self, info, new_name):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in!')

        store = Store.objects.get(user=info.context.user)

        if new_name:
            store.name = new_name
            store.save()
            auth_user = info.context.user
            auth_user.username = new_name
            auth_user.save()
            return ModifyStore(store=store)


class ModifyUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        new_name = graphene.String()

    def mutate(self, info, new_name):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in!')

        auth_user = info.context.user

        if new_name:
            auth_user.username = new_name
            auth_user.save()
            user = User.objects.get(user=auth_user)
            user.full_name = new_name
            user.save()
            return ModifyUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_store = CreateStore.Field()
    modify_store = ModifyStore.Field()
    modify_user = ModifyUser.Field()
