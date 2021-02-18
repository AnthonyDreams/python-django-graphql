import graphene
from graphene_file_upload.scalars import Upload
from apps.address.schema_inputs import AddressInput

class Dictionary(graphene.InputObjectType):
    name = graphene.String()
    id = graphene.Int()

class HorariosTypeInput(graphene.InputObjectType):
    id = graphene.Int(required=False)

class HorariosInput(graphene.InputObjectType):
    day_start = graphene.String()
    day_end = graphene.String()
    description = graphene.String()
    days = graphene.List(Dictionary)
    horarios_type = graphene.Field(HorariosTypeInput)

class StoreInput(graphene.InputObjectType):
    cover_img = Upload()
    profile_img = Upload()
    name = graphene.String(required=True)
    about = graphene.String(required=True)
    horarios = graphene.List(HorariosInput)
    address = graphene.Field(AddressInput)
    active = graphene.Boolean()


class BookingInput(graphene.InputObjectType):
    sits_amount = graphene.Int()
    store_id = graphene.Int()
    date = graphene.String()







