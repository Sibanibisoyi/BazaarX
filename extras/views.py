from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from products.models import Product
from django.contrib import messages
from django.utils import timezone
from .models import Wishlist, FlashSale

# Create your views here.
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id = product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    

    if created:
        messages.success(request, 'Added to wishlist')
    else:
        messages.info(request, 'Already in wishlist')
    return redirect('products:product_detail', slug=product.slug)

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()
    messages.success(request, 'Removed from wishlist')
    return redirect('extras:wishlist_detail')


@login_required
def wishlist_detail(request):
    items=Wishlist.objects.filter(user=request.user)

    return render(request, 'extras/wishlist.html',{
         'items' : items,
    })



def flash_sale(request):
    now = timezone.now()
    sales = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    )
    return render(request,'extras/flash_sale.html',{
        'sales' : sales,
    })





