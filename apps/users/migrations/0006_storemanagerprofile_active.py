# Generated by Django 2.0.5 on 2020-06-03 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200603_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='storemanagerprofile',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
