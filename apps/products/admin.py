from django.contrib import admin
from .models import Product, Type, Modifier, ModificationItems, Category


admin.site.register(Product)
admin.site.register(Type)
admin.site.register(Category)

admin.site.register(Modifier)
admin.site.register(ModificationItems)



# Register your models here.
