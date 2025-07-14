from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django.views.generic import ListView, DetailView
from .models import ProductVariant, Product, Color, Size, Category, ProductMeasurement
from .filters import ProductFilter
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Min, Max, Prefetch, F
from account.models import Partnership
from home.utils import set_discount_flags


class ProductVariantListView(ListView):
    model = Product
    template_name = 'products/products_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.prefetch_related('variants__color', 'variants__size')
        category_slug = self.request.GET.get('category')
        color_id = self.request.GET.get('color')
        query = self.request.GET.get('q')
        ordering = self.request.GET.get('ordering')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        if query:
            queryset = queryset.filter(title__icontains=query)

        if color_id and color_id != 'all':
            queryset = queryset.filter(variants__color_id=color_id)

        if ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-is_active')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        colors = cache.get('product_filter_colors')
        if not colors:
            colors = Color.objects.all()
            cache.set('product_filter_colors', colors, 3600)

        sizes = cache.get('product_filter_sizes')
        if not sizes:
            sizes = Size.objects.all()
            cache.set('product_filter_sizes', sizes, 3600)

        price_range = cache.get('product_filter_price_range')
        if not price_range:
            price_range = Product.objects.aggregate(min=Min('price'), max=Max('price'))
            cache.set('product_filter_price_range', price_range, 3600)
        context.update({
            'price_min': price_range['min'] or 0,
            'price_max': (price_range['max'] or 0) + 50000,
            'colors': colors,
            'sizes': sizes,
        })
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        code = self.kwargs.get('code')
        slug = self.kwargs.get('slug')
        return get_object_or_404(
            Product.objects.select_related(
                'category__sub_category__sub_category'
            ),
            code=code,
            slug=slug
        )

    def dispatch(self, request, *args, **kwargs):
        ref_code = request.GET.get('ref')
        if ref_code:
            request.session['ref_code'] = ref_code
            return redirect(request.path)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        partner = None
        if self.request.user.is_authenticated:
            try:
                partner = Partnership.objects.get(user=self.request.user, is_active=True)
            except Partnership.DoesNotExist:
                pass
        if partner:
            ref_link = self.request.build_absolute_uri() + f'?ref={partner.code}'
        else:
            ref_link = self.request.build_absolute_uri()
        product.views += 1
        product.save(update_fields=['views'])
        variants = product.variants.filter(is_active=True).select_related('color', 'size')
        measurements = ProductMeasurement.objects.filter(product=product).select_related(
            'preset__clothing_part',
            'preset__size'
        ).prefetch_related('preset__items__attribute')
        all_sizes = {v.size for v in variants}
        color_variant_map = {}
        color_size_map = {}

        for v in variants:
            color_variant_map.setdefault(v.color_id, v)
            color_size_map.setdefault(v.color_id, set()).add(v.size)

        gallery_images = [product.image.url] + [v.image.url for v in color_variant_map.values() if v.image]

        category_ancestors = []
        if product.category:
            category_ancestors = product.category.get_category_ancestors()
        similar = Product.objects.filter(category__in=category_ancestors).exclude(pk=product.pk)[:8]
        context['is_favorited'] = False
        if self.request.user.is_authenticated:
            context['is_favorited'] = product.wishlist_set.filter(user=self.request.user).exists()
        else:
            context['is_favorited'] = list(map(int, self.request.session.get('wishlist', [])))
        context.update({
            'ref_link': ref_link,
            'full_image_url': self.request.build_absolute_uri(product.image.url),
            'variants': variants,
            'all_sizes': all_sizes,
            'color_variants': color_variant_map.values(),
            'color_size_map': color_size_map,
            'gallery_images': gallery_images,
            'category_ancestors': category_ancestors,
            'product_measurements': measurements,
            'similar': similar,
            'partner': partner,
        })
        return context


def ajax_product_filter(request):
    queryset = Product.objects.prefetch_related('variants__color', 'variants__size')

    filtered = ProductFilter(request.GET, queryset=queryset).qs.distinct()
    search_query = request.GET.get('q', '').strip()
    if search_query:
        filtered = filtered.filter(title__icontains=search_query)
    ordering = request.GET.get('ordering')
    if ordering:
        filtered = filtered.order_by(F('is_active').desc(), ordering, '-created_at')
    else:
        filtered = filtered.order_by(F('is_active').desc(), '-created_at')

    paginator = Paginator(filtered, 28)
    page_obj = paginator.get_page(request.GET.get('page') or 1)
    set_discount_flags(page_obj.object_list)
    html = render_to_string('products/partials/_product_list.html', {'products': page_obj, 'page_obj': page_obj})
    return JsonResponse({'html': html, 'total_pages': paginator.num_pages, 'current_page': page_obj.number})



def get_variants(request):
    product_id = request.GET.get("product_id")
    size_id = request.GET.get("size_id")
    color_id = request.GET.get("color_id")

    if not product_id or not size_id:
        return JsonResponse({'success': False, 'error': 'missing product_id or size_id'}, status=400)

    variants = ProductVariant.objects.filter(
        product_id=product_id,
        size_id=size_id,
        is_active=True
    ).select_related("color")

    if not variants.exists():
        return JsonResponse({'success': False, 'error': 'no variants found'}, status=404)

    if color_id:
        variant = variants.filter(color_id=color_id).first()
        if not variant:
            return JsonResponse({'success': False, 'error': 'variant not found'}, status=404)
    else:
        variant = variants.first()

    colors_map = {}
    for v in variants:
        c = v.color
        if c.id not in colors_map:
            colors_map[c.id] = {
                'id': c.id,
                'title': c.title,
                'hex_color': c.hex_color,
                'image_url': v.image.url if v.image else ''
            }

    return JsonResponse({
        'success': True,
        'is_active': variant.is_active,
        'has_discount': variant.has_discount,
        'price': variant.price,
        'discounted_price': variant.get_discounted_price(),
        'discount': variant.discount,
        'stock': variant.stock,
        'main_image': variant.image.url if variant.image else '',
        'colors': list(colors_map.values())
    })


@require_GET
def search_suggestions_api(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({"categories": [], "products": []})

    matched_categories = Category.objects.filter(title__icontains=q).order_by('title')[:5]
    categories_data = [{
        "name": c.title,
        "url": f"/product/list/?category={c.slug}"
    } for c in matched_categories]

    matched_products = Product.objects.filter(title__icontains=q).order_by('title')[:4]
    products_data = [{
        "name": p.title,
        "url": p.get_absolute_url(),
        "image": p.image.url if p.image else ""
    } for p in matched_products]

    return JsonResponse({
        "categories": categories_data,
        "products": products_data,
    })


def category_view(request):
    categorya = Category.objects.prefetch_related('sub_category')
    return render(request, 'products/categories.html', {'categorya': categorya})
