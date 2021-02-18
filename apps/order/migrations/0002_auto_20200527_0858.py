# Generated by Django 2.0.5 on 2020-05-27 12:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('promotions', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='coupons',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='promotions.Coupons'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='modifications',
            field=models.ManyToManyField(blank=True, to='products.ModificationItems'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orderitems', to='order.Order'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='products.Product'),
        ),
    ]