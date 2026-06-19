from django.db import models

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique = True)
    discount = models.IntegerField()
    valid_from = models.DateTimeField()
    valid_to   = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    minimum_amount = models.DecimalField(max_digits = 10, decimal_places =2, default=0)
    def __str__(self):
        return self.code