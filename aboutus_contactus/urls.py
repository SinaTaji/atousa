from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about_us, name='aboutus_page'),
    path('rules/', views.rules, name='rules_page'),
    path('contact/', views.contact_us, name='contact_us_page'),
    path('send-contact/', views.ContactView.as_view(), name='contact_page'),
    path('user-panel/', views.UserPanelView.as_view(), name='user_panel_page'),
    path('my-tickets/', views.UserContactListView.as_view(), name='user_tickets_page'),
    path('my-address/', views.UserAddressView.as_view(), name='user_address_page'),
    path('my-orders/', views.UserOrdersView.as_view(), name='user_orders_page'),
    path('ajax/orders/<str:status>/', views.UserOrdersAjaxView.as_view(), name='ajax-orders'),
    path('ajax/user-counts/', views.get_user_counts, name='get_user_counts')
]
