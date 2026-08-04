from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, ProductVariant
from users.models import Address
from django.utils import timezone
from datetime import timedelta

class OrderTracking(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order} - {self.status}"

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

    @property
    def pending_tracked_at(self):
        tracking = self.ordertracking_set.filter(status='pending').first()
        return tracking.created_at if tracking else None

    @property
    def confirmed_tracked_at(self):
        tracking = self.ordertracking_set.filter(status='confirmed').first()
        return tracking.created_at if tracking else None

    @property
    def shipped_tracked_at(self):
        tracking = self.ordertracking_set.filter(status='shipped').first()
        return tracking.created_at if tracking else None

    @property
    def delivered_tracked_at(self):
        tracking = self.ordertracking_set.filter(status='delivered').first()
        return tracking.created_at if tracking else None

    @property
    def cancelled_tracked_at(self):
        tracking = self.ordertracking_set.filter(status='cancelled').first()
        return tracking.created_at if tracking else None

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            try:
                old_order = Order.objects.get(pk=self.pk)
                old_status = old_order.status
            except Order.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        if is_new or self.status != old_status:
            OrderTracking.objects.create(order=self, status=self.status)
            try:
                from extras.models import Notification
                if self.status == 'pending':
                    Notification.objects.create(
                        user=self.user,
                        message=f"Your order #{self.id} has been placed successfully.",
                        notification_type='order'
                    )
                elif self.status == 'confirmed':
                    Notification.objects.create(
                        user=self.user,
                        message=f"Your order #{self.id} has been confirmed and is being processed.",
                        notification_type='order'
                    )
                elif self.status == 'shipped':
                    Notification.objects.create(
                        user=self.user,
                        message=f"Your order #{self.id} has been shipped. It's on its way!",
                        notification_type='order'
                    )
                elif self.status == 'delivered':
                    Notification.objects.create(
                        user=self.user,
                        message=f"Your order #{self.id} has been delivered. Thank you for shopping with BazaarX!",
                        notification_type='order'
                    )
                elif self.status == 'cancelled':
                    reason_str = f" Reason: {self.cancellation_reason}" if self.cancellation_reason else ""
                    Notification.objects.create(
                        user=self.user,
                        message=f"Your order #{self.id} has been cancelled.{reason_str}",
                        notification_type='order'
                    )
            except Exception:
                pass
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ], default='pending')
    tracking_number = models.CharField(max_length=100, blank=True, default='')
    shipped_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        variant_str = f' [{self.variant.name}: {self.variant.value}]' if self.variant else ''
        return f"{self.quantity} * {self.product.name}{variant_str}"