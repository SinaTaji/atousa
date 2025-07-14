import django_filters
from django_filters import filters, NumberFilter, BaseInFilter
from .models import Product, Category


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method='filter_by_category')
    size = django_filters.NumberFilter(field_name='variants__size__id')
    color = django_filters.NumberFilter(field_name='variants__color__id')
    gender = django_filters.CharFilter(method='filter_gender')
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['color', 'material', 'gender', 'price__gt', 'price__lt', 'size', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queryset = self.queryset.order_by('-is_active')

    def filter_gender(self, queryset, name, value):
        if value in ['boys', 'girls']:
            return queryset.filter(gender__in=[value, 'unisex'])
        return queryset

    def filter_by_category(self, queryset, name, value):
        try:
            selected = Category.objects.get(slug=value)
            all_subcategories = selected.get_all_subcategories()
            categories = [selected] + all_subcategories
            return queryset.filter(category__in=categories).distinct()
        except Category.DoesNotExist:
            return queryset.none()
