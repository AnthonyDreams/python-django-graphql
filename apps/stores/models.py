from django.db import models
from apps.products.models import Product
from apps.address.models import Address
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField, JSONField
User = settings.AUTH_USER_MODEL
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)
import json
from django.db.models.signals import pre_save
import datetime
from django.db.models import Sum
from django.template.defaultfilters import date as _date

# Create your models here.
class Booking(models.Model):
    STATUS_CHOICES = (
            (1, ('Pendiente de aceptar')),
            (2, ('Aceptada')),
            (3, ('Cancelada'))
        )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    store = models.ForeignKey('address.StoreLocations', on_delete=models.CASCADE, related_name="bookers")
    date = models.DateTimeField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    sits_amount = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return f"{self.user.first_name} {self.store.store.name}" 
    @property
    def str_status(self):
        status = dict(self.STATUS_CHOICES)
        return str(status[self.status])
    
    @property
    def str_date(self):
        return _date(self.date, "d b, l h:i a")  # self.date.strftime("%B %d, %Y, %I:%M %p")

def pre_save_booking(sender, instance, **kwargs):
    datetime_ = instance.date

        
    if not isinstance(datetime_, datetime.datetime):
        date_time_obj = timezone.datetime.strptime(datetime_, '%Y-%m-%d %H:%M')
        instance.date = date_time_obj

    
pre_save.connect(pre_save_booking, sender=Booking)


class HorariosType(models.Model):
    WEEK = 1
    WEEKEND = 2
    SPECIAL = 3
    TYPE_CHOICES = (
        (WEEK, 'week'),
        (WEEKEND, 'weekend'),
        (SPECIAL, 'special'),

    )

    id = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, primary_key=True)

    def __str__(self):
        type = dict(self.TYPE_CHOICES)
        return type[self.id]

class Horarios(models.Model):
    day_start = models.TimeField()
    day_end = models.TimeField()
    description = models.TextField(null=True, blank=True)
    horarios_type = models.ForeignKey(HorariosType, on_delete=models.CASCADE, null=True)
    days = JSONField(null=True)
    
    @property
    def is_open(self):
        now = timezone.localtime(timezone.now()).time()
        return now > self.day_start and now < self.day_end

    def __str__(self):
        return str(self.horarios_type)

        
class Store(models.Model):
    STORE_TYPE_CHOICES = (
    (1, ('Comida')),
    (2, ('mercados')),
    (3, ('salud')),
    (4, ('public_general_unique_store'))
    )
    cover_img = models.ImageField(upload_to='images/')
    profile_img = models.ImageField(upload_to='images/')
    name = models.CharField(max_length=250)
    about = models.CharField(max_length=800, null=True, blank=True)
    horarios = models.ManyToManyField(Horarios,  related_name='store_horarios', blank=True)
    active = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=True, related_name='store_owner')
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='store_staff')
    store_type = models.PositiveSmallIntegerField(default=1, choices=STORE_TYPE_CHOICES)

    def __str__(self):
        return self.name

    @property
    def today_schedule(self):
        day_of_week = timezone.localtime(timezone.now()).isocalendar()[2]
        week = 1
        if day_of_week > 5:
            week = 2

        this_week_schedule = self.horarios.all().filter(horarios_type_id=week)
        horario = None
        for i in this_week_schedule:
            
            for a in i.days:
                a = json.loads(a.replace("'", '"'))
                if a['id']== day_of_week:
                    horario = i
        
        return horario.is_open


    @property
    def get_absolute_image_url(self):
        return "{0}{1}".format(settings.MEDIA_URL, self.image.url)

    


    @property
    def type_in_used(self):
        return self.type_set.all()
    
    @property
    def categories_allowed(self):
        permits = {
            'restaurantes': {
                'restricted': ['*'],
                'allow' : ['Platos']
            }, 
            'mercados': {
                'restricted': ['Platos', 'salud'],
                'allow' : ['*']
            },
            'salud': {
                'restricted': ['*'],
                'allow' : ['salud']
            },
        }
        permits_of_instance = list(permits.values())[self.store_type-1]
        return permits_of_instance




