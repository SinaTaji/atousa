from django.core.cache import cache
from random import randint
from django.core.exceptions import ValidationError
from utils.sms import send_otp


def GenerateAndSendOtp(phone, purpose='general'):
    count_key = f'otp_send_count:{phone}'
    blocked_key = f'otp_blocked:{phone}'

    send_count = cache.get(count_key, 0)

    if send_count >= 3:
        cache.set(blocked_key, True, timeout=7200)
        raise ValidationError(' شما به محدودیت تعداد درخواست رسیده اید لطفا بعدا دوباره امتحان کنید')

    cache_key = f'otp:{phone}'
    code = randint(1000, 9999)
    print('=' * 90)
    print(code)
    print('=' * 90)
    cache.set(cache_key, code, timeout=120)
    send_otp(phone, code)
    cache.set(count_key, send_count + 1, timeout=7200)
    return True


def GetAndCheckOtp(request, phone):
    user_otp = request.POST.get('user_otp')
    if user_otp is None:
        raise ValidationError('کد تایید خود را وارد کنید')
    if not user_otp.isdigit():
        raise ValidationError('کد تایید باید فقط شامل اعداد باشد.')

    user_otp = int(user_otp)
    cache_key = f'otp:{phone}'
    otp = cache.get(cache_key)

    if otp is None:
        raise ValidationError('کد شما منقضی شده است')
    if user_otp != otp:
        raise ValidationError('کد وارد شده صحیح نیست')
    if otp == user_otp:
        return True


