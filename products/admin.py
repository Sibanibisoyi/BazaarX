from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant
from .models import Review

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline, ProductImageInline]
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    search_fields = ('name', 'description')

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Review)