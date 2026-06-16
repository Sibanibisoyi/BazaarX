from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import get_user_model



class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'phone', 'password1', 'password2']