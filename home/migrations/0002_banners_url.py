# Generated by Django 5.2 on 2025-05-30 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='banners',
            name='url',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='آدرس صفحه'),
        ),
    ]
