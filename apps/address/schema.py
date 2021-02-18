from .models import Address, DeliveryInfo, StoreLocations
import graphene
from graphene_django import DjangoObjectType
from .schema_inputs import StoreLocationsInput
from django.db.models import Q



class AddressObjectType(DjangoObjectType):
    address_string = graphene.String()
    class Meta:
        model = Address

class DeliveryInfoObjectType(DjangoObjectType):
    class Meta:
        model = DeliveryInfo

class StoreLocationObjectType(DjangoObjectType):
    get_name_with_location = graphene.String()
    is_fav = graphene.Boolean()
    has_rated = graphene.Boolean()
    rate = graphene.Float()
    all_rate = graphene.Int()

    class Meta:
        model = StoreLocations

class Query(graphene.ObjectType):
    me_delivery_info = graphene.List(DeliveryInfoObjectType)
    store_ubications = graphene.List(StoreLocationObjectType, store_id=graphene.ID(required=True), searchBy=graphene.String())

    def resolve_me_delivery_info(self, info):
        return DeliveryInfo.objects.filter(user=info.context.user).order_by('-selected', 'id')
    
    def resolve_store_ubications(self, info, store_id, **kwargs):
        store_id = StoreLocations.objects.filter(id=store_id).first().store
        store_ubications = StoreLocations.objects.filter(store=store_id)

        if('searchBy' in kwargs):
            store_ubications_ = store_ubications.filter(phone_number__icontains=kwargs['searchBy'])
            if not store_ubications_.exists() and not kwargs['searchBy'].isnumeric():
                address = Address.objects.filter(
                    Q(street_line1__icontains=kwargs['searchBy']) |
                     Q(street_line2__icontains=kwargs['searchBy']) |
                      Q(city__icontains=kwargs['searchBy']) |
                      Q(locality__icontains=kwargs['searchBy'])).values('id')

                store_ubications_ = store_ubications.filter(location__in=address)
            store_ubications = store_ubications_

        return store_ubications


class addStoreUbication(graphene.Mutation):
    ubication = graphene.Field(StoreLocationObjectType)

    class Arguments:
        store_ubication = StoreLocationsInput()

    def mutate(self, info, store_ubication):
        staff = info.context.user.stores_manager_profile.filter(store=store_ubication['store_id']).first()
        if(staff.role in [1,4]):
            address = store_ubication.pop('location', None)
            address = Address.objects.create(**address)
            store_ubication['store_id'] = StoreLocations.objects.filter(id=store_ubication['store_id']).first().store.id
            location = StoreLocations.objects.create(**store_ubication, location=address)
            staff.id = None
            staff.store = location
            staff.save()
            return addStoreUbication(ubication=location)
        else:
            raise Exception('You don\'t have permitions')


class updateStoreUbication(graphene.Mutation):
    ubication = graphene.Field(StoreLocationObjectType)

    class Arguments:
        store_ubication = StoreLocationsInput()
        ubication_id = graphene.ID(required=True)

    def mutate(self, info, store_ubication, ubication_id):
        if(info.context.user.stores_manager_profile.filter(store=store_ubication['store_id']).first().role in [1,4]):
            address = store_ubication.pop('location', None)
            location = StoreLocations.objects.filter(id=ubication_id)

            if(address):

                address = Address.objects.filter(id=location.first().location.id).update(**address)
                       
            del store_ubication['store_id']
            location.update(**store_ubication)
            return updateStoreUbication(ubication=location.first())

        else:
            raise Exception('You don\'t have permitions')



class selectDeliveryAddress(graphene.Mutation):
    delivery_address = graphene.Field(DeliveryInfoObjectType)

    class Arguments:
        delivery_address_id = graphene.Int(required=True)

    def mutate(self, info, delivery_address_id):
        try:
            before_selected = DeliveryInfo.objects.get(user=info.context.user, selected=True)
            before_selected.selected = False
            before_selected.save() 
        except:
            pass

        finally:
            delivery_address = DeliveryInfo.objects.get(id=delivery_address_id)
            delivery_address.selected = True
            delivery_address.save()

        return selectDeliveryAddress(delivery_address=delivery_address)

class deleteDeliveryAddress(graphene.Mutation):
    done = graphene.Boolean()

    class Arguments:
       delivery_address_id = graphene.Int(required=True) 

    def mutate(self, info, delivery_address_id):
        delivery_address = DeliveryInfo.objects.get(id=delivery_address_id, user = info.context.user)
        return deleteDeliveryAddress(done=delivery_address.delete())

class Mutation(graphene.ObjectType):
    select_delivery_address = selectDeliveryAddress.Field()
    delete_delivery_address = deleteDeliveryAddress.Field()
    add_store_ubication = addStoreUbication.Field()
    update_store_ubication = updateStoreUbication.Field()