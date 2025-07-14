from django.contrib import admin
from .models import Order, OrderItem, UserAddress
from django.utils.timezone import localtime
import jdatetime


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('user', 'created_jalali', 'price_display', 'paid', 'address', 'shipping_method', 'code')
    list_filter = ('paid', 'shipping_method', 'code')

    def price_display(self, obj):
        return "{:,} تومان".format(obj.total_price) if obj.total_price else "-"

    price_display.short_description = 'قیمت'

    def created_jalali(self, obj):
        time = localtime(obj.updated)
        jtime = jdatetime.datetime.fromgregorian(datetime=time)
        return jtime.strftime('%Y/%m/%d - %H:%M:%S')  # تاریخ شمسی با ساعت دقیق

    created_jalali.short_description = 'تاریخ ثبت'


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'address', 'user')
