import graphene
from graphql import GraphQLError

from django.db.models import Q
from django.contrib.auth.models import User
from ..models import User, Store, Turn

import graphql_jwt
import datetime
from datetime import date
import calendar

from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from . import auth
from .types import StoreType, UserType, TurnType, AuthUserType


def is_store_open(store):
    opening_days = str(store.opening_days).split(", ")
    today = date.today()

    return store.opening_time < datetime.datetime.now().time()\
        and store.closing_time > datetime.datetime.now().time()\
        and calendar.day_name[today.weekday()] in opening_days


def check_login(info):
    if info.context.user.is_anonymous:
        raise GraphQLError('Not logged in! ')


class Query(auth.Query, graphene.ObjectType):
    all_stores = graphene.List(StoreType)
    store_detail = graphene.Field(
        auth.StoreType, name=graphene.String(required=True))
    get_turns_for_user = graphene.List(TurnType)
    store_turns = graphene.List(
        TurnType, completed=graphene.Boolean(required=True),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    nearby_stores = graphene.List(StoreType,
                                  lat=graphene.Float(required=True),
                                  lng=graphene.Float(required=True),
                                  first=graphene.Int(),
                                  skip=graphene.Int(),
                                  )

    def resolve_all_stores(self, info):
        check_login(info)
        return Store.objects.all()

    def resolve_nearby_stores(self, info, lat, lng, first=None, skip=None):
        check_login(info)
        ref_location = Point(lat, lng, srid=4326)
        qs = Store.objects.all()
        qs = qs.filter(location__dwithin=(
            ref_location, D(km=12.5))).annotate(distance=GeometryDistance("location", ref_location)).order_by("distance")

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        return qs

    def resolve_store_detail(self, info, name):
        check_login(info)
        store = Store.objects.get(name=name)
        print(store.opening_days)
        if is_store_open(store):
            store.is_open = True
        else:
            store.is_open = False
        store.turns.set(Turn.objects.filter(fullfilled_successfully=False,
                                            user_did_not_present=False, canceled=False, store=store))

        return store

    def resolve_get_turns_for_user(self, info):
        check_login(info)
        current_user = User.objects.get(user=info.context.user)
        turns = Turn.objects.filter(
            fullfilled_successfully=False, user_did_not_present=False, canceled=False, user=current_user)
        for (index, turn) in enumerate(turns):
            store = turns[index].store
            turns[index].store.turns.set(Turn.objects.filter(
                fullfilled_successfully=False, user_did_not_present=False, canceled=False, store=store))
        return turns

    def resolve_store_turns(self, info, completed, first=None, skip=None):
        check_login(info)
        store = Store.objects.get(user=info.context.user)
        qs = Turn.objects.all()
        if completed:
            return qs.filter(Q(fullfilled_successfully=True) |
                             Q(user_did_not_present=True) |
                             Q(canceled=True), store=store).order_by('-completion_time')
        else:
            return qs.filter(
                fullfilled_successfully=False, user_did_not_present=False, canceled=False, store=store)
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        return qs


class CreateTurn(graphene.Mutation):
    turn = graphene.Field(TurnType)

    class Arguments:
        store_name = graphene.String(required=True)

    def mutate(self, info, store_name):
        check_login(info)
        store = Store.objects.get(name=store_name)
        user = User.objects.get(user=info.context.user)
        if store.turns.filter(fullfilled_successfully=False, user_did_not_present=False, canceled=False, user=user).exists():
            raise GraphQLError("User has already an active turn")
        # Selecting the user MODEL (not Django's)
        turn = Turn(user=user, store=store)
        turn.save()
        return CreateTurn(turn=turn)


class CompleteTurnSuccessfully(graphene.Mutation):
    turn = graphene.Field(TurnType)

    class Arguments:
        turn_id = graphene.ID(required=True)

    def mutate(self, info, turn_id):
        check_login(info)
        turn = Turn.objects.get(id=turn_id)
        turn.fullfilled_successfully = True
        turn.complete()
        turn.save()
        return CompleteTurnSuccessfully(turn=turn)


class CancelTurn(graphene.Mutation):
    turn = graphene.Field(TurnType)

    class Arguments:
        turn_id = graphene.ID(required=True)

    def mutate(self, info, turn_id):
        check_login(info)
        turn = Turn.objects.get(id=turn_id)
        turn.canceled = True
        turn.complete()
        turn.save()
        return CancelTurn(turn=turn)


class UserDidNotPresent(graphene.Mutation):
    turn = graphene.Field(TurnType)

    class Arguments:
        turn_id = graphene.ID(required=True)

    def mutate(self, info, turn_id):
        check_login(info)
        turn = Turn.objects.get(id=turn_id)
        turn.user_did_not_present = True
        turn.complete()
        turn.save()
        return UserDidNotPresent(turn=turn)


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(AuthUserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class Mutation(auth.Mutation, graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    create_turn = CreateTurn.Field()
    complete_turn_successfully = CompleteTurnSuccessfully.Field()
    cancel_turn = CancelTurn.Field()
    user_did_not_present = UserDidNotPresent.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
