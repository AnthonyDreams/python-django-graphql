from django.db import models

# Create your models here.
class Event(models.Model):
    event_name = models.CharField(max_length=250)
    time_it_starts = models.TimeField()
    day_of_event = models.DateField()
    date_to_be_delivered = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey('address.Address', on_delete=models.PROTECT)
    orders = models.ManyToManyField('order.Order')