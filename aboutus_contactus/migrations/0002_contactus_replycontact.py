# Generated by Django 5.2 on 2025-06-10 10:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aboutus_contactus', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket', models.CharField(choices=[('orders', 'سفارشات'), ('payment', 'امور مالی'), ('jobbing', 'همکاری'), ('guid', 'راهنمایی'), ('others', 'سایر')], max_length=100, verbose_name='تیکت')),
                ('text', models.TextField(verbose_name='متن پیام')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('answered', models.BooleanField(default=False, verbose_name='پاسخ داده شده ')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'تیکت کاربر',
                'verbose_name_plural': ' تیکت های کاربران',
                'ordering': ['created_at', 'answered'],
            },
        ),
        migrations.CreateModel(
            name='ReplyContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='متن پیام')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ پاسخ')),
                ('reply_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reply_contact', to='aboutus_contactus.contactus', verbose_name='پاسخ به پیام')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reply_contacts', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'پاسخ به کاربر',
                'verbose_name_plural': 'پاسخ به کاربران',
                'ordering': ['created_at'],
            },
        ),
    ]
