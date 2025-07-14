from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from article.models import Article, ArticleCategory
from products.models import Product, Category


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ['categories_list_page', 'home', 'aboutus_page', 'contact_us_page', 'article_list_page',
                'product_list_page']

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.pub_date

    def location(self, obj):
        return obj.get_absolute_url()


class ArticleCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return ArticleCategory.objects.all()

    def location(self, obj):
        return reverse('article_list_page_filter', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.update_at
