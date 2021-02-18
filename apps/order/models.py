from django.db import models
from apps.stores.models import Store
from apps.users.models import User
from apps.address.models import Address
from apps.shoppingCart.models import ShoppingCarts
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_save
import random
import string
from django.contrib.humanize.templatetags import humanize
from django.db.models import Sum
from .dynamodb import create_in_dynamodb
from django.utils import timezone
from .sqs import send_sqs_message
from decimal import Decimal
from .notification_messages import NotificationMessages
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)
# Create your models here.

class Order(models.Model):
    NOTPAID = 0
    PAID = 1
    PARTPAID = 2

    PAYMENT_STATUS = (
    (NOTPAID, 'Not Paid'),
    (PARTPAID, 'Partial Paid'),
    (PAID, 'Paid'),
    )

    ORDER_STATUS = (
        (0, 'cancelada_cliente'),
        (1, 'cancelada_staff'),
        (2, 'pendiente'),
        (3, 'aceptada'),
        (4, 'preparando'),
        (5, 'to deliver'),
        (6, 'on delivery'),
        (7, 'completada'),


    )

    PAYMENT_TYPE =(
        (0, 'pagar en la puerta'),
        (1, 'pago electronico')
    )

    order_code = models.CharField(max_length=10)
    store = models.ForeignKey('address.StoreLocations', on_delete=models.SET_NULL, null=True, related_name="orders")
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="my_orders")
    deliver_to = JSONField()
    comment = models.CharField(max_length=250, null=True, blank=True)
    payment_status = models.IntegerField(default=NOTPAID, choices=PAYMENT_STATUS, null=False)
    client_checked_status = models.DateTimeField(default=timezone.now)
    
    ordered_time = models.DateTimeField(auto_now_add=True)
    updated_order = models.DateTimeField(auto_now=True)
    order_status = models.PositiveSmallIntegerField(default=2, choices=ORDER_STATUS, null=False)
    payment_type = models.PositiveSmallIntegerField(default=1, choices=PAYMENT_TYPE, null=False)
    
    coupons = models.ForeignKey('promotions.Coupons', on_delete=models.CASCADE, blank=True, null=True)


    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug
    @property
    def user_is_current_status_aware(self):
        if get_current_authenticated_user().stores_manager_profile.filter(store=self.store).exists():
            staff = get_current_authenticated_user().stores_manager_profile.filter(store=self.store).first()
            return staff.checked_notifications >= self.updated_order
        else:
            return self.client_checked_status >= self.updated_order

    @property
    def humanize_ordered_time(self):
        return humanize.naturaltime(self.ordered_time).replace(" ago", "")
    
    @property
    def humanize_updated_time(self):
        return humanize.naturaltime(self.updated_order).replace(" ago", "")

    @property
    def str_order_status(self):
        order = dict(self.ORDER_STATUS)
        return str(order[self.order_status])
    @property
    def str_payment_type(self):
        type_ = dict(self.PAYMENT_TYPE)
        return str(type_[self.payment_type])

    @property
    def str_ordered_time(self):
        return self.ordered_time.strftime('%I:%M%p %d %b')

    @property
    def subtotal(self):
        items = self.orderitems.all()
        subtotal_sum = 0
        for item in items:
            suma  = Decimal(item.modifications.aggregate(Sum('modification_price'))['modification_price__sum'] or 0.00)
            item_total = item.price_x_quantity + suma
            subtotal_sum += item_total


        return subtotal_sum




def pre_save_order(instance, sender, **kwargs):
    code = ''.join(random.choice(string.digits) for i in range(10))
    if not Order.objects.filter(order_code=code).exists() and not instance.order_code:
        instance.order_code = code
        instance.slug = f"{code}-{instance.store.store.name}"
    
    connection_data = {"user_id": instance.buyer.email, "identifiers_id": [instance.slug], "user_info":{"user_role": "2"}}
    create_in_dynamodb(connection_data, "AuthTableStag")
    send_sqs_message(NotificationMessages.order_creation(instance))

    

pre_save.connect(pre_save_order, sender=Order)


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT,
                                related_name='orderitems', null=True)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, null=True)
    parent_id = models.ForeignKey('self', on_delete=models.PROTECT, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.IntegerField(default=1, null=False)
    modifications = models.ManyToManyField('products.ModificationItems', blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} {self.order.slug}"

    @property
    def price_x_quantity(self):
        return self.product.price * self.quantity