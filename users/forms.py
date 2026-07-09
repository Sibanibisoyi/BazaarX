from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import get_user_model
from .models import UserProfile



class AuthForm(forms.Form):
    email_or_phone = forms.CharField(
        max_length=150, 
        label="Email or Mobile Number",
        widget=forms.TextInput(attrs={'placeholder': 'Enter email or phone number', 'class': 'form-control'})
    )


from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line', 'city', 'state', 'pincode', 'is_default']



class UserProfileForm(forms.ModelForm):
    class Meta:
        model= UserProfile
        fields = ['bio', 'gender','dob']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }
