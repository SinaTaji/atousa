from django.contrib import admin
from django.db.models import Count

from .models import Category, Size, Color, Product, ProductVariant, ProductMeasurement, MeasurementPreset, \
    PartAttribute, ClothesPart, MeasurementItem


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('color', 'size', 'price', 'discount', 'has_discount', 'stock', 'image')


class ProductMeasurementInline(admin.TabularInline):
    model = ProductMeasurement
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price_display', 'discount', 'has_discount', 'total_stock', 'created_at']
    list_filter = ['category', 'gender', 'material', 'has_discount']
    search_fields = ['title', 'description', 'model']
    inlines = [ProductVariantInline, ProductMeasurementInline]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['code', 'created_at', 'updated_at', 'total_stock']
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'image', 'model', 'description', 'material', 'gender', 'age')
        }),
        ('قیمت و تخفیف', {
            'fields': ('price', 'discount', 'has_discount', 'discount_expiry')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('code', 'views', 'is_active', 'created_at', 'updated_at', 'total_stock')
        }),
    )

    def price_display(self, obj):
        return "{:,} تومان".format(obj.price) if obj.price else "-"

    price_display.short_description = 'قیمت'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'sub_category', 'is_active']
    search_fields = ['title']
    list_filter = ['is_active']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['title', 'hex_color']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['title', 'age_min', 'age_max']


@admin.register(ClothesPart)
class ClothesPartAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(PartAttribute)
class PartAttributeAdmin(admin.ModelAdmin):
    list_display = ['name']


class MeasurementItemInline(admin.TabularInline):
    model = MeasurementItem
    extra = 1


@admin.register(MeasurementPreset)
class MeasurementPresetAdmin(admin.ModelAdmin):
    list_display = ['clothing_part', 'size']
    inlines = [MeasurementItemInline]


@admin.register(ProductMeasurement)
class ProductMeasurementAdmin(admin.ModelAdmin):
    list_display = ['product', 'preset']
