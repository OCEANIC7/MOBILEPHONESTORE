from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
]