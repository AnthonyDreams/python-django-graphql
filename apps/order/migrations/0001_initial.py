# Generated by Django 2.0.5 on 2020-05-27 12:58

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_code', models.CharField(max_length=10)),
                ('deliver_to', django.contrib.postgres.fields.jsonb.JSONField()),
                ('ordered_time', models.DateTimeField(auto_now_add=True)),
                ('comment', models.CharField(max_length=250)),
                ('payment_status', models.IntegerField(choices=[(0, 'Not Paid'), (2, 'Partial Paid'), (1, 'Paid')], default=0)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('quantity', models.IntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
