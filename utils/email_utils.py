from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f'Order #{order.id} Confirmed - BazaarX'
    message = f'Dear {order.user.username},\n\nYour order #{order.id} has been placed successfully.\nTotal: ₹{order.total_price}\n\nThank you for shopping with BazaarX!'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email]
    )

def send_order_shipped_email(order):
    subject = f'Order #{order.id} Shipped - BazaarX'
    message = f'Dear {order.user.username},\n\nYour order #{order.id} has been shipped.\nIt will be delivered soon.\n\nThank you for shopping with BazaarX!'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email]
    )