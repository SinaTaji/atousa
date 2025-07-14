from django.core.cache import cache
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان بنر')
    image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='banners/home/',
        processors=[ResizeToFill(1920, 460)],
        format='WEBP',
        options={'quality': 100}
    )
    mobile_image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='banners/home/mobile/',
        processors=[ResizeToFill(1050, 500)],
        format='WEBP',
        options={'quality': 100},verbose_name='تصویر برای موبایل'
    )
    url = models.CharField(max_length=100, null=True, blank=True, verbose_name='آدرس صفحه')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'بنر'
        verbose_name_plural = 'بنرها'
        ordering = ['title']
        db_table = 'banners'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('homepage_banners')

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete('homepage_banners')
