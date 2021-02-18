from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)
from django.db.models import Sum
# Create your models here.
class DeliveryInfo(models.Model):

    TYPES_CHOICES = (
            (1, ('Home')),
            (2, ('Work')),
            (3, ('Other'))
        )

    type = models.PositiveSmallIntegerField (_('Type'),  choices=TYPES_CHOICES, default=1)
    alias = models.CharField(max_length=40, null=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    location = models.ForeignKey('Address', on_delete=models.CASCADE, null = False)
    delivery_instruction = models.CharField(max_length=250, null=True, blank=True)
    user_address_text = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=False, related_name="delivery_info")
    selected = models.BooleanField(default=False)
    def __str__(self):
        return str(self.alias)
        

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['user', 'type'], name='delivery_address_uniquesity')
    #     ]


class StoreLocations(models.Model):
    
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    location = models.ForeignKey('Address', on_delete=models.CASCADE, null = False)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=False, related_name="store_location")
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.store.name} {self.location.street_line1}"

    @property
    def get_name_with_location(self):
        return f"{self.store.name} {self.location.street_line1}"

    @property
    def is_fav(self):
        
        return self.preferences_set.filter(account=get_current_authenticated_user()).exists()
    
    @property
    def has_rated(self):
        return self.rate_set.filter(rater=get_current_authenticated_user()).exists()

    @property
    def rate(self):
        if self.rate_set.all().count():
            return self.rate_set.aggregate(Sum('point'))['point__sum']/self.rate_set.all().count()
        return 0

    @property
    def all_rate(self):
        return self.rate_set.all().count()

        

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['user', 'type'], name='delivery_address_uniquesity')
    #     ]

class Address(models.Model):
    
    geo = JSONField(default={'set':'False'})
    street_line1 = models.CharField(_('Address 1'), max_length=800, blank=True)
    street_line2 = models.CharField(_('Address 2'), max_length=800, blank=True)
    city = models.CharField(_('City'), max_length=800, blank=True)
    locality = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(_('State'), max_length=800, blank=True, default='Republica Dominicana')
    
    def __str__(self):
        return str(self.street_line1)

    
    @property
    def address_string(self):
        string = [self.city, self.street_line1]
        # if self.street_line1 != self.street_line2:
        #     string.insert(2, self.street_line2)
        # if self.city != self.locality:
        #     string.insert(1,self.city)
        
        print(', '.join(string))
        return  ', '.join(string)

