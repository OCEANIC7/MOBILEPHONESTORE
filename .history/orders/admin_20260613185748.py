from django.contrib import admin
from .models import ShippingZone, Cart, CartItem, Order

admin.site.register(ShippingZone)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)