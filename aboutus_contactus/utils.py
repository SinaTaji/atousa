from django.core.cache import cache


def update_order_status(order):
    if not order.get_in_post and not order.finished:
        return

    if order.finished:
        return

    cache_key = f'order-{order.code}'
    still_in_post = cache.get(cache_key)

    if order.get_in_post and not still_in_post:
        order.get_in_post = False
        order.finished = True
        order.save(update_fields=['get_in_post', 'finished'])
        cache.delete(cache_key)


def message_type(type='default'):
    if type == 'welcome':
        return (
            'خرید شما با موفقیت ثبت شد 🌟'
            ' ممنونیم که آتوسا رو برای خریدتون انتخاب کردید.'
            ' سفارش شما با موفقیت ثبت شد و در حال آماده‌سازی برای ارسال است.'
            '  می‌تونید در هر لحظه از وضعیت سفارش‌تون در پنل کاربری مطلع بشید و مرحله به مرحله روند پردازش و ارسال اون رو پیگیری کنید.'
            ' اگر سوال یا مشکلی داشتید، با افتخار در کنارتون هستیم 💛'
        )
    if type == 'partner':
        return (
            "🎉 درخواست همکاری شما با موفقیت پذیرفته شد!\n"
            "خوشحالیم که از این به بعد کنارمون هستید و به جمع همکاران آتوسا پیوستید.\n"
            "حالا می‌تونید از طریق پنل کاربری به بخش همکاری دسترسی داشته باشید و فعالیت‌تون رو آغاز کنید.\n"
            "در صورت نیاز به راهنمایی یا پشتیبانی، تیم ما همیشه همراه شماست 💛"
        )
    if type == 'rankup':
        return (
            "🎉 تبریک صمیمانه ما رو بپذیرید!\n"
            "با افتخار اعلام می‌کنیم که رده‌ی همکاری شما در آتوسا ارتقا پیدا کرده 🌟\n"
            "این ارتقا نتیجه‌ی پشتکار، تعهد و همراهی ارزشمند شماست.\n"
            "ما به حضور شما در جمع همکاران آتوسا افتخار می‌کنیم و قدردان تلاش‌های شما هستیم.\n"
            "امیدواریم در مسیر پیش رو، با انرژی بیشتر و موفقیت‌های بزرگ‌تر همراه ما باشید.\n"
            "همیشه کنار شما هستیم 💛"
        )


def send_message(user, type='default'):
    from .models import ReplyContact
    ReplyContact.objects.create(
        user=user,
        text=message_type(type),
    )
