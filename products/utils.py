import random


def generate_unique_product_code():
    from .models import Product
    while True:
        code = random.randint(10000, 99999)
        if not Product.objects.filter(code=code).exists():
            return code
