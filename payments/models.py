import random
from django.db import models
from orders.models import Order
from accounts.models import Customer

# Methods that require a phone number (mobile money wallets)
MOBILE_MONEY_METHODS = ('M-Pesa', 'Airtel Money', 'Mixx by Yas', 'HaloPesa')

# Methods that require bank account details (cards)
CARD_METHODS = ('Visa', 'MasterCard')

METHOD_CHOICES = [
    ('M-Pesa', 'M-Pesa'),
    ('Airtel Money', 'Airtel Money'),
    ('Mixx by Yas', 'Mixx by Yas'),
    ('HaloPesa', 'HaloPesa'),
    ('Visa', 'Visa'),
    ('MasterCard', 'MasterCard'),
]


def generate_control_number():
    """Generate a random 8-digit numeric control number, guaranteed unique."""
    while True:
        number = str(random.randint(10000000, 99999999))
        if not SavedPaymentMethod.objects.filter(ControlNumber=number).exists():
            return number


class SavedPaymentMethod(models.Model):
    """A customer's saved payment profile for a given method.

    Mobile money methods (M-Pesa, Airtel Money, Mixx by Yas, HaloPesa) need a
    PhoneNumber. Card methods (Visa, MasterCard) need a BankAccountNumber and
    BankName. Each saved method gets its own randomly generated ControlNumber,
    created once and reused on every future purchase with that method.
    """

    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payment_methods')
    PaymentMethod = models.CharField(max_length=50, choices=METHOD_CHOICES)

    # Mobile money detail
    PhoneNumber = models.CharField(max_length=20, blank=True)

    # Card detail
    BankAccountNumber = models.CharField(max_length=30, blank=True)
    BankName = models.CharField(max_length=100, blank=True)

    ControlNumber = models.CharField(max_length=8, unique=True, editable=False)
    IsDefault = models.BooleanField(default=False)
    CreatedDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-IsDefault', '-CreatedDate']

    def save(self, *args, **kwargs):
        if not self.ControlNumber:
            self.ControlNumber = generate_control_number()

        super().save(*args, **kwargs)

        # Enforce a single default per customer
        if self.IsDefault:
            SavedPaymentMethod.objects.filter(
                Customer=self.Customer
            ).exclude(pk=self.pk).update(IsDefault=False)

    @property
    def is_mobile_money(self):
        return self.PaymentMethod in MOBILE_MONEY_METHODS

    @property
    def is_card(self):
        return self.PaymentMethod in CARD_METHODS

    @property
    def masked_detail(self):
        """A short, display-safe summary of the saved detail."""
        if self.is_mobile_money:
            return self.PhoneNumber
        if self.BankAccountNumber:
            tail = self.BankAccountNumber[-4:]
            return f"{self.BankName} •••• {tail}"
        return ""

    def __str__(self):
        return f"{self.PaymentMethod} ({self.masked_detail}) - {self.Customer}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    Order = models.OneToOneField(Order, on_delete=models.CASCADE)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    PaymentMethod = models.CharField(max_length=50, choices=METHOD_CHOICES)
    SavedPaymentMethod = models.ForeignKey(
        SavedPaymentMethod, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments'
    )
    PaymentStatus = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    PaymentDate = models.DateTimeField(auto_now_add=True)
    TransactionReference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment for Order #{self.Order.id}"