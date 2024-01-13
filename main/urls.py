from django.urls import path
from . import views

urlpatterns = [
  path('',views.home, name="home"),
  path('otp/', views.otp , name="otp"),
  path('verify/', views.sendOtp, name='send_otp'),
  path('submit/', views.verify_otp, name='verify_otp'),
  path('register/', views.savedata, name='register'),
  path('order-summary/', views.order_summary, name='order_summary'),
]
