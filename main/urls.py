from django.urls import path
from . import views

urlpatterns = [
  path('',views.home, name="home"),
  path('otp/', views.otp , name="otp"),
  path('submit/', views.sendOtp, name='send_otp'),
  path('order-summary/', views.order_summary, name='order_summary'),
]
