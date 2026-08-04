from django.contrib import admin
from .models import Wishlist 
from .models import FlashSale, Notification

# Register your models here.
admin.site.register(Wishlist)
admin.site.register(FlashSale)
admin.site.register(Notification)