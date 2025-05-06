from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .factories import UserFactory
from .forms import UserRegistrationForm, UserEditForm
from .services import update_user_profile
from authentication.services import generate_2fa, clear_messages
from django.contrib.auth import logout
from authentication.real_auth import RealAuthenticationSystem
from authentication.proxy import AuthenticationProxy

def register(request):
    clear_messages(request)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            try:
                # Create the user and assign the role
                UserFactory.create_user(
                    user_type=user_type,
                    email=form.cleaned_data['email'],
                    full_name=form.cleaned_data['full_name'],
                    consent_to_share_location=form.cleaned_data['consent_to_share_location'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    phone_number=form.cleaned_data['phone_number'],
                    profile_photo=form.cleaned_data.get('profile_photo', None),
                    blur_profile_photo=form.cleaned_data['blur_profile_photo'],
                    password=form.cleaned_data['password'],
                )
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')  # Redirect to the login page
            except ValidationError as e:
                messages.error(request, e.message)
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'There was an error with your registration.')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def edit_profile(request):
    clear_messages(request)
    user = request.user  # Get the currently logged-in user
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES) 
        if form.is_valid():
            try:
                result = update_user_profile(
                    user,
                    full_name=form.cleaned_data.get('full_name'),
                    email=form.cleaned_data.get('email'),
                    date_of_birth=form.cleaned_data.get('date_of_birth'),
                    phone_number=form.cleaned_data.get('phone_number'),
                    profile_photo=form.cleaned_data.get('profile_photo'),
                    blur_profile_photo=form.cleaned_data.get('blur_profile_photo'),
                    password=form.cleaned_data.get('password'),
                )
                
                if result.get('status') == 'verify_email':
                    request.session['new_email'] = result['new_email']
                    request.session['profile_update_data'] = result['other_data']
                    token = generate_2fa(request.user, target_email=result['new_email'])
                    request.session['email_verification_token'] = token
                    messages.info(request, f"We've sent a verification code to {result['new_email']}. Please verify to update your email.")
                    return redirect('verify_2fa')

                messages.success(request, 'Your profile has been updated successfully.')

                if form.cleaned_data.get('password'): # Check if password was changed
                    logout(request)
                    messages.info(request, 'You have been logged out due to a password change. Please log in again.')
                    return redirect('login')

                return redirect('profile')
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, 'There was an error updating your profile.')
    else:
        form = UserEditForm(initial={'blur_profile_photo': user.blur_profile_photo}) ## Pre-fill the form with the user's current data

    return render(request, 'edit_profile.html', {'form': form})