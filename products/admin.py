from django.contrib import admin
from .models import Category, Product, ProductImage
from .models import Review
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Review)