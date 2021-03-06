# Generated by Django 2.0.5 on 2020-05-27 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModificationItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('modification_price', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Modifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modifier_title', models.CharField(max_length=250)),
                ('type_id', models.PositiveSmallIntegerField(choices=[(1, 'Extras or Complements'), (2, 'Product Variations')], default=1)),
                ('obligatory', models.BooleanField(default=False)),
                ('items_has_price', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
                ('quantity_limit', models.PositiveSmallIntegerField(default=5)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.TextField(null=True)),
                ('product_img', models.ImageField(null=True, upload_to='product_img')),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('weight', models.PositiveSmallIntegerField(choices=[(1, 'LIVIANO'), (2, 'NORMAL'), (3, 'PESADO')], default=1)),
                ('time_to_prepare', models.DurationField(null=True)),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(unique=True)),
                ('sell_as_product', models.BooleanField(default=True)),
                ('sell_as_extra', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_icon', models.ImageField(null=True, upload_to='type_icon/')),
                ('type_name', models.CharField(max_length=250, unique=True)),
                ('global_type', models.BooleanField(default=False)),
            ],
        ),
    ]
