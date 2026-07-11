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
    order_items = OrderItem.objects.filter(
        product__seller=request.user).order_by('-order__created_at')

    return render(request, 'seller/orders.html', {'order_items': order_items})


