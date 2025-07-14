import requests
from django.conf import settings
import logging

from django.urls import reverse

logger = logging.getLogger(__name__)

ZARINPAL_REQUEST_URL = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_VERIFY_URL = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"

HEADERS = {
    'accept': 'application/json',
    'content-type': 'application/json'
}


def send_payment_request(order, phone,request):
    """
    ارسال درخواست پرداخت به زرین‌پال
    """
    callback_url = request.build_absolute_uri(reverse('orders:order_payment_verify'))
    data = {
        "merchant_id": settings.MERCHANT_ID,
        "amount": order.total_price * 10,
        # "callback_url": settings.CALLBACK_URL,
        "callback_url": callback_url,
        "description": f"پرداخت فاکتور شماره {order.code}",
        "metadata": {"phone": phone}
    }

    try:
        response = requests.post(ZARINPAL_REQUEST_URL, json=data, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.exception("خطا در ارسال درخواست پرداخت به زرین‌پال")
        raise RuntimeError(f"Zarinpal request error: {e}")


def verify_payment(order, authority):
    """
    بررسی وضعیت پرداخت
    """
    data = {
        "merchant_id": settings.MERCHANT_ID,
        "amount": order.total_price * 10,
        "authority": authority
    }

    try:
        response = requests.post(ZARINPAL_VERIFY_URL, json=data, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.exception("خطا در وریفای پرداخت با زرین‌پال")
        raise RuntimeError(f"Zarinpal verify error: {e}")
