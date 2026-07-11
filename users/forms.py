from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
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
    pincode = forms.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r'^[1-9][0-9]{5}$',
                message='Enter a valid 6-digit Indian pincode (e.g. 400001).',
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': '6-digit pincode',
            'maxlength': '6',
            'pattern': '[1-9][0-9]{5}',
            'inputmode': 'numeric',
        })
    )

    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line', 'city', 'state', 'pincode', 'is_default']



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'gender', 'dob']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }


User = get_user_model()

class ProfilePictureForm(forms.ModelForm):
    """Separate form for uploading the profile picture on CustomUser."""
    class Meta:
        model = User
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
        }
