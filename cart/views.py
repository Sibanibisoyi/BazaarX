from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem
from products.models import Product, ProductVariant
from coupons.models import Coupon

# Create your views here.
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    variant_id = request.POST.get('variant_id') or request.GET.get('variant_id')
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    # Check stock
    available_stock = variant.stock if variant else product.stock
    if available_stock <= 0:
        messages.error(request, 'Sorry, this item is out of stock.')
        return redirect('products:product_detail', slug=product.slug)

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, variant=variant
    )
    if not created:
        if item.quantity < available_stock:
            item.quantity += 1
            item.save()
        else:
            messages.warning(request, f'Maximum available quantity for this item is {available_stock}.')
    return redirect('cart:cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    total = sum(item.effective_price() * item.quantity for item in items)
    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            discount_amount = (total * coupon.discount) / 100
            discounted_total = total - discount_amount
        except Coupon.DoesNotExist:
            coupon = None
            discount_amount = 0
            discounted_total = total
    else:
        coupon = None
        discount_amount = 0
        discounted_total = total

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'coupon': coupon,
        'discount_amount': discount_amount,
        'discounted_total': discounted_total,
    })

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id = item_id)
    item.delete()
    return redirect('cart:cart_detail')


@login_required
def update_cart_view(request, item_id):
    item = get_object_or_404(CartItem, id = item_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
    return redirect('cart:cart_detail')


