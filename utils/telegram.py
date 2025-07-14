import threading
import requests
from django.conf import settings

from admin_panel.models import Notification


def _send_message_in_thread(text):
    def task():
        topic = settings.NTFY_TOPIC
        url = f"https://ntfy.sh/{topic}"

        headers = {
            "Title": "Atousa",
            "Priority": "high",
        }

        try:
            response = requests.post(url, data=text, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            try:
                print("Ntfy Error:", e)
            except Exception:
                pass

    threading.Thread(target=task, daemon=True).start()


def send_telegram_message(text):
    _send_message_in_thread(text)


def notify(title: str, body: str = '', emoji: str = '🔔'):
    message = f"{emoji} {title}\n\n{body.strip()}"
    send_telegram_message(message)
    Notification.objects.create(title=title, message=body)


def notify_new_order(order):
    text = f"🛒 سفارش #{order.code} از {order.user}\nمبلغ: {order.total_price:,} تومان"
    notify("سفارش جدید", text)


def notify_contact_us(user, contact, message):
    text = f"📨 تیکت جدید از {user}\nموضوع: {contact}\n{message[:100]}"
    notify("پیام جدید", text)


def notify_partner_register(first_name, last_name):
    text = f"➕🤝 {first_name} {last_name} درخواست همکاری داده"
    notify("ثبت نام همکار", text)


def notify_register(user):
    text = f"➕ {user} ثبت‌نام کرد"
    notify("ثبت نام کاربر", text)


def notify_withdraw(user, card, amount):
    text = f"📤 درخواست برداشت از {user}\nشماره کارت: {card}\nمبلغ: {amount:,} تومان"
    notify("درخواست برداشت", text)
