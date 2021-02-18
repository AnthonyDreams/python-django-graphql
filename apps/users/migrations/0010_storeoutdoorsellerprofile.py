# Generated by Django 2.0.5 on 2020-06-21 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20200621_1215'),
        ('address', '0003_storelocations'),
        ('users', '0009_storemanagerprofile_checked_notifications'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreOutdoorSellerProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outdoor_seller_type', models.PositiveSmallIntegerField(choices=[(1, 'street_stablishment'), (2, 'door_to_door'), (3, 'nomada')], default=1)),
                ('cedula', models.CharField(max_length=11)),
                ('product_sells', models.ManyToManyField(related_name='outdoor_sellers_in_stock', to='products.Product')),
                ('store', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='outdoor_sellers', to='address.StoreLocations')),
            ],
        ),
    ]
