# Generated by Django 2.0.5 on 2020-06-08 14:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_order_payment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='client_checked_status',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='updated_order',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
