import graphene
from graphene_file_upload.scalars import Upload


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    product_img = Upload()
    type = graphene.String(required=True)
    price = graphene.Float(required=True)
    active = graphene.Boolean(required=True)
    time_to_prepare = graphene.String(required=True)



class CategoryInput(graphene.InputObjectType):
    type_name = graphene.String()
    type_icon = Upload()
    in_used = graphene.String()
    parent_id = graphene.ID()


class ModifierInput(graphene.InputObjectType):
    id = graphene.ID()
    modifier_title= graphene.String()
    type_id = graphene.Int()
    quantity_limit = graphene.Int()
    active = graphene.Boolean(required=True)
    obligatory = graphene.Boolean(required=True)
    items_has_price = graphene.Boolean(required=True)

class ModifierItemInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    modification_price = graphene.Int(required=True)


