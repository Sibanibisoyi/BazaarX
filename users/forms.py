from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import get_user_model
from .models import UserProfile



class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'phone', 'password1', 'password2']


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
