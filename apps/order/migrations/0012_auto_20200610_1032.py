# Generated by Django 2.0.5 on 2020-06-10 14:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_auto_20200608_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='client_checked_status',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'cancelada_cliente'), (1, 'cancelada_staff'), (2, 'pendiente'), (3, 'aceptada'), (4, 'preparando'), (5, 'to deliver'), (6, 'on delivery'), (7, 'completada')], default=0),
        ),
    ]
