from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reports/', views.reports, name='reports'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
]