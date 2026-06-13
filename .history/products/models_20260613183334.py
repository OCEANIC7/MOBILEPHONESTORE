from django.db import models

class Brand(models.Model):
    BrandName = models.CharField(max_length=100)
    BrandLogo = models.ImageField(upload_to='brands/')

    def __str__(self):
        return self.BrandName


class Product(models.Model):
    ProductName = models.CharField(max_length=200)
    Brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Description = models.TextField()
    Features = models.TextField()
    ProductImage = models.ImageField(upload_to='products/')
    StockQuantity = models.PositiveIntegerField(default=0)
    DateAdded = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-DateAdded']  # Newest first

    def __str__(self):
        return self.ProductName