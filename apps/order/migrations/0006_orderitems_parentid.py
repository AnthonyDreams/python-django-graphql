# Generated by Django 2.0.5 on 2020-06-05 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20200605_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='parentId',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='order.OrderItems'),
        ),
    ]
