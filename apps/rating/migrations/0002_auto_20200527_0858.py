# Generated by Django 2.0.5 on 2020-05-27 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stores', '0001_initial'),
        ('rating', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rate',
            name='rater',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rate',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.Store'),
        ),
    ]
