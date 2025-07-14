from django.core.cache import cache
from .models import Footer


def footer(request):
    links = cache.get('footer_links')
    if not links:
        links = Footer.objects.filter(sub_links__isnull=True).prefetch_related('sub_links').all()
        cache.set('footer_links', links, 60 * 60)
    return {'links': links}
