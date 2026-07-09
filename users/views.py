from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Address
from .forms import AddressForm, UserProfileForm, AuthForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .models import LoyaltyPoints
from .models import PointsHistory
from .utils import generate_otp, send_otp
from .models import OTP
from .models import CustomUser

# Imports for Password Reset
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site




import uuid

def auth_view(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('email_or_phone').strip()
            is_email = '@' in identifier
            
            try:
                if is_email:
                    user = CustomUser.objects.get(email=identifier)
                else:
                    user = CustomUser.objects.get(phone=identifier)
            except CustomUser.DoesNotExist:
                # Create user
                username = f"user_{uuid.uuid4().hex[:8]}"
                if is_email:
                    user = CustomUser.objects.create(username=username, email=identifier, is_active=False)
                else:
                    user = CustomUser.objects.create(username=username, phone=identifier, is_active=False)
                UserProfile.objects.create(user=user)
                LoyaltyPoints.objects.create(user=user)

            otp_code = generate_otp()
            OTP.objects.create(user=user, otp=otp_code)
            send_otp(identifier, otp_code)
            
            request.session['pending_user_id'] = user.id
            return redirect('users:verify_otp')
    else:
        form = AuthForm()
    
    return render(request, 'users/auth.html', {'form': form})

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
        return redirect('users:login')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        try:
            otp_obj = OTP.objects.filter(user_id=user_id, is_used=False).latest('created_at')
            if otp_obj.otp == otp_input and otp_obj.is_valid():
                otp_obj.is_used = True
                otp_obj.save()
                user = otp_obj.user
                
                if not user.is_active:
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


def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            associated_users = CustomUser.objects.filter(email=email, is_active=True)
            if associated_users.exists():
                for user in associated_users:
                    # Generate reset credentials
                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    
                    # Context for email template
                    current_site = get_current_site(request)
                    context = {
                        'email': user.email,
                        'domain': current_site.domain,
                        'site_name': current_site.name,
                        'uid': uidb64,
                        'token': token,
                        'protocol': 'https' if request.is_secure() else 'http',
                        'user': user,
                    }
                    
                    # Render and send email
                    subject = "Password Reset Requested"
                    email_content = render_to_string('users/password_reset_email.html', context)
                    try:
                        send_mail(
                            subject,
                            email_content,
                            None,  # Uses DEFAULT_FROM_EMAIL from settings
                            [user.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        # Log error if any mail service issue occurs
                        pass
                
                messages.success(request, "A password reset email has been sent.")
                return redirect('users:password_reset_done')
            else:
                # Anti-user-enumeration success message
                messages.success(request, "A password reset email has been sent.")
                return redirect('users:password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'users/forgot_password.html', {'form': form})


def password_reset_done(request):
    return render(request, 'users/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('users:password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'users/password_reset_confirm.html', {'form': form, 'validlink': True})
    else:
        return render(request, 'users/password_reset_confirm.html', {'validlink': False})


def password_reset_complete(request):
    return render(request, 'users/password_reset_complete.html')