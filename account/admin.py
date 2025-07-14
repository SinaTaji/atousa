from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Partnership, PartnerMonthlySet, Gift, Withdraw
from .forms import UserCreationForm, UserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone', 'is_active', 'is_active', 'is_superuser', 'is_staff', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('is_active',)

    fieldsets = [
        (None, {'fields': ('phone', 'password', 'is_active', 'is_superuser', 'is_staff')}),
    ]
    add_fieldsets = [
        (None, {'fields': ('phone', 'password1', 'password2')}),
    ]
    search_fields = ('phone',)
    ordering = ('phone',)
    filter_horizontal = []


@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'rank', 'sells', 'is_active', 'created_at')
    list_filter = ('is_active', 'rank')
    list_editable = ('is_active',)


@admin.register(PartnerMonthlySet)
class PartnerMonthlySetAdmin(admin.ModelAdmin):
    list_display = ('partner', 'month', 'sales_count', 'commission_monthly')
    list_filter = ('partner', 'month', 'sales_count')


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ('partner', 'title', 'percent', 'is_active', 'created_at')


@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'card', 'created_at', 'is_paid')
    list_filter = ('is_paid', 'created_at', 'user')
