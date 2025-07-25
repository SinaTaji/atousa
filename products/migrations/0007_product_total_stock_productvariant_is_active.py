# Generated by Django 5.2 on 2025-06-09 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_clothespart_partattribute_measurementpreset_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='total_stock',
            field=models.PositiveIntegerField(default=0, verbose_name='موجودی کل'),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='موجود است'),
        ),
    ]
