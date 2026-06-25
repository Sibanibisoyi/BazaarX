from django.db import models
from users.models import CustomUser

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE) 
    seller      = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    discount    = models.IntegerField(default=0)
    stock       = models.IntegerField(default=0)
    image       = models.ImageField(upload_to='products/', blank=True, null = True)
    is_active   = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    featured_image = models.ImageField(upload_to='products/featured/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)
    

    def __str__(self):
        return f"Image for {self.product.name}"


