# Generated by Django 5.2 on 2025-06-21 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_partnership_partnermonthlyset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnership',
            name='code',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='کد همکاری'),
        ),
    ]
