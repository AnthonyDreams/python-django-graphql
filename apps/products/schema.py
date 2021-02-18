import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from graphene_permissions.permissions import AllowAuthenticated
from .models import Type, Product, Modifier,ModificationItems, Category
from graphene import Connection, ConnectionField, Node, Int
from graphene_permissions.mixins import AuthNode
from django_filters import FilterSet, OrderingFilter
from graphene_django.filter import DjangoFilterConnectionField
from .schema_inputs import ProductInput, CategoryInput, ModifierInput, ModifierItemInput
from ..stores.models import Store
from ..stores.schema import StoreType
from graphene_file_upload.scalars import Upload
from resizeimage import resizeimage
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from itertools import groupby
from apps.address.models import StoreLocations

User = get_user_model()

def Files(model, files):
    if files:
        
        file_ = files
        image_obj = Image.open(file_)
        # resize image
        # image_obj = resizeimage.resize_width(image_obj, 800)

        new_image_io = BytesIO()
        image_obj.save(new_image_io, image_obj.format)

        
        temp_name = file_.name
        
        model.product_img.save(
            temp_name,
            content=ContentFile(new_image_io.getvalue())
        )
    
        model.save()

    return True


class CustomNode(Node):
    class Meta:
        name = 'Node_'

    @staticmethod
    def to_global_id(type, id):
        return id

    @staticmethod
    def get_node_from_global_id(id, context, info, only_type=None):
        return info.return_type.graphene_type._meta.model.objects.get(id=id)

class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = Int()
    count = Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_count(root, info):
        return len(root.edges)


class ProductType(DjangoObjectType):
    str_weight = graphene.String()
    time_to_prepare = graphene.String()
    price = graphene.String()
    class Meta:
        model = Product
        interfaces = (Node, )
        connection_class = ExtendedConnection
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'type': ['exact']
        }
class ModificationItemsType(DjangoObjectType):
    modification_price = graphene.String()
    class Meta:
        model = ModificationItems



class ModifierType(DjangoObjectType):
    get_type = graphene.String()

    class Meta:
        model = Modifier
        interfaces = (CustomNode, )
        connection_class = ExtendedConnection
        filter_fields = {
        'modifier_title': ['exact', 'icontains', 'istartswith'],
        }

class FoodType(DjangoObjectType):
    total_products = graphene.Int()
    url = graphene.String()
    in_used_by_store = graphene.Boolean()
    class Meta:
        model = Type


class CategoryType(DjangoObjectType):

    class Meta:
        model = Category

class ProductByCategoryType(graphene.ObjectType):
    type_name = graphene.String()
    products = graphene.List(ProductType)

