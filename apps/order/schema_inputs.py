import graphene

class ModificationsItemsOrderInput(graphene.InputObjectType):
    modification_id = graphene.ID()
    modification_item_id = graphene.ID()

class OrderItemsInput(graphene.InputObjectType):
    product_id = graphene.ID()
    modification_items = graphene.List(ModificationsItemsOrderInput)
    price = graphene.Int()
    quantity = graphene.Int()
    parent_id = graphene.ID()

class OrderInput(graphene.InputObjectType):
    store_id = graphene.ID()
    comment = graphene.String()
    coupons_id = graphene.ID()
    deliver_to = graphene.JSONString(required=True)
    order_items = graphene.List(OrderItemsInput)


class StatusInput(graphene.InputObjectType):
    status = graphene.ID() 