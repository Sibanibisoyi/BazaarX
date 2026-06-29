from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Coupon

# Create your views here.
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')

        try:
            coupon = Coupon.objects.get(
                code=code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
            
            if request.user in coupon.used_by.all():
                request.session['coupon_id'] = None
                messages.error(request, 'You have already used this coupon')
            else:
                request.session['coupon_id'] = coupon.id
                messages.success(request, 'Coupon applied successfully')

        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            messages.error(request, 'Invalid or expired coupon')
    return redirect('cart:cart_detail')
