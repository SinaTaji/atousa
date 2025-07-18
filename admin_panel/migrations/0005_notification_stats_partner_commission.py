# Generated by Django 5.2 on 2025-07-08 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0004_stats_partner_orders_stats_partner_sales_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='موضوع')),
                ('message', models.TextField(verbose_name='متن')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('is_seen', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='stats',
            name='partner_commission',
            field=models.PositiveBigIntegerField(default=0, verbose_name='مقدار پورسانت همکاران'),
        ),
    ]