class Query(graphene.ObjectType):
    food_type = graphene.List(FoodType, search_by_name=graphene.String(required=False), category_id=graphene.String())
    get_products = DjangoFilterConnectionField(ProductType, category=graphene.String(), store_id=graphene.Int(), price=graphene.String())
    products_group_by_category = graphene.List(ProductByCategoryType, store_id=graphene.Int())
    get_modifiers = DjangoFilterConnectionField(ModifierType, store_id=graphene.Int(), id__in=graphene.List(graphene.ID, required=False))
    get_modifiers_by_product = graphene.List(ModifierType, product_id=graphene.String())
    get_categories = graphene.List(CategoryType, store_id=graphene.Int())
    get_allow_categories = graphene.List(CategoryType, store_id=graphene.Int())

    def resolve_food_type(self, info, **kwargs):
        type = Type.objects.all().order_by('-id')
        if 'search_by_name' in kwargs:
           type = type.filter(type_name__icontains=kwargs['search_by_name']).order_by('-id')
        if 'category_id' in kwargs:
            type = type.filter(type_category__category_name=kwargs['category_id'])
        try:
            store = info.context.store_profile.store
            permits = store.categories_allowed

            if permits['allow'][0]== '*':
                type = type.exclude(type_category__category_name__in=permits['restricted']).distinct()
            else:
                type = type.filter(type_category__category_name__in=permits['allow'])
        finally:

            return type
    
    def resolve_get_categories(self, info, store_id):
        store_id_ = StoreLocations.objects.filter(id=store_id).first().store
        permits = store_id_.categories_allowed
        type_ = Type.objects.filter(in_used=store_id_).values('id')
        category = Category.objects.filter(type_category__in=type_)
        if permits['allow'][0]== '*':
            category = category.exclude(category_name__in=permits['restricted']).distinct()
        else:
            category = category.filter(category_name__in=permits['allow'])

        return category

    def resolve_get_allow_categories(self, info, store_id):
        store_id_ = StoreLocations.objects.filter(id=store_id).first().store
        permits = Store.objects.get(id=store_id_.id).categories_allowed
        category = []
        if permits['allow'][0] == '*':
            category = Category.objects.exclude(category_name__in=permits['restricted']).distinct()
        else:
            category = Category.objects.filter(category_name__in=permits['allow'])

        return category


    def resolve_get_products(self, info, store_id, **kwargs):
        store_id_ = StoreLocations.objects.filter(id=store_id).first().store
        product = Product.objects.filter(store=store_id_)
        if('price' in kwargs):
            if(kwargs['price'] == '>'):
               product = product.order_by('-price')
            elif(kwargs['price'] == '<'):
                product = product.order_by('price')
        else:
            product = product.order_by('-id')
        if('type' in kwargs and kwargs['type'].isnumeric()):
            product = product.filter(type__id=kwargs['type'])
        elif 'category' in kwargs:
            category = Category.objects.filter(category_name__iexact=kwargs['category'])
            product = product.filter(type__id__in=[type_.type_category.all().values('id') for type_ in category])


        return product

    def resolve_get_modifiers(self, info, store_id, **kwargs):
        store_id_ = StoreLocations.objects.filter(id=store_id).first().store
        modifiers = Modifier.objects.filter(store=store_id_).order_by('id')

        if 'id__in' in kwargs:
            modifiers = modifiers.filter(id__in=kwargs['id__in'])

        

        return modifiers

    
    def resolve_products_group_by_category(self, info, store_id):
        store_id_ = StoreLocations.objects.filter(id=store_id).first().store
        data = Type.objects.filter(in_used=store_id_)
        data = Product.objects.filter(type__in=data, store=store_id_).order_by('type')
        data = [{'type_name': key.type_name, 'products' : list(result)} for key, result in groupby(data, key=lambda item: item.type)]
        
        return data

    def resolve_get_modifiers_by_product(self, info, product_id):
        modifiers = Product.objects.get(slug=product_id)

        return modifiers.modifications.all()


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    class Arguments:
        product = ProductInput()
        store_id = graphene.Int()

    def mutate(self, info, product, store_id):
        store = StoreLocations.objects.filter(id=store_id).first().store
        type = Type.objects.get(id=product['type'])
        product['type'] = type
        product = Product.objects.create(store=store, **product)

        return CreateProduct(product=product)

class updateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    class Arguments:
        product = ProductInput()
        product_id = graphene.String()

    def mutate(self, info, product, product_id):
        type = Type.objects.get(id=product['type'])
        product['type'] = type
        product_ = Product.objects.filter(slug=product_id)
        if not product['product_img']:
            del product['product_img']

        product_.update(**product)
        if 'product_img' in product:
            Files(product_[0], product['product_img'])

        return updateProduct(product=product_[0])

class createCategory(graphene.Mutation):
    category = graphene.Field(FoodType)

    class Arguments:
        category = CategoryInput()
    
    def mutate(self, info, category):
        category['type_category_id'] = category.pop('parent_id', None)
        store = info.context.store_profile.store
        category = Type.objects.create(**category)
        category.in_used.add(store)

        return createCategory(category=category)

class updateCategory(graphene.Mutation):
    category = graphene.Field(FoodType)

    class Arguments:
        category = CategoryInput()
        category_id = graphene.Int(required=True)
    
    def mutate(self, info, category, category_id):
        category_ = Type.objects.filter(id=category_id)
        store = StoreLocations.objects.filter(id=category['in_used'][:-1]).first().store

        if category['in_used'][-1] == 't':
           category_[0].in_used.add(store)
        else:
            category_[0].in_used.remove(store)
        
        del category['in_used'] 
        category_.update(**category)

        return updateCategory(category=category_[0])

class setInUsed(graphene.Mutation):
    category = graphene.Field(FoodType)

    class Arguments:
        in_used = graphene.String(required=True)
        category_id = graphene.Int()
    
    def mutate(self, info, category_id, **category):
        category_ = Type.objects.get(id=category_id)
        store = info.context.store_profile.store

        if category['in_used'][-1] == 't':
            category_.in_used.add(store)
        else:
            category_.in_used.remove(store)
        
        return setInUsed(category=category_)


