# Generated by Django 5.2 on 2025-05-30 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='banners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='عنوان بنر')),
                ('banner_image', models.ImageField(upload_to='banners', verbose_name='تصویر بنر')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'بنر',
                'verbose_name_plural': 'بنرها',
                'db_table': 'banners',
                'ordering': ['title'],
            },
        ),
    ]
