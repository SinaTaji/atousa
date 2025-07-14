from django.urls import path
from . import views

urlpatterns = [
    path('stats/daily/', views.daily_sales_current_month, name='daily_sales_last_7_days'),
    path('stats/monthly/', views.monthly_sales_current_year, name='monthly_sales_current_year'),
    path('stats/yearly/', views.yearly_sales, name='yearly_sales'),
]
