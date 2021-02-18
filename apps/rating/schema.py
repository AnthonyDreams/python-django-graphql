import graphene
from graphene_django.types import DjangoObjectType
from .models import Rate
from django.db.models import Case, When
from .schema_type import RateInput
from apps.stores.models import Store
from graphene import Connection, ConnectionField, Node, Int
from graphene_permissions.mixins import AuthNode

class RateType(AuthNode, DjangoObjectType):
    str_created_date = graphene.String()
    is_mine = graphene.Boolean()
    class Meta:
        model = Rate

class RateTypeConnection(Connection):
    class Meta:
        node = RateType
    count = Int()

    def resolve_count(root, info):
        return len(root.edges)

class ListPointType(graphene.ObjectType):
    start_1 = graphene.Int()
    start_2 = graphene.Int()
    start_3 = graphene.Int()
    start_4 = graphene.Int()
    start_5 = graphene.Int()
    total = graphene.Int()


class Query(graphene.ObjectType):
    rates_by_store = ConnectionField(RateTypeConnection, store_id=graphene.Int(required=True))
    start_list = graphene.Field(ListPointType, store_id=graphene.Int())

    def resolve_rates_by_store(self, info, store_id, **kwargs):
        return Rate.objects.filter(store=store_id).annotate(sort_order_auth=Case(When(rater=info.context.user, then=('id')))).order_by('sort_order_auth')

    def resolve_start_list(self, info, store_id):
        rate_all = Rate.objects.filter(store=store_id).count()
        if rate_all == 0:
            rate_all = 1
        start_object = {
            'start_1': (Rate.objects.filter(store=store_id, point=1).count()/rate_all) * 100,
            'start_2': (Rate.objects.filter(store=store_id, point=2).count()/rate_all) * 100,
            'start_3': (Rate.objects.filter(store=store_id, point=3).count()/rate_all) * 100,
            'start_4': (Rate.objects.filter(store=store_id, point=4).count()/rate_all) * 100,
            'start_5': (Rate.objects.filter(store=store_id, point=5).count()/rate_all) * 100,
            'total': rate_all
            
        }
        return start_object


class addRate(graphene.Mutation):
    rate = graphene.Field(RateType)
    
    class Arguments:
        rating = RateInput(required=True)
        store_id = graphene.Int()
    
    def mutate(self, info, rating, store_id):
        rate = Rate.objects.create(**rating, rater=info.context.user, store_id=store_id)

        return addRate(rate=rate)

class editRate(graphene.Mutation):
    rate = graphene.Field(RateType)
    
    class Arguments:
        rating = RateInput(required=True)
        review_id = graphene.Int()
    
    def mutate(self, info, rating, review_id):
        rate = Rate.objects.filter(id=review_id)
        rate.update(**rating)
        return editRate(rate=rate[0])

class removeRate(graphene.Mutation):
    valid = graphene.Boolean()

    class Arguments:
        rate_id = graphene.Int()

    
    def mutate(self, info, rate_id):
        rate = Rate.objects.get(id=rate_id)

        return removeRate(valid=rate.delete())



class Mutation(graphene.ObjectType):
    add_rate = addRate.Field()
    edit_rate = editRate.Field()
    remove_rate = removeRate.Field()
    