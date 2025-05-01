from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import User, GoldSeller, Seller, Property  #have to make user models
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserEditForm, PropertyForm
from django.contrib.auth.decorators import login_required
from .factories import UserFactory
from .services import (
        clear_messages, update_user_profile, get_or_create_gold_seller, save_property_image,
        create_property_for_seller, delete_property, delete_property_image, replace_property_image, add_property_image,
        filter_properties, add_verification_file, delete_verification_file
        )
from django.core.exceptions import ValidationError
from django.http import Http404
from django.conf import settings


# from datetime import timedelta
# from django.utils.timezone import now

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login_email_phone(request):
    return render(request, 'login_email_phone.html')

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
                messages.error(request, e.message)
            except Exception as e:
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
                update_user_profile(
                    user,
                    full_name=form.cleaned_data.get('full_name'),
                    email=form.cleaned_data.get('email'),
                    date_of_birth=form.cleaned_data.get('date_of_birth'),
                    phone_number=form.cleaned_data.get('phone_number'),
                    profile_photo=form.cleaned_data.get('profile_photo'),
                    password=form.cleaned_data.get('password'),
                )
                messages.success(request, 'Your profile has been updated successfully.')

                if form.cleaned_data.get('password'): # Check if password was changed
                    # If the password was changed, log the user out
                    logout(request)
                    messages.info(request, 'You have been logged out due to a password change. Please log in again.')
                    return redirect('login')

                return redirect('profile')
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, 'There was an error updating your profile.')
    else:
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
    print("DEBUG: property_list view called")  
    seller = get_object_or_404(Seller, pk=request.user.pk)
    properties = Property.objects.filter(seller=seller)
    return render(request, 'property_list.html', {
        'properties': properties,
        'MEDIA_URL': settings.MEDIA_URL,
    })

@login_required
def property_detail(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    return render(request, 'property_detail.html', {
        'property': property_obj,
        'MEDIA_URL': settings.MEDIA_URL, 
    })

@login_required
def property_edit(request, property_id):
    property_instance = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    form = PropertyForm(request.POST or None, request.FILES or None, instance=property_instance)

    if request.method == 'POST':
        # Delete image
        if 'delete_image' in request.POST:
            image_to_delete = request.POST['delete_image']
            delete_property_image(property_instance, image_to_delete)
            return redirect('property_edit', property_id=property_id)

        # Replace image
        if 'replace_image_btn' in request.POST:
            image_to_replace = request.POST['replace_image_btn']
            idx = property_instance.image_paths.index(image_to_replace)
            file_field = f'replace_image_{idx}'
            new_image = request.FILES.get(file_field)
            replace_property_image(property_instance, image_to_replace, new_image, save_property_image)
            return redirect('property_edit', property_id=property_id)

        # Add new image
        if 'add_image_btn' in request.POST:
            new_image = request.FILES.get('new_image')
            add_property_image(property_instance, new_image, save_property_image)
            return redirect('property_edit', property_id=property_id)

        # Save other changes
        if 'save_changes' in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "Property updated successfully!")
                return redirect('property_detail', property_id=property_instance.pk)
            else:
                messages.error(request, "There was an error updating the property.")

    return render(request, 'property_edit.html', {
        'form': form,
        'property': property_instance,
        'MEDIA_URL': settings.MEDIA_URL,
    })


@login_required
def property_delete(request, property_id):
    property_instance = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    if request.method == 'POST':
        try:
            delete_property(property_instance)
            messages.success(request, "Property deleted successfully!")
            return redirect('property_list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return render(request, 'property_delete.html', {'property': property_instance})


def property_search(request):
    search_type = request.GET.get('search_type')
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    property_type = request.GET.get('property_type')
    min_rooms = request.GET.get('min_rooms')
    max_rooms = request.GET.get('max_rooms')
    min_size = request.GET.get('min_size')
    max_size = request.GET.get('max_size')
    is_verified = request.GET.get('is_verified')
    # Convert values to correct types
    min_price = float(min_price) if min_price else None
    max_price = float(max_price) if max_price else None
    min_rooms = int(min_rooms) if min_rooms else None
    max_rooms = int(max_rooms) if max_rooms else None
    min_size = float(min_size) if min_size else None
    max_size = float(max_size) if max_size else None
    is_verified = True if is_verified else None

    properties = filter_properties(
        search_type=search_type,
        query=query,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type,
        min_rooms=min_rooms,
        max_rooms=max_rooms,
        min_size=min_size,
        max_size=max_size,
        is_verified=is_verified,
    )
    return render(request, 'property_search.html', {'properties': properties})


@login_required
def property_verify(request, property_id):
    property_instance = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    if request.method == 'POST':
        if request.FILES.get('verification_file'):
            verification_file = request.FILES['verification_file']
            add_verification_file(property_instance, verification_file)
            messages.success(request, "Verification file uploaded successfully!")
            return redirect('property_verify', property_id=property_id)
        elif request.POST.get('delete_verification_file'):
            file_to_delete = request.POST['delete_verification_file']
            if delete_verification_file(property_instance, file_to_delete):
                messages.success(request, "Verification file deleted successfully!")
            else:
                messages.error(request, "File could not be deleted.")
            return redirect('property_verify', property_id=property_id)
    return render(request, 'property_verify.html', {'property': property_instance})


def property_detail_all(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    return render(request, 'property_detail_all.html', {
        'property': property_obj,
        'MEDIA_URL': settings.MEDIA_URL,
    })





