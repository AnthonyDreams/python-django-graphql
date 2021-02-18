from libs.braintreesdk.vault import BrainTreeVault
import graphene
from graphene_django import DjangoObjectType
from .models import *
from .schema_inputs import *

class BillingProfileObjectType(DjangoObjectType):
    class Meta:
        model = BillingProfile


class CardsObjectType(DjangoObjectType):
    class Meta:
        model = Cards


class Query(graphene.ObjectType):
    get_cards = graphene.List(CardsObjectType)

    def resolve_get_cards(self, info):
        cards = info.context.user.billing_profile.cards.all()

        return cards



class addCard(graphene.Mutation):
    card = graphene.Field(CardsObjectType)
    class Arguments:
        billing = Billing(required=True)

    def mutate(self, info, billing):
        card_ = billing.pop('card', None)
        customer_ = billing.pop('card_holder', None)

        try:
            billing_profile = info.context.user.billing_profile
        except BillingProfile.DoesNotExist:
            billing_profile = BillingProfile.objects.create(user=info.context.user)
   
        customer_info = Cards.objects.filter(card_holder_name__contains=f"{customer_.first_name} {customer_.last_name}")
        
        if not customer_info.exists():
            customer_info = BrainTreeVault.addCustomerBillingInfo(customer_).customer
        else:
            customer_info =  customer_info.first().braintree_customer()
       
        billing_card = BrainTreeVault.addCustomerCard(customer_info.id, card_)

        if billing_card.credit_card.token:
            card = Cards.objects.create(card_holder_name=f"{customer_.first_name} {customer_.last_name}", customer_id=billing_card.credit_card.customer_id, last_four=billing_card.credit_card.last_4, card_type=billing_card.credit_card.card_type,billing_profile=billing_profile, braintree_token=billing_card.credit_card.token)  
        else:
            raise billing_card
        return addCard(card=card)



class Mutations(graphene.ObjectType):
    add_card = addCard.Field()