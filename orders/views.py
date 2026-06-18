from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from users.models import Address

# Create your views here.
@login_required
def checkout(request):
    cart , created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    if not items:
        return redirect('cart:cart_detail')
    address = Address.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'orders/checkout.html', {
    'items': items,
    'addresses': address,
    'total': total,
})

@login_required
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id)
        cart = Cart.objects.get(user=request.user)
        items = cart.cartitem_set.all()
        total = sum(item.product.price * item.quantity for item in items)
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total
        )
        
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()
        cart.cartitem_set.all().delete()

        return redirect('orders:order_confirmation', order_id=order.id)
    
    else:
        return redirect('checkout')
    
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order ,id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order,id=order_id, user=request.user)
    items = order.orderitem_set.all()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items,
    })


