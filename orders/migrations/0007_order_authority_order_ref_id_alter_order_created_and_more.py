# Generated by Django 5.2 on 2025-06-08 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_shipping_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='authority',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='کد مرجع زرین\u200cپال'),
        ),
        migrations.AddField(
            model_name='order',
            name='ref_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='شماره پیگیری پرداخت'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='آخرین آپدیت'),
        ),
    ]
