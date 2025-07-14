from django.db import models


class Stats(models.Model):
    class Period(models.TextChoices):
        DAILY = 'daily', 'روزانه'
        MONTHLY = 'monthly', 'ماهانه'
        YEARLY = 'yearly', 'سالانه'

    type = models.CharField(max_length=10, choices=Period.choices)
    jalali_date = models.CharField(max_length=10, blank=True, null=True, verbose_name='تاریخ')
    date = models.DateField(null=True, blank=True, verbose_name='تاریخ میلادی')

    year = models.IntegerField(verbose_name='سال')
    month = models.IntegerField(null=True, blank=True, verbose_name='ماه')
    day = models.IntegerField(null=True, blank=True, verbose_name='روز')

    total_sales = models.PositiveBigIntegerField(default=0, verbose_name='مقدار فروش')
    total_orders = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش')
    user_signups = models.PositiveIntegerField(default=0, verbose_name='ثبت‌نام کاربران')
    partner_signups = models.PositiveIntegerField(default=0, verbose_name='ثبت‌نام همکاران')
    partner_orders = models.PositiveIntegerField(default=0, verbose_name='تعداد خرید همکاران')
    partner_sales = models.PositiveBigIntegerField(default=0, verbose_name='مقدار خرید همکاران')
    partner_commission = models.PositiveBigIntegerField(default=0, verbose_name='مقدار پورسانت همکاران')

    class Meta:
        verbose_name = 'آمار فروش سایت'
        verbose_name_plural = 'آمار فروش های سایت'
        unique_together = [('type', 'year', 'month', 'day')]

    def __str__(self):
        return f"{self.get_type_display()} - {self.jalali_date or self.year}"


class Notification(models.Model):
    title = models.CharField(max_length=200, verbose_name='موضوع')
    message = models.TextField(verbose_name='متن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    is_seen = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
