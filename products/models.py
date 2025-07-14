from django.core.cache import cache
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from .utils import generate_unique_product_code
from account.models import User


class Base(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان', db_index=True)
    slug = models.CharField(max_length=100, unique=True, verbose_name='اسلاگ', null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
        cache.delete('categories')
        return self.slug

    class Meta:
        abstract = True


class Category(Base):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,
                                     verbose_name='دسته بندی اصلی', related_name='sub_categories')
    image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='products/',
        processors=[ResizeToFill(200, 200)],
        format='WEBP',
        options={'quality': 100}
    )

    class Meta:
        db_table = 'category'
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'
        ordering = ['title']

    def __str__(self):
        return self.title


    def get_all_subcategories(self):
        subcategories = list(self.sub_categories.all())
        for subcat in self.sub_categories.all():
            subcategories += subcat.get_all_subcategories()
        return subcategories

    def get_category_ancestors(self):
        ancestors = []
        category = self
        while category:
            ancestors.insert(0, category)
            category = category.sub_category
        return ancestors

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('categories')

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete('categories')


class Color(models.Model):
    title = models.CharField(max_length=20, verbose_name='نام رنگ')
    hex_color = models.CharField(max_length=7, verbose_name='شناسه رنگ')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'colors'
        verbose_name = 'رنگ'
        verbose_name_plural = 'رنگ ها'
        ordering = ['title']


class Size(models.Model):
    title = models.CharField(max_length=10, verbose_name='سایز')
    age_min = models.CharField(max_length=50, null=True, blank=True, verbose_name="حداقل سن")
    age_max = models.CharField(max_length=50, null=True, blank=True, verbose_name='حداکثر سن')

    def __str__(self):
        return f"{self.title} (برای {self.age_min} تا {self.age_max})"

    class Meta:
        db_table = 'color'
        verbose_name = 'سایز'
        verbose_name_plural = 'سایز ها'
        ordering = ['title']


class Product(Base):
    MATERIAL_CHOICES = [
        ('cotton', 'پنبه‌ای'),
        ('linen', 'کتان'),
        ('polyester', 'پلی‌استر'),
        ('wool', 'پشمی'),
        ('silk', 'ابریشم'),
    ]
    GENDER_CHOICES = [
        ('boys', 'پسرانه'),
        ('girls', 'دخترانه'),
        ('unisex', 'هر دو'),
    ]

    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null='True',
                                 verbose_name='دسته بندی', related_name='products')
    slug = models.CharField(max_length=100, verbose_name='اسلاگ', null=True, blank=True, db_index=True)
    model = models.CharField(max_length=50, verbose_name='مدل محصول', null=True, blank=True, db_index=True)
    discount = models.PositiveIntegerField(default=0, verbose_name='درصد تخفیف', null=True, blank=True)
    has_discount = models.BooleanField(default=False, verbose_name='آیا محصول تخفیف دارد؟')
    discount_expiry = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انقضا تخفیف')
    price = models.IntegerField(verbose_name='قیمت محصول', db_index=True)
    age = models.CharField(max_length=70, verbose_name='مناسب چه بازه سنی', null=True, blank=True)

    description = models.TextField(verbose_name='توضیحات کامل')
    material = models.CharField(max_length=100, choices=MATERIAL_CHOICES, verbose_name='جنس محصول')
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, verbose_name='جنسیت')
    image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='products/',
        processors=[ResizeToFill(270, 334)],
        format='WEBP',
        options={'quality': 100}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    code = models.PositiveIntegerField(unique=True, null=True, blank=True)
    views = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    total_stock = models.PositiveIntegerField(default=0, verbose_name='موجودی کل')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        if not self.code:
            self.code = generate_unique_product_code()
        super().save(*args, **kwargs)
        self.clear_homepage_caches()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.clear_homepage_caches()

    def get_discounted_price(self):
        discount = (self.discount / 100) * int(self.price)
        return self.price - discount

    class Meta:
        db_table = 'product'
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['title']

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.code, self.slug])

    def clear_homepage_caches(self):
        cache.delete('homepage_most_discount')
        cache.delete('homepage_most_recent')
        cache.delete('homepage_most_viewed')


