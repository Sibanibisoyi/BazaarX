from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

class Seller(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=200)
    shop_description = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name
