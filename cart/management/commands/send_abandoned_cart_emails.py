from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cart.models import Cart
from utils.email_utils import send_abandoned_cart_email
from coupons.models import Coupon
import string
import random

class Command(BaseCommand):
    help = 'Sends recovery emails for abandoned carts'

    def handle(self, *args, **kwargs):
        # We consider a cart abandoned if it hasn't been updated in 24 hours
        # and we only look back up to 48 hours to avoid spamming very old carts.
        now = timezone.now()
        abandoned_time_start = now - timedelta(hours=48)
        abandoned_time_end = now - timedelta(hours=24)

        # Get carts matching criteria
        abandoned_carts = Cart.objects.filter(
            updated_at__gte=abandoned_time_start,
            updated_at__lte=abandoned_time_end,
            abandoned_email_sent=False
        )

        sent_count = 0

        for cart in abandoned_carts:
            # Check if cart has items
            if cart.cartitem_set.exists():
                # Optionally create or fetch a generic coupon here
                # We'll create a 5% off coupon for 3 days
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                coupon = Coupon.objects.create(
                    code=f"COMEBACK-{code}",
                    discount=5.00,
                    valid_from=now,
                    valid_to=now + timedelta(days=3),
                    active=True
                )
                
                success = send_abandoned_cart_email(cart, coupon=coupon)
                if success:
                    cart.abandoned_email_sent = True
                    cart.save()
                    sent_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully sent {sent_count} abandoned cart emails.'))