class createModifier(graphene.Mutation):
    modifier = graphene.Field(ModifierType)

    class Arguments:
        modifier = ModifierInput(required=True)
        store_id = graphene.Int(required=True)

    def mutate(self, info, modifier, store_id):
        store = StoreLocations.objects.filter(id=store_id).first().store
        modifier = Modifier.objects.create(**modifier, store=store)

        return createModifier(modifier=modifier)


class updateModifier(graphene.Mutation):
    modifier = graphene.Field(ModifierType)

    class Arguments:
        modifier = ModifierInput(required=True)
        modifier_id = graphene.ID()
    
    def mutate(self, info, modifier, modifier_id):
        del modifier['id']
        modifier_ = Modifier.objects.filter(id=modifier_id)
        modifier_.update(**modifier)
        
        return updateModifier(modifier=modifier_[0])

class addModifierProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        modifier_id = graphene.Int()
        product_id = graphene.String()

    def mutate(self, info, modifier_id, product_id):
        modifier = Modifier.objects.get(id=modifier_id)
        product = Product.objects.get(slug=product_id)
        modifier.products.add(product)

        return addModifierProduct(product = product)

class removeModifierProduct(graphene.Mutation):
    remove = graphene.Boolean()

    class Arguments:
        modifier_id = graphene.Int()
        product_id = graphene.String()
    
    def mutate(self, info, modifier_id, product_id):
        modifier = Modifier.objects.get(id=modifier_id)
        product = Product.objects.get(slug=product_id)
        modifier.products.remove(product)

        return removeModifierProduct(remove=True)



class addModifierExtraProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        modifier_id = graphene.Int()
        product_id = graphene.String()

    def mutate(self, info, modifier_id, product_id):
        modifier = Modifier.objects.get(id=modifier_id)
        product = Product.objects.get(slug=product_id)
        modifier.extra_products.add(product)

        return addModifierExtraProduct(product = product)

class removeModifierExtraProduct(graphene.Mutation):
    remove = graphene.Boolean()

    class Arguments:
        modifier_id = graphene.Int()
        product_id = graphene.String()
    
    def mutate(self, info, modifier_id, product_id):
        modifier = Modifier.objects.get(id=modifier_id)
        product = Product.objects.get(slug=product_id)
        modifier.extra_products.remove(product)

        return removeModifierExtraProduct(remove=True)
        

        

class addModifierItem(graphene.Mutation):
    item = graphene.Field(ModificationItemsType)

    class Arguments:
        item = ModifierItemInput(required=True)
        modifier_id = graphene.Int()

    def mutate(self, info, item, modifier_id):
        item = ModificationItems.objects.create(**item)
        modifier = Modifier.objects.get(id=modifier_id)
        modifier.modification_items.add(item)
        return addModifierItem(item= item)

class updateModifierItem(graphene.Mutation):
    item = graphene.Field(ModificationItemsType)

    class Arguments:
        item = ModifierItemInput(required=True)
        item_id = graphene.Int()

    def mutate(self, info, item, item_id):
        item_ = ModificationItems.objects.filter(id=item_id)
        item_.update(**item)
        return updateModifierItem(item= item_[0])

class deleteModifierItem(graphene.Mutation):
    deleted = graphene.Boolean()

    class Arguments:
        item_id = graphene.Int(required=True)

    def mutate(self, info, item_id):
        item = ModificationItems.objects.get(id=item_id)

        return deleteModifierItem(deleted= item.delete())



class SaveImagesProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        files = Upload()
        id = graphene.String(required=True)
   
    
    @staticmethod
    def mutate(self, info, id, files=None):
        file = info.context.FILES
        product = Store.objects.get(slug=id)
        Files(product, file)
        return SaveImagesProduct(product=product)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    save_images_product = SaveImagesProduct.Field()
    update_product = updateProduct.Field()
    create_category = createCategory.Field()
    update_category = updateCategory.Field()
    set_in_used = setInUsed.Field()
    create_modifier = createModifier.Field()
    update_modifier = updateModifier.Field()
    add_modifier_item = addModifierItem.Field()
    update_modifier_item = updateModifierItem.Field()
    delete_modifier_item = deleteModifierItem.Field()
    add_modifier_product = addModifierProduct.Field()
    remove_modifier_product = removeModifierProduct.Field()
    add_modifier_extra_product = addModifierExtraProduct.Field()
    remove_modifier_extra_product = removeModifierExtraProduct.Field()