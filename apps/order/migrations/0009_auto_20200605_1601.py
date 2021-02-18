# Generated by Django 2.0.5 on 2020-06-05 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'cancelada_cliente'), (1, 'cancelada_staff'), (2, 'pendiente'), (3, 'aceptada'), (4, 'preparando'), (5, 'on delivery'), (6, 'completada')], default=0),
        ),
    ]
