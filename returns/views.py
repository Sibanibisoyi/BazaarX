from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ReturnRequest
from orders.models import Order
from django.utils import timezone
from utils.email_utils import send_return_approved_email, send_return_rejected_email

# Create your views here.

@login_required
def raise_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Must be delivered
    if order.status != 'delivered':
        messages.error(request, 'You can only raise a return request for delivered orders.')
        return redirect('orders:order_detail', order_id=order.id)

    # Check 10-day return window
    if not order.is_returnable:
        messages.error(
            request,
            f'The return window for this order has expired. Returns must be raised within 10 days of delivery.'
        )
        return redirect('orders:order_detail', order_id=order.id)

    # Prevent duplicate return requests
    existing = ReturnRequest.objects.filter(order=order, user=request.user).first()
    if existing:
        messages.warning(request, f'You have already raised a return request for Order #{order.id}. Status: {existing.get_status_display()}')
        return redirect('returns:my_returns')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Please provide a reason for the return.')
        else:
            ReturnRequest.objects.create(
                order=order,
                user=request.user,
                reason=reason
            )
            messages.success(request, f'Return request for Order #{order.id} submitted successfully. We will review it within 2–3 business days.')
            return redirect('returns:my_returns')

    return render(request, 'returns/raise_return.html', {
        'order': order,
        'return_deadline': order.return_deadline,
    })

@login_required
def my_returns(request):
    returns = ReturnRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'returns/my_returns.html', {'returns': returns})


@login_required
def approve_return(request, return_id):
    from users.models import WalletTransaction, Wallet
    from django.utils import timezone

    return_request = get_object_or_404(ReturnRequest, id=return_id)
    order = return_request.order
    refund_amount = order.total_price

    # Determine refund method based on payment method
    if order.payment_method == 'cod':
        refund_method = 'cod_wallet'
    else:
        # For Razorpay — credit to BazaarX wallet (original source refund requires stored payment_id)
        refund_method = 'wallet'

    # Credit wallet
    wallet, _ = Wallet.objects.get_or_create(user=return_request.user)
    wallet.balance += refund_amount
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=refund_amount,
        transaction_type='credit',
        description=f'Refund for Return #{return_request.id} (Order #{order.id}) — {order.get_payment_method_display()}'
    )

    # Update return request
    return_request.status = 'approved'
    return_request.refund_method = refund_method
    return_request.refunded_at = timezone.now()
    return_request.save()

    # Update order status to 'returned'
    order.status = 'returned'
    order.save()

    send_return_approved_email(return_request)
    messages.success(
        request,
        f'Return #{return_id} approved. ₹{refund_amount} refunded to {return_request.user.username}\'s BazaarX Wallet. Order #{order.id} marked as Returned.'
    )
    return redirect('dashboard:admin_returns')


@login_required
def reject_return(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)
    return_request.status = 'rejected'
    return_request.save()
    send_return_rejected_email(return_request)
    messages.success(request, f'Return #{return_id} rejected — notification sent to {return_request.user.email}.')
    return redirect('dashboard:admin_returns')
