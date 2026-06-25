from django.contrib import admin
from .models import Payment, SavedPaymentMethod

admin.site.register(Payment)
admin.site.register(SavedPaymentMethod)