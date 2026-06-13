from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE)
    PhoneNumber = models.CharField(max_length=20)
    Address = models.TextField(blank=True)

    def __str__(self):
        return self.User.username