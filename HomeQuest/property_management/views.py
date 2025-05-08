from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.utils.translation import gettext_lazy as _

from .models import Property, PropertyLike, Comment
from .forms import PropertyForm, CommentForm
from .services import (
    create_property_for_seller, delete_property, delete_property_image, 
    replace_property_image, add_property_image, save_property_image,
    filter_properties, add_verification_file, delete_verification_file,
    toggle_like, add_comment
)
from user_management.models import Seller
from notification_system.services import create_notification
from subscription_management.models import GoldSeller

@login_required
def create_property(request):
    try:
        seller = Seller.objects.get(pk=request.user.pk)
    except Seller.DoesNotExist:
        messages.error(request, "Only sellers can create properties.")
        return redirect('home')
    
    property_count = Property.objects.filter(seller=seller).count()
    gold_seller = GoldSeller.objects.filter(pk=seller.pk).first()

    if gold_seller and gold_seller.subscription_type == 'gold' and gold_seller.is_subscription_active():
        is_gold_seller = True
    else:
        is_gold_seller = False
    if request.method == 'POST':

        if not is_gold_seller:
            property_count = Property.objects.filter(seller=seller).count()
            if property_count >= 2:
                messages.error(request, "Basic sellers can list a maximum of 2 properties. Upgrade to Gold for unlimited listings.")
                return redirect('manage_subscription')
            
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                create_property_for_seller(
                    seller=seller,
                    property_data=form.cleaned_data,
                    image=form.cleaned_data.get('image')
                )
                create_notification(request.user, "Your property was created successfully!")
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

    return render(request, 'property_create.html', {'form': form, 
                                                    'property_count': property_count,
                                                    'is_gold_seller': is_gold_seller,})

@login_required
def property_list(request):
    seller = get_object_or_404(Seller, pk=request.user.pk)
    properties = Property.objects.filter(seller=seller)
    return render(request, 'property_list.html', {'properties': properties,})

@login_required
def property_detail(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    return render(request, 'property_detail.html', {
        'property': property_obj,
    })

@login_required
def property_edit(request, property_id):
    property_instance = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    form = PropertyForm(request.POST or None, request.FILES or None, instance=property_instance)

    if request.method == 'POST':
        # Delete image
        if 'delete_image' in request.POST:
            image_to_delete = request.POST['delete_image']
            _, deleted = delete_property_image(property_instance, image_to_delete)
            if deleted:
                messages.success(request, "Image deleted successfully!")
            else:
                messages.error(request, "Image could not be deleted.")
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
                create_notification(request.user, "Your property was updated successfully!")
                messages.success(request, "Property updated successfully!")
                return redirect('property_detail', property_id=property_instance.pk)
            else:
                messages.error(request, "There was an error updating the property.")

    return render(request, 'property_edit.html', {
        'form': form,
        'property': property_instance
    })

@login_required
def property_delete(request, property_id):
    property_instance = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    if request.method == 'POST':
        try:
            delete_property(property_instance)
            create_notification(request.user, "Your property was deleted successfully!")
            messages.success(request, "Property deleted successfully!")
            return redirect('property_list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return render(request, 'property_delete.html', {'property': property_instance})

def property_search(request):
    search_type = request.GET.get('search_type', '')
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    property_type = request.GET.get('property_type', '')
    min_rooms = request.GET.get('min_rooms', '')
    max_rooms = request.GET.get('max_rooms', '')
    min_size = request.GET.get('min_size', '')
    max_size = request.GET.get('max_size', '')
    min_duration = request.GET.get('min_duration', '')  
    max_duration = request.GET.get('max_duration', '') 
    is_verified = request.GET.get('is_verified', '')
    sort_by = request.GET.get('sort_by', '')

    # Convert values to correct types only if they're not empty
    min_price = float(min_price) if min_price.strip() else None
    max_price = float(max_price) if max_price.strip() else None
    min_rooms = int(min_rooms) if min_rooms.strip() else None
    max_rooms = int(max_rooms) if max_rooms.strip() else None
    min_size = float(min_size) if min_size.strip() else None
    max_size = float(max_size) if max_size.strip() else None
    min_duration = int(min_duration) if min_duration.strip() else None  
    max_duration = int(max_duration) if max_duration.strip() else None  
    is_verified = True if is_verified else None

    filter_params = {
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'property_type': property_type,
        'min_rooms': min_rooms,
        'max_rooms': max_rooms,
        'min_size': min_size,
        'max_size': max_size,
        'is_verified': is_verified,
        'sort_by': sort_by if sort_by.strip() else None,
        'search_type': search_type if search_type.strip() else None
    }

    # Filtered properties (matching the user's filters)
    filtered_properties = filter_properties(**filter_params)

    # Three blocks sorted by popularity
    for_sale_properties = filter_properties(
        search_type='for_sale',
        limit=10,
    )

    for_rent_properties = filter_properties(
        search_type='for_rent',
        limit=10,
    )

    recommended_properties = filter_properties(
        search_type='recommended',
        limit=10,
    )

    return render(request, 'property_search.html', {
        'filtered_properties': filtered_properties,
        'for_sale_properties': for_sale_properties,
        'for_rent_properties': for_rent_properties,
        'recommended_properties': recommended_properties
    })


@login_required
def property_verify(request, property_id):
    property_instance = get_object_or_404(Property, pk=property_id, seller__pk=request.user.pk)
    if request.method == 'POST':
        if request.FILES.get('verification_file'):
            verification_file = request.FILES['verification_file']
            add_verification_file(property_instance, verification_file)
            messages.success(request, "Verification file uploaded successfully!")
            create_notification(request.user, "Your verification file was uploaded successfully!")
            return redirect('property_verify', property_id=property_id)
        elif request.POST.get('delete_verification_file'):
            file_to_delete = request.POST['delete_verification_file']
            if delete_verification_file(property_instance, file_to_delete):
                messages.success(request, "Verification file deleted successfully!")
            else:
                messages.error(request, "File could not be deleted.")
            create_notification(request.user, "Your verification file was deleted successfully!")
            return redirect('property_verify', property_id=property_id)
    return render(request, 'property_verify.html', {'property': property_instance})

def property_detail_all(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    if request.method == 'GET':
        property_obj.view_count += 1
        property_obj.save(update_fields=['view_count'])

    comments = property_obj.comments.select_related('user').order_by('created_at')
    comment_form = CommentForm()

    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = property_obj.likes.filter(user=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'like' in request.POST:
            toggle_like(property_obj, request.user)
            return redirect('property_detail_all', property_id=property_id)
        else:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                add_comment(property_obj, request.user, comment_form.cleaned_data['text'])
                return redirect('property_detail_all', property_id=property_id)

    return render(request, 'property_detail_all.html', {
        'property': property_obj,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked,
    })

def properties_for_sale(request):
    properties = filter_properties(search_type='for_sale')
    paginator = Paginator(properties, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'properties_list.html', {
        'page_obj': page_obj,
        'section_title': _('Properties For Sale')
    })

def properties_for_rent(request):
    properties = filter_properties(search_type='for_rent')
    paginator = Paginator(properties, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'properties_list.html', {
        'page_obj': page_obj,
        'section_title': _('Properties For Rent')
    })

def properties_recommended(request):
    properties = filter_properties(search_type='recommended')
    paginator = Paginator(properties, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'properties_list.html', {
        'page_obj': page_obj,
        'section_title': _('Recommended Properties')
    })