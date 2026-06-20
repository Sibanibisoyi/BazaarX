from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product


# Create your models here.
class Wishlist(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
class FlashSale(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=10,decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"Flash Sale - {self.product.name}"