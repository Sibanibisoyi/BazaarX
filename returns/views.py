from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ReturnRequest
from orders.models import Order
# Create your views here.

@login_required
def raise_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        ReturnRequest.objects.create(
            order=order,
            user=request.user,
            reason=reason
        )
        messages.success(request, 'Return request submitted')
        return redirect('orders:my_orders')

    return render(request, 'returns/raise_return.html', {'order': order})

@login_required
def my_returns(request):
    returns = ReturnRequest.objects.filter(user=request.user)
    return render(request, 'returns/my_returns.html', {'returns': returns})
    

@login_required
def approve_return(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)
    return_request.status = 'approved'
    return_request.save()
    messages.success(request,'Return approved')
    return redirect('orders:my_orders')

