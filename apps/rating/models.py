from django.db import models
from django.template.defaultfilters import date as _date
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)

# Create your models here.

class Rate(models.Model):
    point = models.DecimalField(max_digits = 2, decimal_places = 1)
    text = models.TextField()
    store = models.ForeignKey('address.StoreLocations', on_delete=models.CASCADE)
    rater = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='rates')
    created_date = models.DateTimeField(auto_now_add=True)

    @property
    def str_created_date(self):
        return _date(self.created_date, "l, d b")

    @property
    def is_mine(self):
        return self.rater == get_current_authenticated_user()