class ProductVariant(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='محصول', related_name='variants')
    color = models.ForeignKey('Color', on_delete=models.CASCADE, verbose_name='رنگ')
    size = models.ForeignKey('Size', on_delete=models.CASCADE, verbose_name='سایز')
    discount = models.PositiveIntegerField(default=0, verbose_name='درصد تخفیف', null=True, blank=True)
    has_discount = models.BooleanField(default=False, verbose_name='آیا محصول تخفیف دارد؟')
    price = models.IntegerField(verbose_name='قیمت محصول')
    is_active = models.BooleanField(default=True, verbose_name='موجود است')
    image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='products/variant/',
        processors=[ResizeToFill(350, 433)],
        format='WEBP',
        options={'quality': 100}
    )
    stock = models.PositiveIntegerField(default=0, verbose_name='موجودی')

    class Meta:
        unique_together = ('product', 'color', 'size')
        db_table = 'product_variant'
        verbose_name = 'دسته کردن محصول'
        verbose_name_plural = 'دسته کردن محصولات'
        ordering = ['product', 'color']

    def save(self, *args, **kwargs):
        self.is_active = self.stock > 0
        super().save(*args, **kwargs)
        total = ProductVariant.objects.filter(product=self.product).aggregate(total_stock=Sum('stock'))[
                    'total_stock'] or 0
        product_active = total > 0
        Product.objects.filter(id=self.product.id).update(total_stock=total, is_active=product_active)

    def __str__(self):
        return f"{self.product.title} - {self.color.title}  "

    def get_discounted_price(self):
        discount = (self.discount / 100) * int(self.price)
        return self.price - int(discount)

    def how_mutch_discounted(self):
        discount = (self.discount / 100) * int(self.price)
        return int(discount)


class ClothesPart(models.Model):
    name = models.CharField(max_length=100, verbose_name='قطعه لباس')

    class Meta:
        verbose_name = 'قطعه لباس'
        verbose_name_plural = 'قطعات لباس'

    def __str__(self):
        return self.name


class PartAttribute(models.Model):
    name = models.CharField(max_length=100, verbose_name='ویژگی اندازه‌گیری')

    class Meta:
        verbose_name = 'ویژگی اندازه‌گیری'
        verbose_name_plural = 'ویژگی‌های اندازه‌گیری'

    def __str__(self):
        return self.name


class MeasurementPreset(models.Model):
    clothing_part = models.ForeignKey(ClothesPart, on_delete=models.CASCADE, verbose_name='قطعه لباس')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name='سایز')

    class Meta:
        verbose_name = 'الگوی اندازه‌گیری'
        verbose_name_plural = 'الگوهای اندازه‌گیری'
        unique_together = ['clothing_part', 'size']

    def __str__(self):
        return f"{self.clothing_part} - {self.size}"


class MeasurementItem(models.Model):
    preset = models.ForeignKey(MeasurementPreset, on_delete=models.CASCADE, related_name='items',
                               verbose_name='الگوی اندازه‌گیری')
    attribute = models.ForeignKey(PartAttribute, on_delete=models.CASCADE, verbose_name='ویژگی')
    value = models.CharField(max_length=50, verbose_name='مقدار')

    class Meta:
        verbose_name = 'مقدار اندازه‌گیری'
        verbose_name_plural = 'مقادیر اندازه‌گیری'

    def __str__(self):
        return f"{self.preset} / {self.attribute}: {self.value}"


class ProductMeasurement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='measurements', verbose_name='محصول')
    preset = models.ForeignKey(MeasurementPreset, on_delete=models.CASCADE, verbose_name='الگوی اندازه‌گیری')

    class Meta:
        verbose_name = 'اتصال محصول به اندازه‌ها'
        verbose_name_plural = 'اتصالات محصولات به اندازه‌ها'
        unique_together = ['product', 'preset']

    def __str__(self):
        return f"{self.product} → {self.preset}"
