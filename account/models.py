from datetime import timedelta
import jdatetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=11, unique=True, verbose_name='شماره موبایل')
    is_active = models.BooleanField(default=True, verbose_name='حساب کاری فعال است ؟')
    is_superuser = models.BooleanField(default=False, verbose_name='آیا مدیر سایت است')
    is_staff = models.BooleanField(default=False, verbose_name='آیا عضو مدیریت سایت است ؟')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد حساب')

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    def __str__(self):
        return self.phone

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_staff

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        db_table = 'user'
        ordering = ('-created_at',)


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='محصول')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'علاقه مندی'
        verbose_name_plural = 'لیست علاقه مندی ها'
        db_table = 'wishlist'
        ordering = ('created_at',)
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user} ❤️ {self.product}'


class Partnership(models.Model):
    Ranking = [
        ('bronze', 'برنزی'),
        ('silver', 'نقره ای'),
        ('gold', 'طلایی'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='partner/prof/',
        processors=[ResizeToFill(220, 220)],
        format='WEBP',
        options={'quality': 100}
    )
    code = models.CharField(max_length=10, verbose_name='کد همکاری', unique=True, null=True, blank=True)
    rank = models.CharField(max_length=50, choices=Ranking, verbose_name='سطح کاربر', default='bronze')
    sells = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت همکار')
    is_active = models.BooleanField(verbose_name='همکار شود ؟', default=False)
    commission_can_clime = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                               verbose_name=' پورسانت قابل برداشت')
    commission_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مجموع پورسانت')
    eval_start_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ شروع ارزیابی')
    last_evaluated_at = models.DateTimeField(null=True, blank=True, verbose_name='آخرین زمان ارزیابی')

    class Meta:
        verbose_name = 'همکار'
        verbose_name_plural = 'همکاران'
        db_table = 'partnership'
        ordering = ('-created_at',)

    def is_evaluation_due(self):
        return timezone.now() >= self.eval_start_date + timedelta(days=30)

    def reset_evaluation_timer(self):
        now = timezone.now()
        self.eval_start_date = now
        self.last_evaluated_at = now
        self.save(update_fields=['eval_start_date', 'last_evaluated_at'])

    def create_monthly_record(self):
        today = jdatetime.date.today()
        PartnerMonthlySet.objects.create(
            partner=self,
            year=today.year,
            month=today.month,
            sales_count=0,
            commission_monthly=0,
            monthly_sells=0)

    def days_left_to_evaluation(self):
        end = self.eval_start_date + timedelta(days=30)
        remaining = end - timezone.now()
        return max(remaining.days + 1, 0)

    def save(self, *args, **kwargs):
        is_new_activation = False

        if self.is_active and not self.code:
            from .utils import generate_secure_code
            self.code = generate_secure_code()
            from aboutus_contactus.utils import send_message
            send_message(self.user, type='partner')
            self.eval_start_date = timezone.now()
            self.last_evaluated_at = timezone.now()
            is_new_activation = True
            from .utils import duration_gift_code
            duration_gift_code(partner=self, percent=10, days=7, gift_type='welcome')

        super().save(*args, **kwargs)
        if is_new_activation:
            today = jdatetime.date.today()
            PartnerMonthlySet.objects.create(
                partner=self,
                year=today.year,
                month=today.month,
                sales_count=0,
                commission_monthly=0,
                monthly_sells=0
            )

    def __str__(self):
        return f'{self.first_name} {self.last_name}-{self.code}'


class Gift(models.Model):
    partner = models.ForeignKey(Partnership, on_delete=models.CASCADE, verbose_name='همکار', related_name='gifts')
    title = models.CharField(max_length=100, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیح')
    gift_code = models.CharField(max_length=15, verbose_name='کد هدیه', unique=True, null=True, blank=True)
    percent = models.PositiveSmallIntegerField(default=0, verbose_name='درصد تخفیف')
    is_active = models.BooleanField(default=False, verbose_name='آیا فعال است')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    expire_after_days = models.PositiveIntegerField(default=0, verbose_name='انقضا پس از چند روز')
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انقضا')
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر دفعات استفاده')
    used_count = models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده شده')

    class Meta:
        verbose_name = 'کد تخفیف کاربر'
        verbose_name_plural = 'کد های تخفیف کاربران'
        db_table = 'gift'
        ordering = ('created_at',)
        unique_together = ('partner', 'gift_code')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        now = timezone.now()

        if is_new:
            if self.expire_after_days > 0 and not self.valid_until:
                self.valid_until = now + timedelta(days=self.expire_after_days)
            if not self.gift_code:
                from .utils import generate_gift_code
                self.gift_code = generate_gift_code()
            self.is_active = True

        super().save(*args, **kwargs)

    def is_valid(self):
        if not self.is_active:
            return False

        if self.valid_until and self.valid_until < timezone.now():
            return False

        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False

        return True

    def usage(self):
        return self.max_uses - self.used_count

    def __str__(self):
        return f'{self.title}-{self.partner}'


class PartnerMonthlySet(models.Model):
    partner = models.ForeignKey(Partnership, on_delete=models.CASCADE, verbose_name='همکار',
                                related_name='monthly_stat')
    year = models.IntegerField(verbose_name='سال')
    month = models.IntegerField(verbose_name='ماه')
    sales_count = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش ماهانه')
    commission_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=' پورسانت ماهانه')
    monthly_sells = models.IntegerField(default=0, verbose_name='فروش ماهانه')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def how_much_to_promote(self):
        rank = self.partner.rank
        sells = self.monthly_sells

        thresholds = {
            'bronze': 3_000_000,
            'silver': 9_000_000,
            'gold': 9_000_000
        }

        required = thresholds.get(rank)
        if required is None:
            return None  # رنک نامعتبر

        if rank in ['bronze', 'silver']:
            if sells >= required:
                return True
            else:
                return required - sells
        elif rank == 'gold':
            if sells < required:
                return required - sells
            else:
                return True

    class Meta:
        verbose_name = 'عملکرد ماهانه همکار'
        verbose_name_plural = 'عملکرد های ماهانه همکاران'
        db_table = 'partner_monthly_set'
        ordering = ('-year', '-month')
        unique_together = ('partner', 'year', 'month')

    def __str__(self):
        return f'{self.partner} {self.year} {self.month}'


class Withdraw(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر', related_name='withdraws')
    amount = models.PositiveIntegerField(verbose_name="مبلغ")
    card = models.CharField(max_length=22, verbose_name='شماره کارت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    is_paid = models.BooleanField(default=False, verbose_name='آیا پرداخت شده')
    p_id = models.CharField(max_length=50, verbose_name='کد پیگیری', null=True, blank=True)

    class Meta:
        verbose_name = 'درخواست برداشت'
        verbose_name_plural = 'درخواست برداشت کاربران'
        db_table = 'withdraw'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} {self.amount} {self.card}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not is_new:
            old = Withdraw.objects.get(pk=self.pk)
            is_paid_now = self.is_paid and not old.is_paid
        else:
            is_paid_now = self.is_paid

        if is_paid_now:
            partner = Partnership.objects.get(user=self.user)
            partner.commission_can_clime -= self.amount
            partner.save(update_fields=['commission_can_clime'])

        super().save(*args, **kwargs)
