import graphene
from graphene import Connection, ConnectionField, Node, Int
from graphene_permissions.mixins import AuthNode
from graphene_django import DjangoObjectType
from .getTrucks import getTrucksBusinessLogically
from graphene_permissions.permissions import AllowAuthenticated
from .models import Store, Horarios, HorariosType, Booking
from .schema_inputs import *
from apps.address.models import Address, StoreLocations
from apps.address.schema import AddressObjectType, StoreLocationObjectType
from apps.users.models import Preferences, StoreManagerProfile, User
from django.shortcuts import get_object_or_404
import time
from django_filters import FilterSet, OrderingFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from resizeimage import resizeimage
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Q

def Files(model, files):
    if files:
        for file in files:
            try:
                file_ = files[file]

            except:
                file = 1 if files[0] == file else 2
                file_ = files[file -1]

            try:
                image_obj = Image.open(file_)
            except:
                continue
            
            # resize image
            # image_obj = resizeimage.resize_width(image_obj, 800)

            new_image_io = BytesIO()
            image_obj.save(new_image_io, image_obj.format)

            
            temp_name = file_.name
            if int(file) == 1:
                model.profile_img.save(
                    temp_name,
                    content=ContentFile(new_image_io.getvalue())
                )
            elif int(file) == 2:
                model.cover_img.save(
                            temp_name,
                            content=ContentFile(new_image_io.getvalue())
                        )
            model.save()

        return True

class HorariosObjectType(DjangoObjectType):
    is_open = graphene.Boolean()
    class Meta:
        model= Horarios

class BookingType(DjangoObjectType):
    str_status = graphene.String()
    str_date = graphene.String()
    class Meta:
        model = Booking

class StoreType(AuthNode, DjangoObjectType):
    permission_classes = (AllowAuthenticated,)
    today_schedule = graphene.Int()
    
    get_absolute_image_url = graphene.String()
    
    class Meta:
        model = Store
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'type': ['exact']
        }

class Store_Connection(Connection):
    class Meta:
        node = StoreType
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'type': ['exact']
        }
    count = Int()

    def resolve_count(root, info):
        return len(root.edges)

class StoreLocation_Connection(Connection):
    class Meta:
        node = StoreLocationObjectType

    count = Int()

    def resolve_count(root, info):
        return len(root.edges)

class Query(graphene.ObjectType):
    stores = ConnectionField(StoreLocation_Connection, store_type=graphene.Int())
    store_detail = graphene.Field(StoreLocationObjectType, id=graphene.Int(required=True))
    store_admin = graphene.Field(StoreType)
    favorite_stores = ConnectionField(StoreLocation_Connection)
    booking_stores = graphene.List(BookingType, store_id=graphene.Int(required=True))
    mine_stores = graphene.List('apps.users.schema.StoreManagerProfileType')
    get_store_by_filter = graphene.List(StoreType, store_type=graphene.Int())
    get_all_staff_members = graphene.List('apps.users.schema.StoreManagerProfileType', store_id=graphene.Int(), searchBy=graphene.String(), role=graphene.Int())
    def resolve_stores(self, info, **kwargs):
        return getTrucksBusinessLogically.byBusinessType(kwargs['store_type'])

    def resolve_mine_stores(self, info):
        return info.context.user.stores_manager_profile.all().order_by('-id')

    def resolve_store_detail(self, info, id):
        return get_object_or_404(StoreLocations, id=id)

    def resolve_store_admin(self, info):
        return get_object_or_404(Store, id=info.context.store_profile.store.id)
    
    def resolve_favorite_stores(self, info, **kwargs):
        return Preferences.objects.get(account=info.context.user).fav_stores.all()

    def resolve_booking_stores(self, info, store_id):
        return info.context.user.reservations.filter(store=store_id).exclude(status=3)

    def resolve_get_store_by_filter(self, info, **kwargs):
        return Store.objects.filter(**kwargs)

    def resolve_get_all_staff_members(self, info, store_id, **kwargs):
        staffs = StoreManagerProfile.objects.filter(store_id=store_id)
        if 'searchBy' in kwargs:
            user = User.objects.filter(Q(first_name__icontains=kwargs['searchBy']) | Q(email__icontains=kwargs['searchBy'])).values('id')
            staffs = staffs.filter(user_id__in=user)
        
        if 'role' in kwargs:
            staffs = staffs.filter(role=kwargs['role'])
        return staffs.order_by('role')

