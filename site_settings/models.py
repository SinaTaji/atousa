from django.core.cache import cache
from django.db import models


class Footer(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    link = models.CharField(max_length=100, verbose_name="آدرس صفحه", null=True, blank=True)
    sub_links = models.ForeignKey('self', null=True, blank=True, related_name='sub_link', verbose_name="زیر دسته ها",
                                  on_delete=models.CASCADE)

    class Meta:
        verbose_name = "پاورقی"
        verbose_name_plural = "پاورقی ها"
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete("template.cache.footer_static")

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete("template.cache.footer_static")
