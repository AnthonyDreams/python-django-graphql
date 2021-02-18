from django.contrib import admin
from .models import HorariosType, Store, Horarios, Booking

# Register your models here.
admin.site.register(Store)
admin.site.register(Horarios)

admin.site.register(HorariosType)
admin.site.register(Booking)