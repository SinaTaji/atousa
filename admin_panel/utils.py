import jdatetime
from django.db import transaction
from .models import Stats


def update_stats_on_order(order):
    today_j = jdatetime.date.today()
    today_g = today_j.togregorian()

    year = today_j.year
    month = today_j.month
    day = today_j.day

    final_price = order.total_price

    with transaction.atomic():
        # روزانه
        daily_stat, _ = Stats.objects.update_or_create(
            type='daily',
            year=year, month=month, day=day,
            defaults={
                'jalali_date': str(today_j),
                'date': today_g,
            }
        )
        daily_stat.increment(final_price)

        # ماهانه
        monthly_stat, _ = Stats.objects.update_or_create(
            type='monthly',
            year=year, month=month,
            defaults={
                'jalali_date': f"{year}/{str(month).zfill(2)}",
                'date': today_g,
            }
        )
        monthly_stat.increment(final_price)

        # سالانه
        yearly_stat, _ = Stats.objects.update_or_create(
            type='yearly',
            year=year,
            defaults={
                'jalali_date': str(year),
                'date': today_g,
            }
        )
        yearly_stat.increment(final_price)


def increment(self, final_price):
    self.total_orders += 1
    self.total_sales += final_price
    self.save()


Stats.increment = increment


def update_stats_on_user_signup():
    today_j = jdatetime.date.today()
    today_g = today_j.togregorian()

    year = today_j.year
    month = today_j.month
    day = today_j.day

    with transaction.atomic():
        # ثبت در روزانه
        Stats.objects.update_or_create(
            type='daily',
            year=year, month=month, day=day,
            defaults={
                'jalali_date': str(today_j),
                'date': today_g,
            },
        )[0].increment_user_signup()

        # ثبت در ماهانه
        Stats.objects.update_or_create(
            type='monthly',
            year=year, month=month,
            defaults={
                'jalali_date': f"{year}/{str(month).zfill(2)}",
                'date': today_g,
            },
        )[0].increment_user_signup()

        # ثبت در سالانه
        Stats.objects.update_or_create(
            type='yearly',
            year=year,
            defaults={
                'jalali_date': str(year),
                'date': today_g,
            },
        )[0].increment_user_signup()


def increment_user_signup(self):
    self.user_signups += 1
    self.save()


Stats.increment_user_signup = increment_user_signup


def update_stats_on_partner_signup():
    today_j = jdatetime.date.today()
    today_g = today_j.togregorian()

    year = today_j.year
    month = today_j.month
    day = today_j.day

    with transaction.atomic():
        Stats.objects.update_or_create(
            type='daily',
            year=year, month=month, day=day,
            defaults={
                'jalali_date': str(today_j),
                'date': today_g,
            },
        )[0].increment_partner_signups()

        Stats.objects.update_or_create(
            type='monthly',
            year=year, month=month,
            defaults={
                'jalali_date': f"{year}/{str(month).zfill(2)}",
                'date': today_g,
            },
        )[0].increment_partner_signups()

        Stats.objects.update_or_create(
            type='yearly',
            year=year,
            defaults={
                'jalali_date': str(year),
                'date': today_g,
            },
        )[0].increment_partner_signups()


def increment_partner_signups(self):
    self.partner_signups += 1
    self.save()


Stats.increment_partner_signups = increment_partner_signups


def update_stats_on_partner_order(order, commission):
    today_j = jdatetime.date.today()
    today_g = today_j.togregorian()

    year = today_j.year
    month = today_j.month
    day = today_j.day

    final_price = order.total_price

    with transaction.atomic():
        # روزانه
        daily_stat, _ = Stats.objects.update_or_create(
            type='daily',
            year=year, month=month, day=day,
            defaults={
                'jalali_date': str(today_j),
                'date': today_g,
            }
        )
        daily_stat.increment_partner(final_price, commission)

        # ماهانه
        monthly_stat, _ = Stats.objects.update_or_create(
            type='monthly',
            year=year, month=month,
            defaults={
                'jalali_date': f"{year}/{str(month).zfill(2)}",
                'date': today_g,
            }
        )
        monthly_stat.increment_partner(final_price, commission)

        # سالانه
        yearly_stat, _ = Stats.objects.update_or_create(
            type='yearly',
            year=year,
            defaults={
                'jalali_date': str(year),
                'date': today_g,
            }
        )
        yearly_stat.increment_partner(final_price, commission)


def increment_partner(self, final_price, commission):
    self.partner_orders += 1
    self.partner_sales += final_price
    self.partner_commission += commission
    self.save()


Stats.increment_partner = increment_partner
