from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, ProductVariant
from users.models import Address
from django.utils import timezone
from datetime import timedelta

# Create your models here.

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]
PAYMENT_METHOD_CHOICES = [
    ('razorpay', 'Online Payment (Razorpay)'),
    ('cod', 'Cash on Delivery'),
]

class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='razorpay')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)  # set when status → delivered
    cancellation_reason = models.TextField(blank=True, default='')  # filled when cancelled

    def __str__(self):
        return f"Order{self.id} by {self.user.username}"

    @property
    def return_deadline(self):
        """Returns the last date a return can be raised (10 days after delivery)."""
        if self.delivered_at:
            return self.delivered_at + timedelta(days=10)
        return None

    @property
    def is_returnable(self):
        """True if status is delivered AND within 10-day return window."""
        if self.status != 'delivered' or not self.delivered_at:
            return False
        return timezone.now() <= self.return_deadline
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        variant_str = f' [{self.variant.name}: {self.variant.value}]' if self.variant else ''
        return f"{self.quantity} * {self.product.name}{variant_str}"