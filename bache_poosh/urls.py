import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from home.views import robots_txt
from django.contrib.sitemaps.views import sitemap
from home.site_map import StaticViewSitemap, ProductSitemap, ArticleSitemap, ArticleCategorySitemap
sitemaps = {
    'products': ProductSitemap,
    'categories': StaticViewSitemap,
    'articles': ArticleSitemap,
    'articles_cat': ArticleCategorySitemap,
}
urlpatterns = [
      path('robots.txt', robots_txt, name='robots_txt'),
      path('atousa/admin/panel/sina1234/', admin.site.urls),
      path('atousa/admin/panel/stats/', include('admin_panel.urls')),
      path('', include('home.urls')),
      path('user/', include('authentication.urls')),
      path('product/', include('products.urls')),
      path('cart/', include('orders.urls')),
      path('account/', include('account.urls')),
      path('us/', include('aboutus_contactus.urls')),
      path('article/', include('article.urls')),
      path('__debug__/', include(debug_toolbar.urls)),
      path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
