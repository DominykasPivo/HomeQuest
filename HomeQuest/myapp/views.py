from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import User, GoldSeller, Seller, Property  #have to make user models
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserEditForm, PropertyForm
from django.contrib.auth.decorators import login_required
from .factories import UserFactory
from .services import clear_messages, update_user_profile, get_or_create_gold_seller, update_subscription, create_property_for_seller, delete_property, update_property
from django.core.exceptions import ValidationError
from django.http import Http404

import os
from django.conf import settings

import logging
# from datetime import timedelta
# from django.utils.timezone import now

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login_email_phone(request):
    return render(request, 'login_email_phone.html')

logger = logging.getLogger(__name__)
def register(request):
    clear_messages(request)

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            try:
                # Create the user and assign the role
                user = UserFactory.create_user(
                    user_type=user_type,
                    email=form.cleaned_data['email'],
                    full_name=form.cleaned_data['full_name'],
                    consent_to_share_location=form.cleaned_data['consent_to_share_location'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    phone_number=form.cleaned_data['phone_number'],
                    profile_photo=form.cleaned_data.get('profile_photo', None),
                    password=form.cleaned_data['password'],
                )
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')  # Redirect to the login page
            except ValidationError as e:
                logger.error(f"Validation error during registration: {e}")
                messages.error(request, e.message)
            except Exception as e:
                logger.error(f"Unexpected error during registration: {e}")
                messages.error(request, f"An unexpected error occurred: {str(e)}")
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
            # # Get the user by email
            # user = User.objects.get(email=email)
            # Authenticate using the username (since Django uses username internally)
            user = authenticate(request, email=email, password=password)
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
            user = authenticate(request, phone_number = user.phone_number, password=password)
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


@login_required
def manage_subscription(request):
    try:
        # Ensure the user is a Seller
        seller = Seller.objects.get(pk=request.user.pk)
    except Seller.DoesNotExist:
        messages.error(request, "You must be a Seller to access this page.")
        return redirect('home')

    # Get the GoldSeller instance if it exists
    gold_seller = GoldSeller.objects.filter(pk=seller.pk).first()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'buy_gold':
            # Upgrade to GoldSeller
            gold_seller = get_or_create_gold_seller(request.user, upgrade_to_gold=True)
        elif action == 'cancel_gold' and gold_seller:
            # Downgrade to basic
            gold_seller.subscription_plan = 'basic'
            gold_seller.subscription_end_date = None
            gold_seller.save()
        return redirect('manage_subscription')

    return render(request, 'manage_subscription.html', {'gold_seller': gold_seller})


@login_required
def create_property(request):
    try:
        seller = Seller.objects.get(pk=request.user.pk)
    except Seller.DoesNotExist:
        messages.error(request, "Only sellers can create properties.")
        return redirect('home')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                create_property_for_seller(
                    seller=seller,
                    property_data=form.cleaned_data,
                    image=form.cleaned_data.get('image')
                )
                print("asdaada")
                messages.success(request, "Property created successfully!")
                return redirect('property_list')
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
        else:
            messages.error(request, "There was an error creating the property.")
    else:
        form = PropertyForm()

    return render(request, 'property_create.html', {'form': form})

@login_required
def property_list(request):
    print("DEBUG: property_list view called")  # Add this line
    seller = get_object_or_404(Seller, pk=request.user.pk)
    properties = Property.objects.filter(seller=seller)
    return render(request, 'property_list.html', {'properties': properties})

@login_required
def property_detail(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    return render(request, 'property_detail.html', {'property': property_obj})

@login_required
def property_edit(request, property_id):
    property_instance = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            try:
                # Use the service function to update the property
                image = form.cleaned_data.get('image')
                print(f"DEBUG: Image parameter in create_property_for_seller: {type(image)}")
                # Only pass the image if it's an uploaded file
                if hasattr(image, 'read'):
                    image_to_pass = image
                    
                else:
                    
                    image_to_pass = None
                update_property(
                    property_instance=property_instance,
                    property_data=form.cleaned_data,
                    image=image_to_pass
                )
                
                messages.success(request, "Property updated successfully!")
                return redirect('property_detail', property_id=property_instance.pk)
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
        else:
            messages.error(request, "There was an error updating the property.")
    else:
        form = PropertyForm(instance=property_instance)

    return render(request, 'property_edit.html', {'form': form, 'property': property_instance})

@login_required
def property_delete(request, property_id):
    property_instance = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    if request.method == 'POST':
        try:
            # Use the service function to delete the property
            delete_property(property_instance)
            messages.success(request, "Property deleted successfully!")
            return redirect('property_list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return render(request, 'property_delete.html', {'property': property_instance})