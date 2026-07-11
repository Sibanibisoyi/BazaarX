from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Coupon(models.Model):
    code           = models.CharField(max_length=20, unique=True)
    discount       = models.IntegerField(help_text='Percentage discount (e.g. 10 for 10%)')
    valid_from     = models.DateTimeField()
    valid_to       = models.DateTimeField()
    is_active      = models.BooleanField(default=True)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses       = models.PositiveIntegerField(
        default=0,
        help_text='Maximum total redemptions allowed (0 = unlimited)'
    )
    times_used     = models.PositiveIntegerField(default=0, editable=False)
    used_by        = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.code

    def is_valid_for_user(self, user):
        """Return True if this coupon can still be used right now by this user."""
        now = timezone.now()
        if not self.is_active:
            return False, 'This coupon is no longer active.'
        if now < self.valid_from or now > self.valid_to:
            return False, 'This coupon has expired or is not yet active.'
        if self.max_uses > 0 and self.times_used >= self.max_uses:
            return False, 'This coupon has reached its maximum number of uses.'
        if self.used_by.filter(pk=user.pk).exists():
            return False, 'You have already used this coupon.'
        return True, ''

    def mark_used(self, user):
        """Atomically increment the usage counter and record the user."""
        Coupon.objects.filter(pk=self.pk).update(times_used=models.F('times_used') + 1)
        self.used_by.add(user)