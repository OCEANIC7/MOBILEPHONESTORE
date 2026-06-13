from django.db import models
from orders.models import Order

class Payment(models.Model):
    METHOD_CHOICES = [
        ('M-Pesa', 'M-Pesa'),
        ('Airtel Money', 'Airtel Money'),
        ('Mixx by Yas', 'Mixx by Yas'),
        ('HaloPesa', 'HaloPesa'),
        ('Visa', 'Visa'),
        ('MasterCard', 'MasterCard'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    Order = models.OneToOneField(Order, on_delete=models.CASCADE)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    PaymentMethod = models.CharField(max_length=50, choices=METHOD_CHOICES)
    PaymentStatus = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    PaymentDate = models.DateTimeField(auto_now_add=True)
    TransactionReference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment for Order #{self.Order.id}"