from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.conf import settings
from user_management.services import update_user_profile
from .services import clear_messages, generate_2fa, verify_2fa_token
from user_management.models import User
from authentication.real_auth import RealAuthenticationSystem
from authentication.proxy import AuthenticationProxy


def login_email_phone(request):
    """View for selecting login method (email or phone)"""
    return render(request, 'login_email_phone.html')

def login_email(request):
    """Handle login with email and password"""
    clear_messages(request)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            auth_system = AuthenticationProxy(RealAuthenticationSystem())
            user = auth_system.email_authenticate_user(request, email, password)
            if user is not None:
                request.session['pre_2fa_user_id'] = user.pk
                auth_system.send_email_authentication_code(user, email)
                messages.info(request, 'The verification code has been sent to your email.')
                return redirect('verify_2fa')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return render(request, 'login_email.html')

def login_phone(request):
    """Handle login with phone number and password"""
    clear_messages(request)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        auth_system = AuthenticationProxy(RealAuthenticationSystem())
        user = auth_system.phone_num_authenticate_user(request, phone_number, password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid phone number or password.')
    return render(request, 'login_phone.html')

def verify_2fa(request):
    """Verify 2FA code and complete login or email change."""
    new_email = request.session.get('new_email')
    profile_data = request.session.get('profile_update_data')
    auth_system = AuthenticationProxy(RealAuthenticationSystem())
   
    if new_email:
        if request.method == 'POST':
            token = request.POST.get('token')
            stored_token = request.session.get('email_verification_token')
            if token == stored_token:
                user = request.user
                user.email = new_email
                
                if profile_data: 
                    update_user_profile(user, **profile_data)
                else:
                    user.save()
                
                
                for key in ['new_email', 'profile_update_data', 'email_verification_token']:
                    if key in request.session:
                        del request.session[key]
                
                messages.success(request, "Email verified and profile updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Invalid verification code. Please try again.")
        
        return render(request, '2fa.html', {'verification_type': 'email_change', 'new_email': new_email})


    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        messages.error(request, "Authentication session expired. Please log in again.")
        return redirect('login_email')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login_email')
    
    if request.method == 'POST':
        token = request.POST.get('token')
        
        if auth_system.verify_code(user, token):
            # 2FA successful, complete login
            login(request, user)
            # Clean up the session
            if 'pre_2fa_user_id' in request.session:
                del request.session['pre_2fa_user_id']
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid verification code. Please try again.")
    
    return render(request, '2fa.html')

def logout_view(request):
    logout(request)
    return redirect('login')
