import secrets
import string
from decimal import Decimal
from admin_panel.utils import update_stats_on_partner_order
from .models import Partnership, PartnerMonthlySet, Gift


def generate_secure_code(length=10):
    from .models import Partnership
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))
        if not Partnership.objects.filter(code=code).exists():
            return code


def promote_partner(user, monthly_sells):
    try:
        partner = Partnership.objects.get(user=user, is_active=True)
    except Partnership.DoesNotExist:
        return

    current_rank = partner.rank
    new_rank = current_rank

    if current_rank == 'bronze' and monthly_sells > 3000000:
        new_rank = 'silver'
    elif current_rank == 'silver' and monthly_sells > 9000000:
        new_rank = 'gold'
    elif current_rank == 'gold' and monthly_sells < 9000000:
        new_rank = 'silver'

    if new_rank != current_rank:
        partner.rank = new_rank
        partner.save(update_fields=['rank'])
        if rank_priority(new_rank) > rank_priority(current_rank):
            from aboutus_contactus.utils import send_message
            send_message(user, type='rankup')
            duration_gift_code(partner, 10, 7, gift_type='rank_up')


def rank_priority(rank):
    priorities = {
        'bronze': 1,
        'silver': 2,
        'gold': 3,
    }
    return priorities.get(rank, 0)


def update_partner_stats(request, order):
    code = request.session.get('ref_code')
    user = request.user
    if code:
        try:
            partner = Partnership.objects.get(code=code, is_active=True)
        except Partnership.DoesNotExist:
            return
    else:
        try:
            partner = Partnership.objects.get(user=user, is_active=True)
        except Partnership.DoesNotExist:
            return
    monthly_stat = PartnerMonthlySet.objects.filter(partner=partner).order_by('-created_at').first()
    if partner.is_evaluation_due():
        promote_partner(user, monthly_stat.monthly_sells)
        partner.reset_evaluation_timer()
        partner.create_monthly_record()
        monthly_stat = PartnerMonthlySet.objects.filter(partner=partner).order_by('-created_at').first()

    monthly_stat.sales_count += 1
    partner.sells += 1
    monthly_stat.monthly_sells += order.total_price
    rank = partner.rank
    is_partner = partner.user == user
    price = order.total_price
    commission = 0

    if is_partner:
        if rank == 'gold':
            commission = price * Decimal('0.14')
        else:
            commission = price * Decimal('0.05')
    else:
        if rank == 'bronze':
            commission = price * Decimal('0.05')
        elif rank == 'silver':
            commission = price * Decimal('0.09')
        elif rank == 'gold':
            commission = price * Decimal('0.14')

    monthly_stat.commission_monthly += commission
    partner.commission_can_clime += commission
    partner.commission_earned += commission
    update_stats_on_partner_order(order, commission)
    monthly_stat.save()
    partner.save()


def is_partner(request):
    if request.user.is_authenticated:
        user = request.user
        return Partnership.objects.filter(user=user, is_active=True).exists()
    return False


# =========================== gift code ======================
def generate_gift_code(length=15):
    from .models import Gift
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))
        if not Gift.objects.filter(gift_code=code).exists():
            return code


def get_gift_message(partner, percent, days, gift_type='default'):
    first_name = partner.first_name
    rank = partner.get_rank_display()

    if gift_type == 'welcome':
        return (
            f"{first_name} عزیز، سلام! 🌸\n"
            f"به خانواده‌ی آتوسا خوش اومدی! خیلی خوشحالیم که از امروز قراره با هم مسیر زیبایی رو شروع کنیم 💫\n"
            f"برای شروع، یه کد تخفیف {percent}% برات فعال کردیم تا باهاش اولین قدم‌های فروش‌ت رو محکم‌تر برداری 🎁\n"
            f"این کد اختصاصی تا {days} روز فعاله و می‌تونه بهت کمک کنه مشتری جذب کنی و زودتر دیده بشی 🌟\n"
            f"ما اینجاییم تا کنارت باشیم. به دنیای آتوسا خوش اومدی 💖"
        )

    elif gift_type == 'rank_up':
        return (
            f"{first_name} عزیز، سلام و تبریک از طرف خانواده‌ی آتوسا! 🎉\n"
            f"ارتقا به سطح {rank} نشانه‌ی تعهد، پشتکار و همراهی ارزشمند تو با ماست 🌟\n"
            f"به پاس این تلاش‌ها، با افتخار یک کد تخفیف {percent}% ویژه برای شما فعال کرده‌ایم 🎁\n"
            f"این کد تا {days} روز اعتبار دارد تا بتوانی فروش خود را ارتقا دهی 💼\n"
            f"آتوسا قدردان حضور ارزشمندت است و همواره همراه و پشتیبان تو خواهد بود. با بهترین آرزوها، تیم آتوسا ❤️"
        )


def duration_gift_code(partner, percent, days, gift_type='default'):
    gift_code = generate_gift_code()
    description = get_gift_message(partner, percent, days, gift_type)

    Gift.objects.create(
        partner=partner,
        gift_code=gift_code,
        title='کد تخفیف ویژه شما',
        percent=percent,
        expire_after_days=days,
        description=description,
    )
