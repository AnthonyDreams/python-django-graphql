# Generated by Django 2.0.5 on 2020-06-15 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0003_storelocations'),
        ('products', '0005_auto_20200531_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='in_stock',
            field=models.ManyToManyField(blank=True, to='address.StoreLocations'),
        ),
    ]
