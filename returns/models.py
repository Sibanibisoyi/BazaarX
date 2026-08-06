from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order
from django.utils import timezone

# Create your models here.

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

REFUND_METHOD_CHOICES = [
    ('wallet', 'BazaarX Wallet'),
    ('original', 'Original Payment Source'),
    ('cod_wallet', 'Wallet (COD Order)'),
]

class ReturnRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    refund_method = models.CharField(max_length=20, choices=REFUND_METHOD_CHOICES, blank=True, null=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Return for Order #{self.order.id}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            try:
                old_req = ReturnRequest.objects.get(pk=self.pk)
                old_status = old_req.status
            except ReturnRequest.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        if not is_new and self.status != old_status:
            try:
                from extras.models import Notification
                if self.status == 'approved':
                    method_label = self.get_refund_method_display() if self.refund_method else 'wallet'
                    Notification.objects.create(
                        user=self.user,
                        message=f"Your return request for Order #{self.order.id} has been approved. Refund of ₹{self.order.total_price} will be credited to your {method_label} within 5–7 business days.",
                        notification_type='return'
                    )
                elif self.status == 'rejected':
                    Notification.objects.create(
                        user=self.user,
                        message=f"Your return request for Order #{self.order.id} has been rejected.",
                        notification_type='return'
                    )
            except Exception:
                pass



    