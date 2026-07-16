from django import forms
from .models import Seller
from products.models import Product, ProductVariant

class SellerForm(forms.ModelForm):

    class Meta:
        model = Seller
        fields = ['shop_name', 'shop_description']

class ProductForm(forms.ModelForm):
    sizes = forms.CharField(
        max_length=255, 
        required=False, 
        help_text="Comma-separated sizes (e.g., S, M, L, XL). Stock will be set to product default.",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. S, M, L, XL'})
    )
    quantities = forms.CharField(
        max_length=255, 
        required=False, 
        help_text="Comma-separated quantities (e.g., 50ml, 100ml, 200g). Stock will be set to product default.",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 50ml, 100ml, 200g'})
    )

    class Meta:
        model = Product
        fields = ['name', 'slug', 'category', 'description',
                  'price', 'discount', 'stock', 'sizes', 'quantities', 'image', 'is_active', 'is_featured', 'featured_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            size_variants = self.instance.productvariant_set.filter(name__iexact='Size')
            if size_variants.exists():
                self.fields['sizes'].initial = ', '.join([v.value for v in size_variants])
            qty_variants = self.instance.productvariant_set.filter(name__iexact='Quantity')
            if qty_variants.exists():
                self.fields['quantities'].initial = ', '.join([v.value for v in qty_variants])