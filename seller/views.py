from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from .models import Seller
from .forms import SellerForm, ProductForm
from products.models import Product, Category
from orders.models import Order, OrderItem


# Create your views here.
@login_required
def seller_register(request):
    if Seller.objects.filter(user=request.user).exists():
        return redirect('seller:seller_dashboard')
    if request.method == 'POST':
        form = SellerForm(request.POST)
        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            seller.save()
            messages.success(request, 'Registration submitted for approval')
            return redirect('products:home')
    else:
        form = SellerForm()
    return render(request, 'seller/register.html', {'form': form})

@login_required
def seller_dashboard(request):
    seller = get_object_or_404(Seller, user=request.user)
    products = Product.objects.filter(seller=request.user)

    # Basic Analytics
    order_items = OrderItem.objects.filter(product__seller=request.user, order__status__in=['confirmed', 'shipped', 'delivered'])
    total_sales = order_items.count()
    total_revenue = sum(item.price * item.quantity for item in order_items)

    # Analytics per product for Chart.js
    product_stats = products.annotate(
        revenue=Sum(F('orderitem__price') * F('orderitem__quantity'), filter=Q(orderitem__order__status__in=['confirmed', 'shipped', 'delivered']))
    )

    product_names = [p.name[:20] for p in product_stats]
    product_revenues = [float(p.revenue or 0) for p in product_stats]

    return render(request, 'seller/dashboard.html', {
        'seller': seller,
        'products': products,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'product_names': product_names,
        'product_revenues': product_revenues,
    })

@login_required
def add_product(request):
    seller = get_object_or_404(Seller, user=request.user)

    if not seller.is_approved:
        messages.error(request, 'Your seller account is not approved yet')
        return redirect('seller:seller_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product added successfully')
            return redirect('seller:seller_dashboard')
    else:
        form = ProductForm()

    return render(request, 'seller/add_product.html', {'form': form})


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request,'Product updated')
            return redirect ('seller:seller_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'seller/edit_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    messages.success(request,'Product deleted')
    return redirect('seller:seller_dashboard')

@login_required
def seller_orders(request):
    seller = get_object_or_404(Seller, user=request.user)
    orders = Order.objects.filter(orderitem__product__seller=request.user).distinct().order_by('-created_at')
    
    for order in orders:
        order.seller_items_count = order.orderitem_set.filter(product__seller=request.user).count()
        order.seller_total_price = sum(item.price * item.quantity for item in order.orderitem_set.filter(product__seller=request.user))
        
    return render(request, 'seller/orders.html', {
        'orders': orders,
        'seller': seller,
    })

@login_required
def seller_order_detail(request, order_id):
    seller = get_object_or_404(Seller, user=request.user)
    order = get_object_or_404(Order, id=order_id)
    items = order.orderitem_set.filter(product__seller=request.user).select_related('product', 'variant')
    
    if not items.exists():
        messages.error(request, "This order does not contain products from your shop.")
        return redirect('seller:seller_orders')
        
    return render(request, 'seller/order_detail.html', {
        'order': order,
        'items': items,
        'seller': seller,
    })

@login_required
def ship_order_item(request, item_id):
    seller = get_object_or_404(Seller, user=request.user)
    item = get_object_or_404(OrderItem, id=item_id, product__seller=request.user)
    
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number', '').strip()
        if not tracking_number:
            messages.error(request, "Please enter a tracking number.")
            return redirect('seller:seller_order_detail', order_id=item.order.id)
            
        item.shipping_status = 'shipped'
        item.tracking_number = tracking_number
        from django.utils import timezone
        item.shipped_at = timezone.now()
        item.save()
        
        # Notify the buyer
        from extras.models import Notification
        Notification.objects.create(
            user=item.order.user,
            message=f"Item '{item.product.name}' from your Order #{item.order.id} has been shipped! Tracking ID: {tracking_number}.",
            notification_type='order'
        )
        
        # Check if all items in this order are now shipped
        order = item.order
        all_shipped = not order.orderitem_set.exclude(shipping_status='shipped').exists()
        if all_shipped and order.status in ['pending', 'confirmed']:
            order.status = 'shipped'
            order.save()
            
        messages.success(request, f"Item '{item.product.name}' has been marked as shipped.")
    
    return redirect('seller:seller_order_detail', order_id=item.order.id)


