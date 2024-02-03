from django.urls import path, re_path
from . import views

urlpatterns = [
    path('success/', views.success, name="payment_success"),
]