class SaveImages(graphene.Mutation):
    store = graphene.Field(StoreType)

    class Arguments:
        files = Upload()
        id = graphene.Int(required=True)
   
    
    @staticmethod
    def mutate(self, info, id, files=None):
        file = info.context.FILES
        store = Store.objects.get(id=id)
        Files(store, file)
        return SaveImages(store=store)


class CreateStore(graphene.Mutation):
    store = graphene.Field(StoreType)
    class Arguments:
        store_data = StoreInput(required=True)
    @staticmethod    
    def mutate(self, info, store_data):
        horarios = store_data.pop('horarios', None)
        address = store_data.pop('address', None)
        address = Address.objects.create(**address['location'])
        store = Store.objects.create(**store_data,  owner=info.context.user)
        location = StoreLocations.objects.create(phone_number=address['phone_number'], location=address, store=store)
        store_manager = StoreManagerProfile.objects.create(user=info.context.user, role=1, store=store)
        for i in store_data.horarios:
            horario_type = HorariosType.objects.get(id = i.horarios_type.id)
            i['horarios_type'] = horario_type
            horarios = Horarios.objects.create(**i)
            store.horarios.add(horarios)
        
        store.save()
        
        return CreateStore(store=store)


class updateStore(graphene.Mutation):
    store = graphene.Field(StoreType)
    class Arguments:
        store_data = StoreInput(required=True)
        store_id = graphene.Int(required=True)
    @staticmethod    
    def mutate(self, info, store_data, store_id):
        store_ = Store.objects.filter(id=info.context.store_profile.store.id)
        file = [store_data['profile_img'], store_data['cover_img']]
        store_.update(**store_data)
        Files(store_[0], file)

        
        return CreateStore(store=store_[0])

class createBooking(graphene.Mutation):
    booking = graphene.Field(BookingType)
    class Arguments:
        reservation = BookingInput(required=True)
    def mutate(self, info, reservation):
        booking = Booking.objects.create(**reservation, user = info.context.user)
        return createBooking(booking=booking)

class cancelBooking(graphene.Mutation):
    valid = graphene.Boolean()

    class Arguments:
        reservation_id = graphene.Int()

    def mutate(self, info, reservation_id):
        booking = Booking.objects.get(id=reservation_id)
        if booking.status == 1:
            return cancelBooking(valid=booking.delete())
        elif booking.status == 2:
            booking.status = 3
            booking.save()
            return cancelBooking(valid=True)

class ToggleStaffMember(graphene.Mutation):
    manager = graphene.Field('apps.users.schema.StoreManagerProfileType')

    class Arguments:
        email = graphene.String(required=True)
        store = graphene.ID(required=True)
        role_id = graphene.ID(required=True)

    def mutate(self, info, email, store, role_id):
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create(email=email)
            manager = StoreManagerProfile.objects.create(user=user, store_id=store, role=role_id)
        elif not user.stores_manager_profile.filter(store_id=store).first():
            manager = StoreManagerProfile.objects.create(user=user, store_id=store, role=role_id)
        elif not user.stores_manager_profile.filter(store_id=store).first().active:
            manager = StoreManagerProfile.objects.get(id=user.stores_manager_profile.get(store_id=store).id)
            manager.active = True
            manager.save()

        else:
            manager = StoreManagerProfile.objects.get(id=user.stores_manager_profile.get(store_id=store).id)
            manager.active = False
            manager.save()

        return ToggleStaffMember(manager=user.stores_manager_profile.filter(store_id=store).first())


        



class Mutation(graphene.ObjectType):
    store_create = CreateStore.Field()
    store_update = updateStore.Field()
    save_images = SaveImages.Field()
    create_booking = createBooking.Field()
    cancel_booking = cancelBooking.Field()
    toggle_staff_member = ToggleStaffMember.Field()