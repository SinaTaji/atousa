from django.urls import path
from . import views

urlpatterns = [
    path('favorite/toggle/<int:product_id>/', views.wish_list, name='toggle_favorite'),
    path('wishlist/', views.wishlist_page, name='wish_list_page'),
    path('partner-ship/', views.PartnerShipRegister.as_view(), name='partner_register_page'),
    path('dashboard/', views.PartnerPanelView.as_view(), name='partner_dashboard_page'),
    path('gift-box/', views.PartnerGiftsView.as_view(), name='partner_gifts_page'),
    path('withdraw/', views.WithdrawView.as_view(), name='partner_withdraw_page'),
]
