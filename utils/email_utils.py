import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

def _send_html_email(subject, template_name, context, recipient_list):
    """
    Helper function to send a beautiful HTML email with text fallback.
    """
    try:
        # Inject global variables if needed (e.g. site_url)
        context['site_url'] = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        
        # Render HTML body
        html_content = render_to_string(template_name, context)
        # Create plain text version from HTML
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {str(e)}")
        # Print to console for easy local debugging if SMTP fails
        print(f"EMAIL ERROR: Failed to send '{subject}' to {recipient_list}. Error: {str(e)}")
        return False

def send_order_placed_email(order):
    subject = f'Order #{order.id} Placed - BazaarX'
    context = {
        'order': order,
        'items': order.orderitem_set.all(),
    }
    return _send_html_email(subject, 'emails/order_placed.html', context, [order.user.email])

# Keep/Alias send_order_confirmation_email for backward compatibility
def send_order_confirmation_email(order):
    return send_order_placed_email(order)

def send_order_shipped_email(order):
    subject = f'🚚 Your BazaarX Order #{order.id} Has Been Shipped!'
    context = {
        'order': order,
        'items': order.orderitem_set.all(),
    }
    return _send_html_email(subject, 'emails/order_shipped.html', context, [order.user.email])

def send_order_delivered_email(order):
    subject = f'🎉 Your BazaarX Order #{order.id} Has Been Delivered!'
    context = {
        'order': order,
        'items': order.orderitem_set.all(),
    }
    return _send_html_email(subject, 'emails/order_delivered.html', context, [order.user.email])

def send_order_cancelled_email(order):
    subject = f'❌ Your BazaarX Order #{order.id} Has Been Cancelled'
    context = {
        'order': order,
        'items': order.orderitem_set.all(),
    }
    return _send_html_email(subject, 'emails/order_cancelled.html', context, [order.user.email])


def send_return_approved_email(return_request):
    subject = f'✅ Return Approved — BazaarX Order #{return_request.order.id}'
    context = {
        'return_request': return_request,
        'order': return_request.order,
        'user': return_request.user,
    }
    return _send_html_email(
        subject, 'emails/return_approved.html', context, [return_request.user.email]
    )


def send_return_rejected_email(return_request):
    subject = f'❌ Return Request Declined — BazaarX Order #{return_request.order.id}'
    context = {
        'return_request': return_request,
        'order': return_request.order,
        'user': return_request.user,
    }
    return _send_html_email(
        subject, 'emails/return_rejected.html', context, [return_request.user.email]
    )