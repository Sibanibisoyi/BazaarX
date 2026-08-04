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


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'extras/notifications.html', {
        'page_obj': page_obj,
        'notifications': page_obj,
    })

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'status': 'success', 'unread_count': unread_count})

@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success', 'unread_count': 0})





