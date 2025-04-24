from django.shortcuts import render, redirect, HttpResponse
from .models import User #have to make user models
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserEditForm
from django.contrib.auth.decorators import login_required
from .factories import UserFactory
from .services import clear_messages, update_user_profile
from django.core.exceptions import ValidationError

# Create your views here.
def home(request):
    return render(request, 'base.html')

def login_email_phone(request):
    return render(request, 'login_email_phone.html')

def register(request):
    # Clear any existing messages
    clear_messages(request)

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            UserFactory.create_user(
                user_type=user_type,
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                full_name=form.cleaned_data['full_name'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                consent_to_share_location=form.cleaned_data['consent_to_share_location'],
                phone_number=form.cleaned_data['phone_number'],
                profile_photo=form.cleaned_data.get('profile_photo', None),
                password=form.cleaned_data['password'],
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')  # Redirect to the login page
        else:
            messages.error(request, 'There was an error with your registration.')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_email(request):
    # Clear any existing messages
    clear_messages(request)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Get the user by email
            user = User.objects.get(email=email)
            # Authenticate using the username (since Django uses username internally)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page after login
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login_email.html')

def login_phone(request):
    # Clear any existing messages
    clear_messages(request)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        try:
            user = User.objects.get(phone_number=phone_number)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page after login
            else:
                messages.error(request, 'Invalid phone number or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid phone number or password.')
    return render(request, 'login_phone.html')


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def edit_profile(request):
    clear_messages(request)
    user = request.user  # Get the currently logged-in user
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Use the service function to update the user's profile
                update_user_profile(
                    user,
                    username=form.cleaned_data.get('username'),
                    full_name=form.cleaned_data.get('full_name'),
                    email=form.cleaned_data.get('email'),
                    phone_number=form.cleaned_data.get('phone_number'),
                    profile_photo=form.cleaned_data.get('profile_photo'),
                    password=form.cleaned_data.get('password'),
                )
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('profile')  # Redirect to the profile page
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, 'There was an error updating your profile.')
    else:
        # Initialize the form with blank fields
        form = UserEditForm()

    return render(request, 'edit_profile.html', {'form': form})