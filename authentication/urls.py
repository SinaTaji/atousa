from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='user_login_page'),
    path('logout/', views.LogoutView.as_view(), name='user_logout'),
    path('verify/', views.VerifyOtpView.as_view(), name='verify_otp_page'),
    path('resend_otp/', views.resend_otp.as_view(), name='resend_otp'),
]
