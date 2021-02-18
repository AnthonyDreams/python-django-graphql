import graphene

class Geo(graphene.InputObjectType):
    lat = graphene.Float()
    lng = graphene.Float()

class AddressInput(graphene.InputObjectType):
    id = graphene.Int()
    city = graphene.String()
    street_line1 = graphene.String()
    street_line2 = graphene.String()
    locality = graphene.String()
    state = graphene.String()
    geo = graphene.Field(Geo)

class DeliveryAddressInput(graphene.InputObjectType):
    id = graphene.Int()
    type = graphene.Int()
    alias = graphene.String()
    selected = graphene.Boolean()
    phone_number = graphene.String()
    location = graphene.Field(AddressInput)
    delivery_instruction = graphene.String()
    user_address_text = graphene.String()




class StoreLocationsInput(graphene.InputObjectType):
    phone_number = graphene.String()
    store_id = graphene.ID()
    active = graphene.Boolean()
    location = graphene.Field(AddressInput)
