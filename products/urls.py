from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ProductVariantListView.as_view(), name='product_list_page'),
    path('categories/', views.category_view, name='categories_list_page'),
    path('ajax/filter-products/', views.ajax_product_filter, name='ajax_filter_products'),
    path('<int:code>/<str:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('get-variants/', views.get_variants, name='get_variants'),
    path('ajax/search-suggestions/', views.search_suggestions_api, name='search_suggestions'),
]
