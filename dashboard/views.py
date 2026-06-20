from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from orders.models import Order
from products.models import Product
from seller.models import Seller
from returns.models import ReturnRequest
from django.db.models import Sum
from django.contrib import messages
# Create your views here.

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('products:home')
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

@login_required
def approve_seller(request,seller_id):
    if not request.user.is_staff:
        return redirect('products:home')
    seller = get_object_or_404(Seller, id=seller_id)
    seller.is_approved = True
    seller.save()
    messages.success(request, 'Seller approved')
    return redirect('dashboard:admin_dashboard')

@login_required
def reject_return(request,return_id):
    if not request.user.is_staff:
        return redirect('products:home')
    return_request = get_object_or_404(ReturnRequest, id=return_id)
    return_request.status = 'rejected'
    return_request.save()
    messages.success(request, 'return rejected')
    return redirect('dashboard:admin_dashboard')

