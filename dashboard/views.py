from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from orders.models import Order
from products.models import Product, ProductImage, ProductVariant
from seller.models import Seller
from returns.models import ReturnRequest
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from products.models import Product, Category
from seller.forms import ProductForm
from .forms import CategoryForm
from django.core.paginator import Paginator
from django.utils import timezone


# ─── Reusable staff guard decorator ──────────────────────────────────────────
def staff_required(view_func):
    """Redirect non-staff users away from admin views."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/bazarx-admin/login/')
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('products:home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Views ────────────────────────────────────────────────────────────────────

@staff_required
def admin_dashboard(request):
    User = get_user_model()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    recent_orders = Order.objects.order_by('-created_at')[:10]
    pending_sellers = Seller.objects.filter(is_approved=False)
    pending_returns = ReturnRequest.objects.filter(status='pending')

    # Line chart data: Orders per day for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_orders = Order.objects.filter(created_at__gte=thirty_days_ago) \
        .annotate(date=TruncDate('created_at')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')

    chart_labels = [entry['date'].strftime('%b %d') if entry['date'] else '' for entry in daily_orders]
    chart_data = [entry['count'] for entry in daily_orders]

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_orders': total_orders,
        'total_users': total_users,
        'total_products': total_products,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'pending_sellers': pending_sellers,
        'pending_returns': pending_returns,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    })


@staff_required
def approve_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.is_approved = True
    seller.save()
    messages.success(request, 'Seller approved successfully.')
    return redirect('dashboard:admin_dashboard')


def admin_login(request):
    """Separate login for the admin control center."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/bazarx-admin/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('/bazarx-admin/')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    return render(request, 'dashboard/admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('/bazarx-admin/login/')


# ─── Products ─────────────────────────────────────────────────────────────────

@staff_required
def admin_products(request):
    products = Product.objects.all().order_by('-id')
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard/products/product_list.html', {'products': page_obj, 'page_obj': page_obj})


@staff_required
def admin_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            
            # Save multiple images
            images = request.FILES.getlist('extra_images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)
            
            # Save variants
            sizes = form.cleaned_data.get('sizes')
            if sizes:
                size_list = [s.strip() for s in sizes.split(',') if s.strip()]
                for size in size_list:
                    ProductVariant.objects.create(product=product, name='Size', value=size, stock=product.stock)

            quantities = form.cleaned_data.get('quantities')
            if quantities:
                qty_list = [q.strip() for q in quantities.split(',') if q.strip()]
                for qty in qty_list:
                    ProductVariant.objects.create(product=product, name='Quantity', value=qty, stock=product.stock)
            
            messages.success(request, 'Product added successfully.')
            return redirect('dashboard:admin_products')
    else:
        form = ProductForm()
    return render(request, 'dashboard/products/add_product.html', {'form': form})


@staff_required
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            
            # Save multiple additional images
            images = request.FILES.getlist('extra_images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)
            
            # Update variants
            sizes = form.cleaned_data.get('sizes')
            existing_size_variants = product.productvariant_set.filter(name__iexact='Size')
            if sizes:
                size_list = [s.strip() for s in sizes.split(',') if s.strip()]
                existing_size_variants.exclude(value__in=size_list).delete()
                for size in size_list:
                    ProductVariant.objects.get_or_create(
                        product=product, name='Size', value=size,
                        defaults={'stock': product.stock}
                    )
            else:
                existing_size_variants.delete()

            quantities = form.cleaned_data.get('quantities')
            existing_qty_variants = product.productvariant_set.filter(name__iexact='Quantity')
            if quantities:
                qty_list = [q.strip() for q in quantities.split(',') if q.strip()]
                existing_qty_variants.exclude(value__in=qty_list).delete()
                for qty in qty_list:
                    ProductVariant.objects.get_or_create(
                        product=product, name='Quantity', value=qty,
                        defaults={'stock': product.stock}
                    )
            else:
                existing_qty_variants.delete()
            
            messages.success(request, 'Product updated successfully.')
            return redirect('dashboard:admin_products')
    else:
        form = ProductForm(instance=product)
    
    existing_images = ProductImage.objects.filter(product=product)
    return render(request, 'dashboard/products/edit_product.html', {
        'form': form,
        'product': product,
        'existing_images': existing_images,
    })
    return render(request, 'dashboard/products/edit_product.html', {'form': form, 'product': product})


@staff_required
def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('dashboard:admin_products')


# ─── Orders ───────────────────────────────────────────────────────────────────

@staff_required
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard/orders/order_list.html', {'orders': page_obj, 'page_obj': page_obj})


@staff_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.orderitem_set.all()
    return render(request, 'dashboard/orders/order_detail.html', {
        'orders': order,
        'items': items,
    })


@staff_required
def admin_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        old_status = order.status
        order.status = status
        # Auto-stamp delivered_at when status is set to 'delivered'
        if status == 'delivered' and old_status != 'delivered':
            order.delivered_at = timezone.now()
        order.save()
        
        # Send notification email if status changed
        if status != old_status:
            from utils.email_utils import (
                send_order_confirmation_email,
                send_order_shipped_email,
                send_order_delivered_email,
                send_order_cancelled_email,
            )
            if status == 'confirmed':
                send_order_confirmation_email(order)
            elif status == 'shipped':
                send_order_shipped_email(order)
            elif status == 'delivered':
                send_order_delivered_email(order)
            elif status == 'cancelled':
                send_order_cancelled_email(order)

        messages.success(request, 'Order status updated.')
    return redirect('dashboard:admin_order_detail', order_id=order_id)


# ─── Categories ───────────────────────────────────────────────────────────────

@staff_required
def admin_categories(request):
    categories = Category.objects.all().order_by('-id')
    return render(request, 'dashboard/categories/category_list.html', {'categories': categories})


@staff_required
def admin_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('dashboard:admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/categories/category_form.html', {'form': form, 'title': 'Add Category'})


@staff_required
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('dashboard:admin_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/categories/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})


@staff_required
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted.')
    return redirect('dashboard:admin_categories')


from extras.models import FlashSale

@staff_required
def flash_sale_list(request):
    sales = FlashSale.objects.all().order_by('-id')
    return render(request, 'dashboard/flash_sales/flash_sale_list.html', {'sales': sales})

@staff_required
def add_flash_sale(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        sale_price = request.POST.get('sale_price')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        product = get_object_or_404(Product, id=product_id)
        FlashSale.objects.create(
            product=product,
            sale_price=sale_price,
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )
        messages.success(request, 'Flash sale created!')
        return redirect('dashboard:flash_sale_list')
    products = Product.objects.filter(is_active=True)
    return render(request, 'dashboard/flash_sales/add_flash_sale.html', {'products': products})

@staff_required
def delete_flash_sale(request, pk):
    sale = get_object_or_404(FlashSale, pk=pk)
    sale.delete()
    messages.success(request, 'Flash sale deleted!')
    return redirect('dashboard:flash_sale_list')

@staff_required
def delete_product_image(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    image.delete()
    messages.success(request, 'Image deleted.')
    return redirect('dashboard:admin_edit_product', product_id=image.product.id)