# Generated by Django 5.2 on 2025-05-30 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_rename_banners_banner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='banner',
            name='banner_image',
        ),
        migrations.AddField(
            model_name='banner',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='banners/1', verbose_name='تصویر بنر'),
        ),
    ]
