from django.urls import path
from .Views import Cart_views, CreateOrderView, PaymentView, views

app_name = 'orders'
urlpatterns = [
    # Cart section Views
    path('add-to-cart-ajax/', Cart_views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('increase/', Cart_views.increase_quantity, name='cart_increase'),
    path('decrease/', Cart_views.decrease_quantity, name='cart_decrease'),
    path('del/order/', Cart_views.remove_from_cart, name='cart_del'),

    # Create order Views
    path('set-shipping-method/', CreateOrderView.set_shipping_method, name='set_shipping_method'),
    path('create-order/', CreateOrderView.create_order, name='cart_information'),

    # Orders Views
    path('detail/', views.OrderDetail.as_view(), name='cart_detail_page'),
    path('information/', views.InformationView.as_view(), name='cart_information_page'),
    path('payment/', views.PaymentView.as_view(), name='cart_payment_page'),
    path('apply-gift-code/', views.ApplyGiftCodeAjaxView.as_view(), name='apply_gift_code_ajax'),

    # PaymentViews
    path('pay/<int:order_id>/', PaymentView.order_payment_request, name='order_payment'),
    path('verify/', PaymentView.order_payment_verify, name='order_payment_verify'),
    path('success-payment/', PaymentView.payment_success, name='success_payment_page'),
    path('faild-payment/', PaymentView.payment_faild, name='faild_payment_page'),
]
