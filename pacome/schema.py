import graphene
import graphql_jwt

from apps.users.schema import (Query as UserQuery, Mutation as UserMutation)
from apps.products.schema import (Query as ProductQuery, Mutation as ProductMutation)
from apps.stores.schema import (Query as StoresQuery, Mutation as StoreMutation)
from apps.address.schema import (Query as MeAddressQuery, Mutation as AddressMutation)
from apps.rating.schema import (Query as RateQuery, Mutation as RateMutation)
from apps.order.schema import (Query as OrderQuery, Mutation as OrderMutation)
from apps.Billing.schema import (Query as BillingQuery, Mutations as BillingMutation)
from apps.users.schema import UserType


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)

class Query(RateQuery, BillingQuery, UserQuery,ProductQuery,OrderQuery, StoresQuery,MeAddressQuery, graphene.ObjectType):
    pass

class Mutation(RateMutation, BillingMutation, UserMutation, ProductMutation, OrderMutation, StoreMutation,AddressMutation, graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)