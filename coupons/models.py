from django.db import models
from django.conf import settings

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique = True)
    discount = models.IntegerField()
    valid_from = models.DateTimeField()
    valid_to   = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    minimum_amount = models.DecimalField(max_digits = 10, decimal_places =2, default=0)
    used_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    def __str__(self):
        return self.code