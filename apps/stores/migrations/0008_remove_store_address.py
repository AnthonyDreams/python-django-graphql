# Generated by Django 2.0.5 on 2020-06-15 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0007_auto_20200615_1411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='address',
        ),
    ]
