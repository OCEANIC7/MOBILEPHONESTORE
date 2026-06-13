from django.db import models
from orders.models import Order, ShippingZone

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('Not Eligible', 'Not Eligible'),
        ('Preparing', 'Preparing'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
    ]

    Order = models.OneToOneField(Order, on_delete=models.CASCADE)
    DeliveryAddress = models.TextField()
    ShippingZone = models.ForeignKey(ShippingZone, on_delete=models.SET_NULL, null=True)
    DeliveryStatus = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Eligible')

    def __str__(self):
        return f"Delivery for Order #{self.Order.id}"