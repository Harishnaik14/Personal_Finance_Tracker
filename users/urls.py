from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('settings/', views.settings_view, name='settings'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
]
