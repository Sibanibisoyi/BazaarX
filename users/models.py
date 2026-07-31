from django.db import models
import random
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.email
    
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True)
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

class LoyaltyPoints(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.balance} pts"


class PointsHistory(models.Model):
    EARNED = 'earned'
    REDEEMED = 'redeemed'
    TYPE_CHOICES = [
        (EARNED, 'Earned'),
        (REDEEMED, 'Redeemed'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    points = models.IntegerField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.points} pts"



class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # OTP valid for 10 minutes
        return not self.is_used and (timezone.now() - self.created_at).seconds < 600

    def __str__(self):
        return f"{self.user.email} - {self.otp}"

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} Wallet - ₹{self.balance}"

class WalletTransaction(models.Model):
    CREDIT = 'credit'
    DEBIT = 'debit'
    TYPE_CHOICES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - ₹{self.amount}"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)