from django.db import models
from accounts.models import Customer
from products.models import Product

class ShippingZone(models.Model):
    LocationName = models.CharField(max_length=100)
    DeliveryCost = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.LocationName


class Cart(models.Model):
    Customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.Customer}"


class CartItem(models.Model):
    Cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.Quantity} x {self.Product.ProductName}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Awaiting Payment', 'Awaiting Payment'),
        ('Paid', 'Paid'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    ProductTotal = models.DecimalField(max_digits=10, decimal_places=2)
    ShippingCost = models.DecimalField(max_digits=8, decimal_places=2)
    GrandTotal = models.DecimalField(max_digits=10, decimal_places=2)
    OrderStatus = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Awaiting Payment')
    OrderDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.Customer}"