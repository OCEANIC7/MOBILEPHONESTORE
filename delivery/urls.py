from django.urls import path
from . import views

urlpatterns = [
    path('delivery/', views.delivery_tracking, name='delivery_tracking'),
]