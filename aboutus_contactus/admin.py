import jdatetime
from django.contrib import admin
from django.utils.timezone import localtime
from .models import ReplyContact, ContactUs


class ReplyContactInline(admin.TabularInline):
    model = ReplyContact
    extra = 1
    readonly_fields = ['created_jalali']

    def created_jalali(self, obj):
        time = localtime(obj.created_at)
        jtime = jdatetime.datetime.fromgregorian(datetime=time)
        return jtime.strftime('%Y/%m/%d - %H:%M:%S')

    created_jalali.short_description = 'تاریخ ثبت'


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['user', 'ticket', 'answered', 'created_jalali']
    inlines = [ReplyContactInline]
    readonly_fields = ['created_jalali']

    def created_jalali(self, obj):
        time = localtime(obj.created_at)
        jtime = jdatetime.datetime.fromgregorian(datetime=time)
        return jtime.strftime('%Y/%m/%d - %H:%M:%S')

    created_jalali.short_description = 'تاریخ ثبت'
