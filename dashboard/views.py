from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from orders.models import Order
from products.models import Product
from seller.models import Seller
from returns.models import ReturnRequest
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from products.models import Product, Category
from seller.forms import ProductForm
from .forms import CategoryForm


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

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_orders': total_orders,
        'total_users': total_users,
        'total_products': total_products,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'pending_sellers': pending_sellers,
        'pending_returns': pending_returns,
    })


@staff_required
def approve_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.is_approved = True
    seller.save()
    messages.success(request, 'Seller approved successfully.')
    return redirect('dashboard:admin_dashboard')


@staff_required
def reject_return(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)
    return_request.status = 'rejected'
    return_request.save()
    messages.success(request, 'Return request rejected.')
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
    return render(request, 'dashboard/products/product_list.html', {'products': products})


@staff_required
def admin_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
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
            messages.success(request, 'Product updated successfully.')
            return redirect('dashboard:admin_products')
    else:
        form = ProductForm(instance=product)
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
    return render(request, 'dashboard/orders/order_list.html', {'orders': orders})


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
        order.status = status
        order.save()
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
