from django.contrib import messages
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from account.models import WishList
from orders.form import UserAddressForm
from orders.cart import Cart
from .forms import ContactUsForm
from .models import ContactUs, ReplyContact
from orders.models import UserAddress, Order, OrderItem
from .utils import update_order_status
from account.utils import is_partner
from django.core.cache import cache


def about_us(request):
    return render(request, 'about-contact-us/about_us.html')


def contact_us(request):
    return render(request, 'about-contact-us/contact_us.html')


def rules(request):
    return render(request, 'about-contact-us/term.html')


class ContactView(LoginRequiredMixin, View):
    template_name = 'about-contact-us/contact.html'

    def get(self, request):
        form = ContactUsForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = ContactUsForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            from utils.telegram import notify_contact_us
            notify_contact_us(user=request.user, contact=cd['ticket'], message=cd['text'])
            ContactUs.objects.create(
                user=request.user,
                ticket=cd['ticket'],
                text=cd['text'],
            )

            messages.success(request, 'تیکت شما برای پشتیبانی ارسال شد')
            return redirect(reverse('contact_page'))
        return render(request, self.template_name, {'form': form})


class UserPanelView(LoginRequiredMixin, View):
    template_name = 'about-contact-us/user_panel.html'

    def get(self, request):
        user = request.user
        message = (
                ContactUs.objects.filter(user=user).count() +
                ReplyContact.objects.filter(user=user).count()
        )
        addresses = UserAddress.objects.filter(user=user).count()
        wishes = WishList.objects.filter(user=user).count()
        orders = Order.objects.filter(user=user).count()
        partner = is_partner(request)
        context = {'user': user, 'message': message, 'addresses': addresses, 'wishes': wishes, 'orders': orders,
                   'partner': partner}
        return render(request, self.template_name, context)


class UserContactListView(LoginRequiredMixin, ListView):
    model = ContactUs
    template_name = 'about-contact-us/contact-lists.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        user = self.request.user
        ReplyContact.objects.filter(user=user, is_read=False).update(is_read=True)
        return ContactUs.objects.filter(user=user).prefetch_related(
            Prefetch('reply_contact', queryset=ReplyContact.objects.select_related('user'))
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        contacts = ContactUs.objects.filter(user=user).prefetch_related(
            Prefetch('reply_contact', queryset=ReplyContact.objects.select_related('user'))
        )

        replies = ReplyContact.objects.filter(user=user, reply_to__isnull=True)

        combined = []

        for contact in contacts:
            combined.append({
                'type': 'contact',
                'object': contact,
                'created_at': contact.created_at
            })
            for reply in contact.reply_contact.all():
                combined.append({
                    'type': 'reply',
                    'object': reply,
                    'created_at': reply.created_at
                })

        for reply in replies:
            combined.append({
                'type': 'standalone',
                'object': reply,
                'created_at': reply.created_at
            })

        context['contacts'] = sorted(combined, key=lambda x: x['created_at'], reverse=True)
        return context


class UserAddressView(LoginRequiredMixin, View):
    template_name = 'about-contact-us/user_address.html'

    def get(self, request):
        user = request.user
        addresses = UserAddress.objects.filter(user=user)

        address_form = UserAddressForm()
        context = {
            'address_form': address_form,
            'addresses': addresses,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        address_form = UserAddressForm(request.POST)

        if address_form.is_valid():
            cd = address_form.cleaned_data
            user = request.user
            address = UserAddress.objects.filter(
                user=user,
                province=cd['province'],
                city=cd['city'],
                address=cd['address'],
                postal_code=cd['postal_code'],
                phone=cd['phone']
            ).first()
            if not address:
                address = UserAddress.objects.create(
                    user=user,
                    first_name=cd['first_name'],
                    last_name=cd['last_name'],
                    province=cd['province'],
                    city=cd['city'],
                    address=cd['address'],
                    postal_code=cd['postal_code'],
                    phone=cd['phone'],
                )
            messages.success(request, 'آدرس شما با موفقیت ثبت شد')
            return redirect(reverse('user_address_page'))
        addresses = UserAddress.objects.filter(user=request.user)
        context = {
            'address_form': address_form,
            'addresses': addresses,
        }

        return render(request, self.template_name, context=context)


class UserOrdersView(View):
    template_name = 'about-contact-us/user_orders.html'

    def get(self, request):
        orders = list(Order.objects.filter(user=request.user, paid=True).order_by('-updated'))

        orders_packing = 0
        orders_sending = 0
        orders_finished = 0

        for order in orders:
            update_order_status(order)
            if not order.get_in_post and not order.finished:
                orders_packing += 1
            if order.get_in_post and not order.finished:
                orders_sending += 1
            if order.finished and not order.get_in_post:
                orders_finished += 1

        context = {
            'orders_sending': orders_sending,
            'orders_packing': orders_packing,
            'orders_finished': orders_finished,
        }
        return render(request, 'about-contact-us/user_orders.html', context)


class UserOrdersAjaxView(View):
    def get(self, request, status):
        if status == 'cart':
            cart = Cart(request)
            return render(request, 'partial/order_list_partial.html', {'cart': cart, 'status': status})
        status_map = {
            'packing': lambda o: o.paid and not o.get_in_post and not o.finished,
            'sending': lambda o: o.paid and o.get_in_post and not o.finished,
            'finished': lambda o: o.paid and o.finished and not o.get_in_post,
        }

        if status not in status_map:
            raise Http404()

        orders = list(Order.objects
                      .filter(user=request.user, paid=True)
                      .select_related('address')
                      .prefetch_related(Prefetch('items', queryset=OrderItem.objects.select_related('product')))
                      .order_by('-updated'))

        filtered_orders = [o for o in orders if status_map[status](o)]

        paginator = Paginator(filtered_orders, 5)
        page_number = request.GET.get('page', 1)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(request, 'partial/order_list_partial.html', {
            'orders': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'status': status,
        })


def get_user_counts(request):
    if not request.user.is_authenticated:
        return JsonResponse({'wishlist_count': 0, 'messages_count': 0})

    wishlist_count = WishList.objects.filter(user=request.user).count()
    messages_count = ReplyContact.objects.filter(user=request.user, is_read=False).count()

    return JsonResponse({
        'wishlist_count': wishlist_count,
        'messages_count': messages_count,
    })
