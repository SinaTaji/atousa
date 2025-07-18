# Generated by Django 5.2 on 2025-06-03 18:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='نام')),
                ('last_name', models.CharField(max_length=100, verbose_name='نام خانوادگی')),
                ('province', models.CharField(max_length=50, verbose_name='استان')),
                ('city', models.CharField(max_length=50, verbose_name='شهر')),
                ('address', models.CharField(max_length=150, verbose_name='آدرس')),
                ('postal_code', models.CharField(max_length=15, verbose_name='کد پستی')),
                ('phone', models.CharField(max_length=15, verbose_name='شماره تماس گیرنده')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.order', verbose_name='سبد خرید')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'آدرس کاربر',
                'verbose_name_plural': 'آدرس کاربران',
                'db_table': 'user_address',
            },
        ),
    ]
