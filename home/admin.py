from django.contrib import admin
from .models import Banner


@admin.register(Banner)
class BannersAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_editable = ('is_active',)
