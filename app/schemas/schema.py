import graphene
from graphql import GraphQLError

from django.db.models import Q
from django.contrib.auth.models import User
from ..models import User, Store, Turn

import graphql_jwt
import datetime

from . import auth
from .types import StoreType, UserType, TurnType, AuthUserType


class Query(auth.Query, graphene.ObjectType):
    all_stores = graphene.List(StoreType)
    search_store = graphene.Field(
        auth.StoreType, name=graphene.String(required=True))
    get_turns_for_user = graphene.List(TurnType)
    store_turns = graphene.List(
        TurnType, completed=graphene.Boolean(required=True))

    def resolve_all_stores(self, info):
        return Store.objects.all()

    def resolve_search_store(self, info, name):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in! ')
        store = Store.objects.get(name=name)
        if store.opening_time < datetime.datetime.now().time() and store.closing_time > datetime.datetime.now().time():
            store.is_open = True
        else:
            store.is_open = False
        return store

    def resolve_get_turns_for_user(self, info):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in! ')
        current_user = User.objects.get(user=info.context.user)
        return Turn.objects.filter(fullfilled_successfully=False, user_did_not_present=False, canceled=False, user=current_user)

    def resolve_store_turns(self, info, completed):
        if info.context.user.is_anonymous:
            raise GraphQLError('Not logged in! ')
        store = Store.objects.get(user=info.context.user)
        if completed:
            return Turn.objects.filter(Q(fullfilled_successfully=True) |
                                       Q(user_did_not_present=True) |
                                       Q(canceled=True), store=store).order_by('-completion_time')
        else:
            return Turn.objects.filter(
                fullfilled_successfully=False, user_did_not_present=False, canceled=False, store=store)


class CreateTurn(graphene.Mutation):
    turn = graphene.Field(TurnType)

    class Arguments:
        store_name = graphene.String(required=True)

    def mutate(self, info, store_name):
        store = Store.objects.get(name=store_name)
        user = User.objects.get(user=info.context.user)
        # Selecting the user MODEL (not Django's)
        turn = Turn(user=user, store=store)
        turn.save()
        return CreateTurn(turn=turn)


class CompleteTurnSuccessfully(graphene.Mutation):
    turn = graphene.Field(TurnType)

    class Arguments:
        turn_id = graphene.ID(required=True)

    def mutate(self, info, turn_id):
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
