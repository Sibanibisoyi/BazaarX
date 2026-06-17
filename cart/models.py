from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f"Cart of {self.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(default= 1)
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"