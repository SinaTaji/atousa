from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import jdatetime
from .models import Stats


@login_required
@staff_member_required
def daily_sales_current_month(request):
    today = jdatetime.date.today()
    year = today.year
    month = today.month

    stats = Stats.objects.filter(
        type='daily',
        year=year,
        month=month,
    )

    data_map = {stat.day: stat for stat in stats}

    labels = list(range(1, 31))  # از ۱ تا ۳۰
    sales = []
    orders = []
    p_sales = []
    p_orders = []
    signups = []
    p_signups = []
    commission = []

    for day in labels:
        stat = data_map.get(day)
        sales.append(stat.total_sales if stat else 0)
        orders.append(stat.total_orders if stat else 0)
        p_sales.append(stat.partner_sales if stat else 0)
        p_orders.append(stat.partner_orders if stat else 0)
        commission.append(stat.partner_commission if stat else 0)
        signups.append(stat.user_signups if stat else 0)
        p_signups.append(stat.partner_signups if stat else 0)

    return JsonResponse({
        'labels': [str(d) for d in labels],
        'sales': sales,
        'orders': orders,
        'signups': signups,
        'p_signups': p_signups,
        'p_sales': p_sales,
        'p_orders': p_orders,
        'p_commission': commission,
    })


JALALI_MONTHS = [
    'فروردین', 'اردیبهشت', 'خرداد',
    'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر',
    'دی', 'بهمن', 'اسفند',
]


@login_required
@staff_member_required
def monthly_sales_current_year(request):
    today = jdatetime.date.today()
    stats = Stats.objects.filter(
        type='monthly',
        year=today.year,
    )

    month_data = {stat.month: stat for stat in stats}

    labels = []
    sales = []
    orders = []
    p_sales = []
    p_orders = []
    signups = []
    p_signups = []
    commission = []

    for month in range(1, 13):
        stat = month_data.get(month)
        labels.append(JALALI_MONTHS[month - 1])
        sales.append(stat.total_sales if stat else 0)
        orders.append(stat.total_orders if stat else 0)
        p_sales.append(stat.partner_sales if stat else 0)
        p_orders.append(stat.partner_orders if stat else 0)
        commission.append(stat.partner_commission if stat else 0)
        signups.append(stat.user_signups if stat else 0)
        p_signups.append(stat.partner_signups if stat else 0)

    return JsonResponse(
        {'labels': labels, 'sales': sales, 'orders': orders, 'signups': signups, 'p_signups': p_signups,
         'p_sales': p_sales,
         'p_orders': p_orders, 'p_commission': commission, })


@login_required
@staff_member_required
def yearly_sales(request):
    start_year = 1404
    end_year = 1414

    stats = Stats.objects.filter(
        type='yearly',
        year__gte=start_year,
        year__lte=end_year
    )

    data_map = {stat.year: stat for stat in stats}

    labels = []
    sales = []
    orders = []
    p_sales = []
    p_orders = []
    signups = []
    p_signups = []
    commission = []

    for year in range(start_year, end_year + 1):
        stat = data_map.get(year)
        labels.append(str(year))
        sales.append(stat.total_sales if stat else 0)
        orders.append(stat.total_orders if stat else 0)
        p_sales.append(stat.partner_sales if stat else 0)
        p_orders.append(stat.partner_orders if stat else 0)
        commission.append(stat.partner_commission if stat else 0)
        signups.append(stat.user_signups if stat else 0)
        p_signups.append(stat.partner_signups if stat else 0)

    return JsonResponse(
        {'labels': labels, 'sales': sales, 'orders': orders, 'signups': signups, 'p_signups': p_signups,
         'p_sales': p_sales,
         'p_orders': p_orders, 'p_commission': commission, })
