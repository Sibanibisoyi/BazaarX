from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Coupon

# Create your views here.
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')

        try:
            coupon = Coupon.objects.get(code=code)
            is_valid, msg = coupon.is_valid_for_user(request.user)
            
            if is_valid:
                request.session['coupon_id'] = coupon.id
                messages.success(request, 'Coupon applied successfully')
            else:
                request.session['coupon_id'] = None
                messages.error(request, msg)

        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            messages.error(request, 'Invalid or expired coupon')
    return redirect('cart:cart_detail')
