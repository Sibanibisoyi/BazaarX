from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from users.models import Address
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from utils.email_utils import send_order_confirmation_email
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
from users.utils import redeem_points
from users.utils import award_points
from decimal import Decimal


# Create your views here.
@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    if not items:
        return redirect('cart:cart_detail')
    address = Address.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)

    discount = 0
    if request.method == 'POST':
        points_to_redeem = int(request.POST.get('points_to_redeem', 0))
        if points_to_redeem > 0:
            success, message = redeem_points(request.user, points_to_redeem)
            if success:
                discount = points_to_redeem * 1  # 1 point = ₹1
                total -= discount
                messages.success(request, f'{points_to_redeem} points redeemed! ₹{discount} discount applied.')
            else:
                messages.error(request, message)

    return render(request, 'orders/checkout.html', {
        'items': items,
        'addresses': address,
        'total': total,
        'discount': discount,
    })



@login_required
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        discount = Decimal(request.POST.get('discount', '0'))
        address = get_object_or_404(Address, id=address_id)
        cart = Cart.objects.get(user=request.user)
        items = cart.cartitem_set.all()
        total = sum(item.product.price * item.quantity for item in items) - discount
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
        return redirect('orders:initiate_payment', order_id=order.id)

    
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

            # Award loyalty points after successful payment
            order = Order.objects.filter(user=request.user).order_by('-created_at').first()
            if order:
                award_points(request.user, order.total_price, order.id)

            messages.success(request, 'Payment successful')
            return redirect('orders:my_orders')

        except:
            messages.error(request, 'Payment verification failed')
            return redirect('orders:my_orders')



@login_required
def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.orderitem_set.all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 20)
    p.drawString(1*inch, 10*inch, "BazaarX Invoice")
    
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, 9.5*inch, f"Order ID: {order.id}")
    p.drawString(1*inch, 9.2*inch, f"Date: {order.created_at}")
    p.drawString(1*inch, 8.9*inch, f"Customer: {request.user.username}")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, 8.4*inch, "Items:")
    
    y = 8.1*inch
    p.setFont("Helvetica", 11)
    for item in items:
        p.drawString(1*inch, y, f"{item.product.name} x{item.quantity} - ₹{item.price}")
        y -= 0.3*inch
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, y - 0.2*inch, f"Total: ₹{order.total_price}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{order.id}.pdf'
    return response




