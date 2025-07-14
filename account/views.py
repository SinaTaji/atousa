import json
from .utils import update_partner_stats, promote_partner
import jdatetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from .models import WishList, Partnership, PartnerMonthlySet, Gift, Withdraw
from .forms import PartnershipForm, WithdrawForm
from products.models import Product
from .mixins import ActivePartnerRequiredMixin


def wish_list(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if not request.user.is_authenticated:
        wishlist = request.session.get('wishlist', [])
        product_id_str = str(product_id)
        if product_id_str in wishlist:
            wishlist.remove(product_id_str)
            status = 'removed'
        else:
            wishlist.append(product_id_str)
            status = 'added'
        request.session['wishlist'] = wishlist
        return JsonResponse({'status': status, "source": "session"})
    obj, created = WishList.objects.get_or_create(user=request.user, product_id=product_id)
    if not created:
        obj.delete()
        return JsonResponse({"status": "removed", "source": "db"})
    return JsonResponse({"status": "added", "source": "db"})


def wishlist_page(request):
    if request.user.is_authenticated:
        products = Product.objects.filter(wishlist__user=request.user)
    else:
        wishlist_ids = request.session.get('wishlist', [])
        products = Product.objects.filter(id__in=wishlist_ids)

    return render(request, 'account/wish_list.html', {
        'products': products
    })


class PartnerShipRegister(LoginRequiredMixin, View):
    template_name = 'account/partner_register.html'

    def get(self, request):
        user = request.user
        partner = Partnership.objects.filter(user=user).exists()
        if partner:
            return redirect('partner_dashboard_page')
        form = PartnershipForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PartnershipForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            user = request.user
            first_name = cd['first_name']
            last_name = cd['last_name']
            image = cd['image']
            exist = Partnership.objects.filter(user=user).exists()
            if exist:
                messages.error(request,
                               'کاربر گرامی شما قبلا ثبت نام کرده اید لطفا منتظر نتیجه بمانید')
                return redirect(reverse('user_panel_page'))
            from utils.telegram import notify_partner_register
            notify_partner_register(first_name=first_name, last_name=last_name)
            partner = Partnership(
                user=user,
                first_name=first_name,
                last_name=last_name,
                image=image,
            )
            partner.save()
            from admin_panel.utils import update_stats_on_partner_signup
            update_stats_on_partner_signup()
            messages.success(request, 'درخواست شما ثبت شد. نتیجه به ‌زودی از طریق صندوق پیام‌ها اطلاع ‌رسانی خواهد شد')
            return redirect(reverse('user_panel_page'))
        return render(request, self.template_name, {'form': form})


class PartnerPanelView(ActivePartnerRequiredMixin, TemplateView):
    template_name = 'account/partner_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partner = self.partner
        gifts_count = Gift.objects.filter(partner=partner, is_active=True).count()
        if partner.is_evaluation_due():
            latest_stat = PartnerMonthlySet.objects.filter(partner=partner).order_by('-created_at').first()
            if latest_stat:
                promote_partner(partner.user, latest_stat.monthly_sells)
            partner.reset_evaluation_timer()
            partner.create_monthly_record()

        today_jalali = jdatetime.date.today()
        year = today_jalali.year
        current_stat = PartnerMonthlySet.objects.filter(partner=partner).order_by('-created_at').first()
        MONTH_NAMES_FA = [
            "فروردین", "اردیبهشت", "خرداد",
            "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر",
            "دی", "بهمن", "اسفند"
        ]

        stats_qs = partner.monthly_stat.filter(year=year).order_by('month')
        stats_dict = {s.month: s for s in stats_qs}

        sales = []
        commission = []

        for month in range(1, 13):
            stat = stats_dict.get(month)
            if stat:
                sales.append(stat.sales_count)
                commission.append(float(stat.commission_monthly))
            else:
                sales.append(0)
                commission.append(0)
        context.update({
            'days_left': partner.days_left_to_evaluation(),
            'gifts_count': gifts_count,
            'partner': self.partner,
            'current_stat': current_stat,
            'chart_labels_json': json.dumps(MONTH_NAMES_FA),
            'sales_data_json': json.dumps(sales),
            'commission_data_json': json.dumps(commission),
        })

        return context


class PartnerGiftsView(ActivePartnerRequiredMixin, TemplateView):
    template_name = 'account/parts/partner_gifts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partner = self.partner
        all_gifts = Gift.objects.filter(partner=partner).order_by('-created_at')

        for gift in all_gifts:
            if gift.is_active and not gift.is_valid():
                gift.is_active = False
                gift.save(update_fields=['is_active'])

        active_gifts = [gift for gift in all_gifts if gift.is_valid()]
        expired_gifts = [gift for gift in all_gifts if not gift.is_valid()]

        context['active_gifts'] = active_gifts
        context['expired_gifts'] = expired_gifts
        return context


class WithdrawView(ActivePartnerRequiredMixin, View):
    template_name = 'account/parts/withdraw.html'

    def _render_form(self, request, form):
        user = request.user
        try:
            partner = Partnership.objects.get(user=user)
        except Partnership.DoesNotExist:
            messages.error(request, 'شما همکار نیستید!')
            return redirect('user_panel_page')

        withdraws = Withdraw.objects.filter(user=user).order_by('-created_at')
        progressing = [draw for draw in withdraws if not draw.is_paid]
        paid = [draw for draw in withdraws if draw.is_paid]

        context = {
            'form': form,
            'withdraws': withdraws,
            'progressing': progressing,
            'paid': paid,
            'partner': partner
        }
        return render(request, self.template_name, context)

    def get(self, request):
        form = WithdrawForm()
        return self._render_form(request, form)

    def post(self, request):
        form = WithdrawForm(request.POST)
        if form.is_valid():
            user = request.user
            cd = form.cleaned_data
            try:
                partner = Partnership.objects.get(user=user)
            except Partnership.DoesNotExist:
                messages.error(request, 'شما همکار نیستید!')
                return redirect('user_panel_page')
            commission_cc = partner.commission_can_clime
            withdraw_exist = Withdraw.objects.filter(user=user, is_paid=False).exists()
            if withdraw_exist:
                form.add_error('card', 'درخواست قبلی شما در حال بررسی است ')
                return self._render_form(request, form)
            card = cd.get('card')
            amount = cd.get('amount')
            if amount > commission_cc:
                form.add_error('amount', f'موجودی شما {commission_cc} است ')
                return self._render_form(request, form)
            from utils.telegram import notify_withdraw
            notify_withdraw(user=request.user, amount=amount, card=card)
            Withdraw.objects.create(
                user=user,
                card=card,
                amount=amount,
            )
            messages.success(request, 'درخواست برداشت شما ثبت شد و به زودی انجام خواهد شد')
            return redirect('partner_dashboard_page')

        return self._render_form(request, form)
