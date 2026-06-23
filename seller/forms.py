from django import forms
from .models import Seller
from products.models import Product

class SellerForm(forms.ModelForm):

    class Meta:
        model = Seller
        fields = ['shop_name', 'shop_description']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'category', 'description',
                  'price', 'discount', 'stock', 'image', 'is_active', 'is_featured', 'featured_image']
        