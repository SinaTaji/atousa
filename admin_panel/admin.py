from django.utils.timezone import localtime
import jdatetime
from django.contrib import admin
from .models import Stats, Notification


@admin.register(Stats)
class StatsAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'day', 'total_sales', 'total_orders')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_jalali', 'is_seen']
    list_filter = ['is_seen', 'created_at']
    search_fields = ['title', 'message']
    actions = ['mark_as_seen']

    def created_jalali(self, obj):
        time = localtime(obj.created_at)
        jtime = jdatetime.datetime.fromgregorian(datetime=time)
        return jtime.strftime('%Y/%m/%d - %H:%M:%S')

    created_jalali.short_description = 'تاریخ ثبت'

