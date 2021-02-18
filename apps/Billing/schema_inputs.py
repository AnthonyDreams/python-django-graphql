import graphene




    
class billingAddressInput(graphene.InputObjectType):
    street_address =graphene.String()
    locality = graphene.String()





class cardsInput(graphene.InputObjectType):
    number = graphene.String()
    cardholder_name = graphene.String()
    expiration_month = graphene.String()
    expiration_year = graphene.String()
    expiration_date = graphene.String()
    cvv = graphene.String()
    billing_address = graphene.Field(billingAddressInput)


class cardHolder(graphene.InputObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    


class Billing(graphene.InputObjectType):
    card_holder = graphene.Field(cardHolder)
    card = graphene.Field(cardsInput)