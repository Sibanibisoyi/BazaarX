from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, ProductVariant

# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f"Cart of {self.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product', 'variant')

    def __str__(self):
        variant_str = f' [{self.variant.name}: {self.variant.value}]' if self.variant else ''
        return f"{self.quantity} x {self.product.name}{variant_str}"

    def effective_price(self):
        if self.variant and self.variant.price_override:
            return self.variant.price_override
        return self.product.price