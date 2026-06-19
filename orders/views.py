from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from users.models import Address
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


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

@login_required
def initiate_payment(request, order_id):
    order = get_object_or_404(Order ,id=order_id, user=request.user)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = order.total_price * 100
    razorpay_order = client.order.create({
        'amount': int(amount),
            'currency': 'INR',
            'payment_capture': 1
        })
    return render(request, 'orders/payment.html', {
    'order': order,
    'razorpay_order': razorpay_order,
    'key_id': settings.RAZORPAY_KEY_ID,
})


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            messages.success(request, 'Payment successful')
            return redirect('orders:my_orders')

        except:
            messages.error(request, 'Payment verification failed')
            return redirect('orders:my_orders')
