from django.urls import path
from . import views

urlpatterns = [
    path('payment/', views.payment, name='payment'),
    path('order-success/', views.order_success, name='order_success'),
    path('orders/', views.my_orders, name='my_orders'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),
]