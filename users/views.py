from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Address
from .forms import AddressForm, UserProfileForm, RegisterForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .models import LoyaltyPoints
from .models import PointsHistory
from .utils import generate_otp, send_otp_email
from .models import OTP
from .models import CustomUser




def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # deactivate until OTP verified
            user.save()
            otp_code = generate_otp()
            OTP.objects.create(user=user, otp=otp_code)
            send_otp_email(user.email, otp_code)
            request.session['pending_user_id'] = user.id
            return redirect('users:verify_otp')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('products:home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('users:login')



@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    loyalty, created = LoyaltyPoints.objects.get_or_create(user=request.user)
    return render(request, 'users/profile.html', {
        'profile': profile,
        'loyalty': loyalty,
    })


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'users/address_list.html', {'addresses': addresses})

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('users:address_list')
    else:
        form = AddressForm()
    return render(request, 'users/add_address.html', {'form': form})

@login_required
def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('users:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'users/add_address.html', {'form': form})

@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    return redirect('users:address_list')


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'users/edit_profile.html', {'form': form})




@login_required
def points_history(request):
    history = PointsHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/points_history.html', {'history': history})

def verify_otp(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect('users:register')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        try:
            otp_obj = OTP.objects.filter(user_id=user_id, is_used=False).latest('created_at')
            if otp_obj.otp == otp_input and otp_obj.is_valid():
                otp_obj.is_used = True
                otp_obj.save()
                user = otp_obj.user
                user.is_active = True
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pending_user_id']
                return redirect('products:home')
            else:
                messages.error(request, 'Invalid or expired OTP.')
        except OTP.DoesNotExist:
            messages.error(request, 'OTP not found.')
    
    return render(request, 'users/verify_otp.html')



def otp_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            otp_code = generate_otp()
            OTP.objects.create(user=user, otp=otp_code)
            send_otp_email(email, otp_code)
            request.session['pending_user_id'] = user.id
            return redirect('users:verify_login_otp')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    return render(request, 'users/otp_login.html')

def verify_login_otp(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect('users:otp_login')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        try:
            otp_obj = OTP.objects.filter(user_id=user_id, is_used=False).latest('created_at')
            if otp_obj.otp == otp_input and otp_obj.is_valid():
                otp_obj.is_used = True
                otp_obj.save()
                user = otp_obj.user
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pending_user_id']
                return redirect('products:home')
            else:
                messages.error(request, 'Invalid or expired OTP.')
        except OTP.DoesNotExist:
            messages.error(request, 'OTP not found.')
    
    return render(request, 'users/verify_login_otp.html')