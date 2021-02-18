import graphene
from graphene_django import DjangoObjectType
from .models import Order, OrderItems
from .schema_inputs import OrderInput
from graphene import Connection, ConnectionField, Node, Int
from graphene_permissions.mixins import AuthNode
from django_filters import FilterSet, OrderingFilter
from graphene_django.filter import DjangoFilterConnectionField
from apps.products.schema import CustomNode
from apps.products.models import Product
import jwt
from django.db.models import Q
from django.utils import timezone
from .schema_inputs import StatusInput
from .sqs import send_sqs_message
from .notification_messages import NotificationMessages


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = Int()
    count = Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_count(root, info):
        return len(root.edges)

class OrderType(DjangoObjectType):
    user_is_current_status_aware = graphene.Boolean()
    humanize_ordered_time = graphene.String()
    humanize_updated_time = graphene.String()
    str_order_status = graphene.String()
    str_payment_type = graphene.String()
    subtotal = graphene.Int()
    str_ordered_time = graphene.String()
    class Meta:
        model = Order
        interfaces = (CustomNode, )
        connection_class = ExtendedConnection
        filter_fields = {
        'ordered_time': ['exact'],
        }

class OrderItemsType(DjangoObjectType):
    price_x_quantity = graphene.String()
    class Meta:
        model = OrderItems
    
class NotificationRoomToken(graphene.ObjectType):
    token=graphene.String()


class Query(graphene.ObjectType):
    get_orders_by_authenticated = DjangoFilterConnectionField(OrderType)
    get_order_by_seller = graphene.List(OrderType,store_id=graphene.Int(), pending=graphene.Boolean())
    get_pending_order_by_seller = graphene.List(OrderType,store_id=graphene.Int(), pending=graphene.Boolean())

    get_api_gateway_notification_token = graphene.Field(NotificationRoomToken)
    get_unfinish_order = graphene.List(OrderType, check=graphene.Boolean())
    get_my_order_by_slug = graphene.Field(OrderType, order_slug=graphene.String())
    

    def resolve_get_orders_by_authenticated(self, info, **kwargs):
        return info.context.user.my_orders.all().order_by('-ordered_time')

    
    def resolve_get_order_by_seller(self, info, store_id, **kwargs):
        order = Order.objects.filter(store=store_id)
        if 'pending' in kwargs:
            order = order.exclude(order_status__in=[7,0,1]).order_by('-updated_order')
        return order

    def resolve_get_pending_order_by_seller(self, info, store_id, **kwargs):
        order = Order.objects.filter(store=store_id).exclude(order_status__in=[7,0,1]).order_by('-id')

        return order

    def resolve_get_api_gateway_notification_token(self, info):
        user = info.context.user
        formation = {"user_id":user.email, "identifiers_id": ""}
        if user.stores_manager_profile.all().count() > 0:
            print(user.stores_manager_profile.first().store.id)
            formation["identifiers_id"] = user.stores_manager_profile.first().store.id
            formation["user_role"] = "1"
        else:
            try:
                formation["identifiers_id"] = user.my_orders.exclude(order_status__in=[7,0,1])[0].slug
            except:
                return None
            formation["user_role"] = "2"

        

        return {"token":jwt.encode(formation, "", algorithm="HS256").decode("utf-8")}

    def resolve_get_unfinish_order(self, info, **kwargs):
        orders = info.context.user.my_orders.exclude(order_status__in=[7,0,1]).order_by('-updated_order')
        if kwargs['check']:
            orders.update(client_checked_status=timezone.now())
        return orders

    def resolve_get_my_order_by_slug(self, info, order_slug):
        order = info.context.user.my_orders.get(slug=order_slug)

        return order
        





class createOrder(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        order = OrderInput(required=True)
    def mutate(self, info, order):
        order_item = order.pop("order_items", None)  
        order_ = Order.objects.create(**order, buyer=info.context.user)
        
        for item in order_item:
            modifications = item.pop("modification_items", None)
            item['product_id'] = Product.objects.get(slug=item['product_id']).id
            
            if item['parent_id']:
                parent = Product.objects.get(slug=item['parent_id'])
                item['parent_id'] = OrderItems.objects.filter(order=order_, product_id=parent).first()
            
            order_item = OrderItems.objects.create(**item, order=order_)
            order_item.modifications.add(*[modification['modification_item_id'] for modification in modifications])

        return createOrder(order=order_)

class updateOrderStatus(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        order_status = graphene.Int()
        order_id = graphene.ID()

    def mutate(self, info, order_status, order_id):
        order = Order.objects.filter(slug=order_id)
        message = ""
        if(order_status == 3 and order[0].store.store.store_type == 1):
            order_status = 4
        order.update(order_status=order_status, updated_order=timezone.now())
        if order_status in [3,4]:
            message = NotificationMessages.order_aceptada(order.first()) 
        elif order_status == 5:
            message = NotificationMessages.order_to_deliver(order.first())
        elif order_status == 6:
            message = NotificationMessages.order_on_delivery(order.first())
        elif order_status == 7:
            message = NotificationMessages.order_completed(order.first())
        elif order_status == 0:
            message = NotificationMessages.order_cancel_by_client(order.first())
        elif order_status == 1:
            message = NotificationMessages.order_cancel_by_store(order.first())


        send_sqs_message(message)

        return Order.objects.filter(slug=order_id)
        
        
    


class Mutation(graphene.ObjectType):
    create_order = createOrder.Field()
    update_order_status = updateOrderStatus.Field()