import threading
from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.contrib import messages
from account.models import User
from utils.utils import GenerateAndSendOtp, GetAndCheckOtp
from .forms import LoginForm
from django.core.cache import cache
from .mixins import RedirectAuthenticatedUserMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from admin_panel.utils import update_stats_on_user_signup


class VerifyOtpView(RedirectAuthenticatedUserMixin, View):
    def get(self, request: HttpRequest):
        context = request.session.get('otp_contex')
        if not context:
            return redirect('user_login_page')
        return render(request, 'authentication/verify_otp.html')

    def post(self, request: HttpRequest):

        context = request.session.get('otp_contex')
        if not context:
            return render(request, 'authentication/verify_otp.html',
                          {'error': 'اطلاعات شما یافت نشد. لطفاً مجدداً تلاش کنید.'})

        phone = context['phone']
        cash_kay = f'{phone}'

        try:
            if GetAndCheckOtp(request, phone):
                user_data = cache.get(cash_kay)
                if not user_data:
                    raise ValidationError('اطلاعات شما منقضی شده است لطفا دوباره ثبت نام کنید')
                phone = user_data['phone']
                if User.objects.filter(phone=phone).exists():
                    user = User.objects.get(phone=phone)
                    login(request, user)
                    messages.success(request, 'خوش آمدید')
                    next_url = request.POST.get('next', '/')
                    if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                        next_url = '/'
                    return redirect(next_url)
                from utils.telegram import notify_register
                notify_register(user=phone)
                user = User.objects.create_user(phone, )
                update_stats_on_user_signup()
                login(request, user)
                del request.session['otp_contex']
                cache.delete(cash_kay)
                messages.success(request, 'خوش آمدید')
                next_url = request.session.get('next_url', '/')
                if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                    next_url = '/'
                return redirect(next_url)
        except ValidationError as e:
            return render(request, 'authentication/verify_otp.html', {'error': e.messages[0]})


class resend_otp(RedirectAuthenticatedUserMixin, View):
    def get(self, request: HttpRequest):
        context = request.session.get('otp_contex')
        if not context:
            return redirect(reverse('user_login_page'))
        phone = context['phone']

        cache_key = f'otp:{phone}'
        otp = cache.get(cache_key)

        try:
            if not otp:
                threading.Thread(target=GenerateAndSendOtp, args=(phone,)).start()
                messages.success(request, 'کد جدید برای شما ارسال شد')
                return redirect(reverse('verify_otp_page', ))
            raise ValidationError('کد شما هنوز منقضی نشده است')
        except ValidationError as e:
            return render(request, 'authentication/verify_otp.html', {'error': e.messages[0]})


class LoginView(RedirectAuthenticatedUserMixin, View):

    def get(self, request: HttpRequest):
        form = LoginForm()
        context = {'form': form}
        return render(request, 'authentication/login.html', context)

    def post(self, request: HttpRequest):
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                cd = form.cleaned_data
                phone = cd.get('phone')

                cash_kay = f'{phone}'
                cache.set(cash_kay, {'phone': phone}, timeout=300)
                request.session['next_url'] = request.POST.get('next', '/')
                request.session['otp_contex'] = {
                    'phone': phone,
                }
                threading.Thread(target=GenerateAndSendOtp, args=(phone,)).start()
                messages.success(request, 'کد فعال سازی برای شما ارسال شد')
                return redirect(reverse('verify_otp_page'))
            except ValidationError as e:
                context = {'form': form, 'error': e.messages[0]}
                return render(request, 'authentication/login.html', context)
        context = {'form': form}
        return render(request, 'authentication/login.html', context)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        logout(request)
        messages.error(request, 'شما از حساب خود خارج شدید')
        return redirect(reverse('home'))
