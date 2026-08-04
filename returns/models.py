from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

# Create your models here.

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

class ReturnRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
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
                    Notification.objects.create(
                        user=self.user,
                        message=f"Your return request for Order #{self.order.id} has been approved. Refund of ₹{self.order.total_price} credited to your wallet.",
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



    