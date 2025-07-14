from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django_jalali.db import models as jmodels


class ArticleCategory(models.Model):
    title = models.CharField(max_length=100, verbose_name='دسته بندی ', db_index=True)
    slug = models.CharField(max_length=100, verbose_name='اسلاگ', null=True, blank=True, db_index=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'article_category'
        verbose_name = 'دسته بندی مقاله'
        verbose_name_plural = 'دسته بندی مقالات'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class Article(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان مقاله', db_index=True)
    short_desc = models.CharField(max_length=200, verbose_name='توضیح کوتاه')
    image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='article/base/',
        processors=[ResizeToFill(365, 240)],
        format='WEBP',
        options={'quality': 100}
    )
    big_image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='article/big/',
        processors=[ResizeToFill(1400, 500)],
        format='WEBP',
        options={'quality': 100}
    )
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE, verbose_name='دسته بندی مقاله ',
                                 related_name='articles', null=True, blank=True)
    slug = models.CharField(max_length=100, verbose_name='اسلاگ', null=True, blank=True, db_index=True)
    pub_date = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ انتشار')
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید ها")

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article_detail_page', args=[self.slug])


class ArticlePart(models.Model):
    Article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='مقاله اصلی',
                                related_name='article_parts')
    title = models.CharField(max_length=100, verbose_name="عنوان بخش")
    desc = models.TextField(verbose_name="متن بخش")
    image = ProcessedImageField(
        null=True,
        blank=True,
        upload_to='article/detail/',
        processors=[ResizeToFill(400, 252)],
        format='WEBP',
        options={'quality': 100}
    )
    part = models.PositiveIntegerField(default=1, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ['-part']
        db_table = 'article_parts'
        verbose_name = 'تکه های مقاله'
        verbose_name_plural = 'تکه های مقالات'

    def __str__(self):
        return self.Article.title
