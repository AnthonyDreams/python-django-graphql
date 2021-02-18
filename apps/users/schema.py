import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from .validation import UserValidation
from apps.address.schema import AddressObjectType, DeliveryInfoObjectType
from apps.address.schema_inputs import DeliveryAddressInput
from apps.address.models import *
from .models import Preferences, StoreManagerProfile
from apps.stores.schema import BookingType
User = get_user_model()


class UserType(DjangoObjectType):
    selected_address = graphene.Field(DeliveryInfoObjectType)
    class Meta:
        model = User

class PreferencesType(DjangoObjectType):
    class Meta:
        model = Preferences

class StoreManagerProfileType(DjangoObjectType):
    role_str = graphene.String()
    class Meta:
        model = StoreManagerProfile

class StoreManagerRolesType(graphene.ObjectType):
    value = graphene.ID()
    name = graphene.String()

class UserInput(graphene.InputObjectType):
    id = graphene.Int(required=True)
    email =graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    phone_number = graphene.String()
    password = graphene.String()

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    me = graphene.Field(UserType)
    my_reservations = graphene.List(BookingType)
    get_staff_roles = graphene.List(StoreManagerRolesType) 

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_user(self, info, id):
        return User.objects.get(id=id)

    def resolve_me(self, info):
        user = info.context.user

        if user.is_anonymous:
            raise Exception('Not Logged in')

        return user
    def resolve_my_reservations(self, info):
        return info.context.user.reservations.all()

    def resolve_get_staff_roles(self, info):
        return [{'value': i[0], 'name': i[1]} for i in StoreManagerProfile.ProfileType]
        


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        email =graphene.String()
        password = graphene.String()

    
    def mutate(self, info, **kwargs):
        if UserValidation.userExist(kwargs):
            raise GraphQLError('Email en uso.') 
        user = User(email=kwargs['email'])
        user.set_password(kwargs['password'])
        user.save()
        preferences = Preferences.objects.create(account=user)
        return CreateUser(user= user)

class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    class Arguments:
        user_data = UserInput(required=True)
    
    def mutate(self, info, user_data):
        user = info.context.user
      
        if user.id != int(user_data['id']):
            raise Exception('You don\'t have permitions')
        
        del user_data['id']
        user_to_edit = User.objects.filter(id=user.id)
        user_to_edit.update(**user_data)     

        
        return UpdateUser(user=user_to_edit[0])


class AddDeliveryAddress(graphene.Mutation):
    address = graphene.Field(AddressObjectType)

    class Arguments:
        delivery_address = DeliveryAddressInput(required=True)
    
    def mutate(self, info, delivery_address):
        count = DeliveryInfo.objects.filter(user=info.context.user).count()
        location = delivery_address.pop('location', None)
        if count >= 6:
            raise Exception('No puede tener más de 6 direcciones')
        address = Address.objects.create(**location)
        delivery_info = DeliveryInfo.objects.create(**delivery_address, location=address, user=info.context.user, selected=True if count == 0 else False)
        return AddDeliveryAddress(address=address)

class editDeliveryAddress(graphene.Mutation):
    address = graphene.Field(AddressObjectType)

    class Arguments:
        delivery_address = DeliveryAddressInput(required=True)

    def mutate(self, info, delivery_address):
        location = delivery_address.pop('location', None)
        address_ = Address.objects.filter(id=location['id']).update(**location)
        delivery_info = DeliveryInfo.objects.filter(id=delivery_address['id']).update(**delivery_address)

class addFavorite(graphene.Mutation):
    valid = graphene.Boolean()

    class Arguments:
        market_id = graphene.Int(required=True)

    def mutate(self, info, market_id):
        try:
            inFav = info.context.user.account_preference.first().fav_stores.filter(id=market_id)
        except AttributeError:
            Preferences.objects.create(account=info.context.user)
            inFav = info.context.user.account_preference.first().fav_stores.filter(id=market_id)            
        
        if inFav:
            raise Exception('Se encuentra en favoritos')
        else:
            info.context.user.account_preference.first().fav_stores.add(market_id)

        return addFavorite(valid=True)

class removeFavorite(graphene.Mutation):
    valid = graphene.Boolean()

    class Arguments:
        market_id = graphene.Int(required=True)

    def mutate(self, info, market_id):
        valid = info.context.user.account_preference.all()[0].fav_stores.filter(id=market_id)
        if not valid:
            raise Exception('No se ha encontrado en favoritos')
        else:
            info.context.user.account_preference.all()[0].fav_stores.remove(market_id)

        return addFavorite(valid=True)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    add_delivery_address = AddDeliveryAddress.Field()
    edit_delivery_address = editDeliveryAddress.Field()
    remove_favorite = removeFavorite.Field()
    add_favorite = addFavorite.Field()



