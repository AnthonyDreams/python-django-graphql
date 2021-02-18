from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)

from apps.users.middleware import get_current_authenticated_store

import datetime
# Create your models here.

class PublicProductManager(models.Manager):

    def get_queryset(self):
        """
        this will return all the public products for independent seller and stores
            """
        return super().get_queryset().filter(store__store_type=4)
    
    def create_public_product(self, product, sells_by=False):
        """
        public_general_unique_store
        in the product parameter is always pass the public_general_unique_store as the store field 
        and the store who added the product if it aint domi itself will be pass as sells_by
        ex: if jumbo adds a rice product that they sell and it aint a jumbo private product this
        function is executed, because it will add jumbo as a seller but the product will be added
        to domi public_general_unique store as a not active product waiting for aproval
        """
        product = self.model(**product)
        product.active = False
        product.save(using=self._db)
        if sells_by:
            sells_by = StoreUbicationStock.objects.create(product=product, is_public=1)
            sells_by.stock_of.add(**sells_by)

        return product


class Product(models.Model):
    WEIGHT_CHOICES = (
        (1, 'LIVIANO'),
        (2, 'NORMAL'),
        (3, 'PESADO'),

    )

    name = models.CharField(max_length=250)
    description = models.TextField(null=True)
    product_img = models.ImageField(upload_to='product_img', null=True)
    type = models.ForeignKey('Type', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.PositiveSmallIntegerField(default=1, choices=WEIGHT_CHOICES)
    time_to_prepare = models.DurationField(null=True)
    active = models.BooleanField(default=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True)
    sell_as_product = models.BooleanField(default=True)
    sell_as_extra = models.BooleanField(default=False)
    objects = models.Manager()
    public = PublicProductManager()



    @property
    def str_weight(self):
        weight = dict(self.WEIGHT_CHOICES)
        return str(weight[self.weight])
    def __str__(self):
        return self.name

def pre_save_product(sender, instance, **kwargs):
    if not isinstance(instance.time_to_prepare, datetime.timedelta):
        instance.time_to_prepare = str(datetime.timedelta(minutes=int(instance.time_to_prepare)))

    instance.slug = slugify("{} {}".format(instance.name, instance.store.id))

    
pre_save.connect(pre_save_product, sender=Product)


class StoreUbicationStock(models.Model):
    PUORPRI = (
        (0, 'private'),
        (1, 'public')

    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="who_sells_me")
    in_stock = models.PositiveIntegerField()
    is_public = models.BooleanField(choices=PUORPRI, default=0)
    stock_of =  models.ManyToManyField('address.StoreLocations', related_name="in_stock_products")

# class PublicProductsSellsBy(models.Model):
#     """

#         This model is just for products added by domi itself and not by private afiliated stores. 
#         Those products are not sell by domi, so we need to know all the private stores that sells 
#         those generic/public products
        
#             """
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="who_sells_me")
#     sells_by = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="public_products")
#     has_in_stock = models.ManyToManyField('address.StoreLocations', related_name="in_stock_public_products")
    

class Category(models.Model):
    category_icon = models.ImageField(upload_to='category_icon/', max_length=100, null=True)
    category_name = models.CharField(max_length=150)

    def __str__(self):
        return self.category_name

    

class Type(models.Model):
    type_icon = models.ImageField(upload_to='type_icon/', max_length=100, null=True)
    type_name = models.CharField(max_length=250, unique=True)
    global_type = models.BooleanField(default=False)
    in_used = models.ManyToManyField('stores.Store', blank=True)
    type_category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1, related_name='type_category')


    def __str__(self):
        return self.type_name

    @property
    def in_used_by_store(self):
        store_profile = get_current_authenticated_store()
        if(store_profile):
            return self.in_used.filter(id=store_profile.store.id).exists()
        return False
        
    
    @property
    def total_products(self):
        return self.product_set.all().count()


class ModificationItems(models.Model):
    name = models.CharField(max_length=150)
    modification_price = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)



class Modifier(models.Model):
    # ExtrasComplementsAndVariations for products
    MODIFIER_TYPES = (
        (1, "Extras or Complements"),
        (2, "Product Variations"),
    )

    modifier_title = models.CharField(max_length=250)
    type_id =  models.PositiveSmallIntegerField(choices=MODIFIER_TYPES, default=1)
    obligatory = models.BooleanField(default=False)
    items_has_price = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    products = models.ManyToManyField(Product, related_name="modifications", blank=True)
    extra_products = models.ManyToManyField(Product, related_name="extras", blank=True)
    modification_items = models.ManyToManyField(ModificationItems, blank=True)
    quantity_limit = models.PositiveSmallIntegerField(default=5)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    @property
    def get_type(self):
        modifier = dict(self.MODIFIER_TYPES)
        return str(modifier[self.type_id])



    @property
    def items_total(self):
        if self.type_id == 2:
            return self.modification_items.all().count()

        return self.products.all().count()

    @property
    def modifications(self):
        return self.products