from django.db import models
from django.contrib.auth import get_user_model
from .utils import generate_unique_product_code
from django.core.cache import cache

User = get_user_model()


class Order(models.Model):
    SHIPPING_CHOICES = [
        ('pishteaz', 'پست پیشتاز'),
        ('tipax', 'ارسال با تیپاکس'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر ')
    total_price = models.PositiveIntegerField(blank=True, null=True, verbose_name='جمع فاکتور')
    paid = models.BooleanField(verbose_name='پرداخت شده ؟', default=False)
    TrackingCode = models.CharField(max_length=100, verbose_name='کد رهگیری', null=True, blank=True)
    get_in_post = models.BooleanField(default=False, verbose_name='به پست تحویل داده شد')
    finished = models.BooleanField(default=False, verbose_name='به دست کاربر رسید')
    code = models.PositiveIntegerField(null=True, blank=True, verbose_name='شماره فاکتور')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, verbose_name='آخرین آپدیت')
    address = models.ForeignKey('UserAddress', on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='آدرس ارسال')
    shipping_method = models.CharField(
        max_length=20,
        choices=SHIPPING_CHOICES,
        default='pishteaz',
        verbose_name='روش ارسال'
    )
    authority = models.CharField(max_length=255, null=True, blank=True, verbose_name='کد مرجع زرین‌پال')
    ref_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='شماره پیگیری پرداخت')

    class Meta:
        ordering = ['-created', 'paid']
        db_table = 'orders'
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'

    def save(self, *args, **kwargs):
        if self.TrackingCode and not self.get_in_post and not self.finished:
            self.get_in_post = True
            cache_key = f'order-{self.code}'
            cache.set(cache_key, True, timeout=604800)
        if not self.code:
            self.code = generate_unique_product_code()
        super().save(*args, **kwargs)

    def get_total_items_price(self):
        total_price = sum(item.price for item in self.items.all())
        return total_price

    def get_shipping_price(self):
        if self.shipping_method == 'pishteaz':
            return 0 if self.get_total_items_price() >= 2000000 else 69000
        elif self.shipping_method == 'tipax':
            return 0

    def get_final_price(self):
        return self.get_total_items_price() + self.get_shipping_price()

    def __str__(self):
        return f'{self.user}-{self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='سفارش', related_name='items')
    product = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, verbose_name='محصول')
    price = models.IntegerField(verbose_name='قیمت محصول')
    discount = models.PositiveIntegerField(verbose_name='تخفیف', default=0)
    quantity = models.IntegerField(default=1, verbose_name='تعداد')

    class Meta:
        verbose_name = 'محصول سبد خرید'
        verbose_name_plural = 'محصولات سبد های خرید'
        db_table = 'order_items'

    def __str__(self):
        return f'{self.order}'


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    province = models.CharField(max_length=50, verbose_name='استان')
    city = models.CharField(max_length=50, verbose_name='شهر')
    address = models.CharField(max_length=150, verbose_name='آدرس')
    postal_code = models.CharField(max_length=15, verbose_name='کد پستی')
    phone = models.CharField(max_length=15, verbose_name='شماره تماس گیرنده')

    class Meta:
        verbose_name = 'آدرس کاربر'
        verbose_name_plural = 'آدرس کاربران'
        db_table = 'user_address'

    def __str__(self):
        return f'{self.first_name}-{self.last_name}-{self.province}-{self.city}-{self.address}-{self.phone}'
