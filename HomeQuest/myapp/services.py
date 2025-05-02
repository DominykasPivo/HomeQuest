from .models import User, Buyer, Seller, GoldSeller, Property, PropertyLike, Comment, Notification
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils.timezone import now
import os
from django.conf import settings
import logging
from django.contrib.messages import get_messages
import shutil # for deleting directories
from django.db.models import Q
from django.db.models.query import QuerySet # for filtering properties
from django.core.files.uploadedfile import UploadedFile
import difflib # for comparing strings // for search bar finding similar properties

def clear_messages(request):
    """
    Clears all messages from the session.
    """
    storage = get_messages(request)
    for _ in storage:
        pass  # Consume and clear all messages



def create_user(user_type, **kwargs):
    """
    Create a user and assign a role (Buyer or Seller).
    """
    try:
        # Create the correct subclass directly!
        if user_type == 'buyer':
            user = Buyer.objects.create(
                email=kwargs.get('email'),
                full_name=kwargs.get('full_name'),
                date_of_birth=kwargs.get('date_of_birth'),
                consent_to_share_location=kwargs.get('consent_to_share_location'),
                phone_number=kwargs.get('phone_number'),
                profile_photo=kwargs.get('profile_photo'),
                blur_profile_photo=kwargs.get('blur_profile_photo'),  
            )
        elif user_type == 'seller':
            # Create a GoldSeller directly
            gold_seller = GoldSeller.objects.create(
                email=kwargs.get('email'),
                full_name=kwargs.get('full_name'),
                date_of_birth=kwargs.get('date_of_birth'),
                consent_to_share_location=kwargs.get('consent_to_share_location'),
                phone_number=kwargs.get('phone_number'),
                profile_photo=kwargs.get('profile_photo'),
                blur_profile_photo=kwargs.get('blur_profile_photo'),
                subscription_plan='basic',  # Default to basic
                subscription_end_date=None  # No subscription end date for basic
            )
            user = gold_seller  # The GoldSeller is also a User
        else:
            raise ValidationError("Invalid user type. Must be 'buyer' or 'seller'.")
        
        user.set_password(kwargs.get('password'))
        user.save()
        return user
    except Exception as e:
        raise

def update_user_profile(user, **kwargs):
    """
    Update the user's profile with the provided data.
    """
    # Validate email uniqueness only if a new email is provided
    new_email = kwargs.get('email')
    if new_email and new_email != user.email:
        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            raise ValidationError(f"The email '{new_email}' is already in use by another account.")

    # Validate phone number uniqueness only if a new phone number is provided
    new_phone_number = kwargs.get('phone_number')
    if new_phone_number and new_phone_number != user.phone_number:
        if User.objects.filter(phone_number=new_phone_number).exclude(id=user.id).exists():
            raise ValidationError(f"The phone number '{new_phone_number}' is already in use by another account.")
        
    # Delete the old profile photo if a new one is provided
    # Only update if a real file was uploaded

    # Update fields only if new values are provided and not empty
    if kwargs.get('full_name'):
        user.full_name = kwargs['full_name']
    if new_email:
        user.email = new_email
    if new_phone_number:
        user.phone_number = new_phone_number

    new_profile_photo = kwargs.get('profile_photo')
    if isinstance(new_profile_photo, UploadedFile): # 
        if new_profile_photo != user.profile_photo:
            old_photo_path = os.path.join(settings.MEDIA_ROOT, user.profile_photo.name)
            if os.path.exists(old_photo_path) and user.profile_photo.name != 'profile_photos/default-profile.png':
                os.remove(old_photo_path)
            user.profile_photo = new_profile_photo
        

    if 'date_of_birth' in kwargs and kwargs['date_of_birth']:
        user.date_of_birth = kwargs['date_of_birth']

    if 'blur_profile_photo' in kwargs:
        user.blur_profile_photo = kwargs['blur_profile_photo']

    if kwargs.get('password'): 
        user.set_password(kwargs['password']) # Hash the new password

    user.save()
    return user


def get_or_create_gold_seller(user, upgrade_to_gold=False):
    """
    Get the GoldSeller instance for the given user, or update it if upgrading.
    """
    # Ensure the user is a Seller
    try:
        seller = Seller.objects.get(pk=user.pk)
    except Seller.DoesNotExist:
        raise ValidationError("You must be a Seller to upgrade to Gold.")

    # Get the existing GoldSeller instance
    gold_seller = GoldSeller.objects.get(pk=seller.pk)

    # Upgrade to gold if requested
    if upgrade_to_gold:
        gold_seller.subscription_plan = 'gold'
        gold_seller.subscription_end_date = now().date() + timedelta(days=30)
        gold_seller.save()

    return gold_seller

def update_subscription(gold_seller, action):
    """
    Update the subscription plan and end date for a GoldSeller.
    """
    if action == 'buy_gold':
        gold_seller.subscription_plan = 'gold'
        gold_seller.subscription_end_date = now().date() + timedelta(days=30)  # 30-day subscription
    elif action == 'cancel_gold':
        gold_seller.subscription_plan = 'basic'
        gold_seller.subscription_end_date = None  # Clear the subscription end date
    gold_seller.save()


def save_property_image(property_instance, image):
    if not image:
        return []
    folder = f'property_images/property_{property_instance.property_id}'
    abs_folder = os.path.join(settings.MEDIA_ROOT, folder)
    os.makedirs(abs_folder, exist_ok=True)
    filename = image.name
    rel_path = os.path.join(folder, filename)
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    with open(abs_path, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    return [rel_path]


def create_property_for_seller(seller, property_data, image=None):
    """
    Create a property for a seller with the given data and an optional image.
    """
    if not isinstance(seller, Seller):
        raise ValidationError("Only sellers can create properties.")

    # Create and save the property instance
    property_instance = Property(
        seller=seller,
        location=property_data.get('location'),
        map_location=property_data.get('map_location'),
        price=property_data.get('price'),
        size=property_data.get('size'),
        room_num=property_data.get('room_num'),
        property_type=property_data.get('property_type'),
        listing_type=property_data.get('listing_type'),
        duration=property_data.get('duration'),
        is_verified=property_data.get('is_verified', False),
    )
    property_instance.save()  # Save the property to generate an ID

    if image:
        image_paths = save_property_image(property_instance, image)
        # Convert backslashes to forward slashes for JSON compatibility
        image_paths = [p.replace('\\', '/') for p in image_paths]
        try:
            property_instance.image_paths = image_paths
            property_instance.save()
        except Exception as e:
            raise


    return property_instance

def update_property(property_instance, property_data, image=None):
    """
    Update an existing property with new data and an optional image.
    """
    property_instance.location = property_data.get('location')
    property_instance.map_location = property_data.get('map_location')
    property_instance.price = property_data.get('price')
    property_instance.size = property_data.get('size')
    property_instance.room_num = property_data.get('room_num')
    property_instance.property_type = property_data.get('property_type')
    property_instance.is_verified = property_data.get('is_verified', False)
    property_instance.save()

    # Handle the uploaded image
    property_instance.location = property_data.get('location')
    property_instance.map_location = property_data.get('map_location')
    property_instance.price = property_data.get('price')
    property_instance.size = property_data.get('size')
    property_instance.room_num = property_data.get('room_num')
    property_instance.property_type = property_data.get('property_type')
    property_instance.listing_type = property_data.get('listing_type')
    property_instance.is_verified = property_data.get('is_verified', False)
    property_instance.save()

    # Handle the uploaded images
    if image:
        image_paths = property_instance.image_paths or []
        for img in image:
            new_paths = save_property_image(property_instance, img)
            image_paths.extend([p.replace('\\', '/') for p in new_paths])
        property_instance.image_paths = image_paths
        property_instance.save()

    return property_instance
def delete_property(property_instance):
    """
    Delete a property instance and its image folder.
    """
    # Delete the property images folder
    folder = f'property_images/property_{property_instance.property_id}'
    abs_folder = os.path.join(settings.MEDIA_ROOT, folder)
    if os.path.exists(abs_folder):
        shutil.rmtree(abs_folder)
    # Delete the property itself
    if property_instance.verification_files:
        verification_folder = f'property_verifications/property_{property_instance.property_id}'
        abs_verification_folder = os.path.join(settings.MEDIA_ROOT, verification_folder)
        if os.path.exists(abs_verification_folder):
            shutil.rmtree(abs_verification_folder)

    property_instance.delete()


def delete_property_image(property_instance, image_to_delete):
    image_paths = property_instance.image_paths or []
    if image_to_delete in image_paths:
        image_full_path = os.path.join(settings.MEDIA_ROOT, image_to_delete)
        if os.path.exists(image_full_path):
            os.remove(image_full_path)
        image_paths.remove(image_to_delete)
        property_instance.image_paths = image_paths
        property_instance.save()
    return property_instance

def replace_property_image(property_instance, image_to_replace, new_image, save_property_image_func):
    image_paths = property_instance.image_paths or []
    if image_to_replace in image_paths and new_image:
        idx = image_paths.index(image_to_replace)
        old_image_full_path = os.path.join(settings.MEDIA_ROOT, image_to_replace)
        if os.path.exists(old_image_full_path):
            os.remove(old_image_full_path)
        new_path = save_property_image_func(property_instance, new_image)[0].replace('\\', '/')
        image_paths[idx] = new_path
        property_instance.image_paths = image_paths
        property_instance.save()
    return property_instance

def add_property_image(property_instance, new_image, save_property_image_func):
    if new_image:
        image_paths = property_instance.image_paths or []
        new_path = save_property_image_func(property_instance, new_image)[0].replace('\\', '/')
        image_paths.append(new_path)
        property_instance.image_paths = image_paths
        property_instance.save()
    return property_instance

def filter_properties(
    search_type=None, query=None, min_price=None, max_price=None,
    property_type=None, min_rooms=None, max_rooms=None, min_size=None, max_size=None,
    is_verified=None, seller_id=None, min_duration=None, max_duration=None, limit=None, sort_by=None
):
    properties = Property.objects.all()

    if search_type == 'for_rent':
        properties = properties.filter(listing_type='for_rent')
    elif search_type == 'for_sale':
        properties = properties.filter(listing_type='for_sale')
    elif search_type == 'recommended':
        properties = properties.order_by('-like_count', '-view_count', '-comment_count')

    if property_type:
        properties = properties.filter(property_type=property_type)
    if min_rooms:
        properties = properties.filter(room_num__gte=min_rooms)
    if max_rooms:
        properties = properties.filter(room_num__lte=max_rooms)
    if min_size:
        properties = properties.filter(size__gte=min_size)
    if max_size:
        properties = properties.filter(size__lte=max_size)
    if is_verified is not None:
        properties = properties.filter(is_verified=is_verified)
    if seller_id:
        properties = properties.filter(seller__pk=seller_id)
    if min_duration:
        properties = properties.filter(duration__gte=min_duration)
    if max_duration:
        properties = properties.filter(duration__lte=max_duration)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)

    # Fuzzy location search (after all filters)
    if query:
        locations = list(properties.values_list('location', flat=True))
        map_locations = list(properties.values_list('map_location', flat=True))
        all_locations = list(set(locations + map_locations))
        closest = difflib.get_close_matches(query, all_locations, n=10, cutoff=0.5)
        if closest:
            filtered = properties.filter(
                Q(location__in=closest) | Q(map_location__in=closest)
            )
            def similarity_key(obj):
                best = 0
                for field in [obj.location, obj.map_location]:
                    for match in closest:
                        ratio = difflib.SequenceMatcher(None, query, field or '').ratio()
                        if ratio > best:
                            best = ratio
                return -best
            properties = sorted(filtered, key=similarity_key)
        else:
            properties = properties.filter(
                Q(location__icontains=query) | Q(map_location__icontains=query)
            )

    
    # Sorting logic for filtered results
    if isinstance(properties, QuerySet):
        if sort_by == 'most_viewed':
            properties = properties.order_by('-view_count')
        elif sort_by == 'most_commented':
            properties = properties.order_by('-comment_count')
        elif sort_by == 'most_liked':
            properties = properties.order_by('-like_count')
        elif search_type in ('for_sale', 'for_rent'):
            properties = properties.order_by('-like_count', '-view_count', '-comment_count')
    elif isinstance(properties, list) and sort_by:
        if sort_by == 'most_viewed':
            properties.sort(key=lambda x: x.view_count, reverse=True)
        elif sort_by == 'most_commented':
            properties.sort(key=lambda x: x.comment_count, reverse=True)
        elif sort_by == 'most_liked':
            properties.sort(key=lambda x: x.like_count, reverse=True)


    if limit is not None:
        if isinstance(properties, list):
            return properties[:limit]
        return properties[:limit]
    return properties

def save_verification_file(property_instance, file):
    folder = f'property_verifications/property_{property_instance.property_id}'
    abs_folder = os.path.join(settings.MEDIA_ROOT, folder)
    os.makedirs(abs_folder, exist_ok=True)
    filename = file.name
    rel_path = os.path.join(folder, filename)
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    with open(abs_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return rel_path.replace('\\', '/')

def add_verification_file(property_instance, file):
    if file:
        verification_files = property_instance.verification_files or []
        new_path = save_verification_file(property_instance, file)
        verification_files.append(new_path)
        property_instance.verification_files = verification_files
        property_instance.is_verified = True
        property_instance.save()
    return property_instance

def delete_verification_file(property_instance, file_to_delete):
    verification_files = property_instance.verification_files or []
    if file_to_delete in verification_files:
        abs_path = os.path.join(settings.MEDIA_ROOT, file_to_delete)
        if os.path.exists(abs_path):
            os.remove(abs_path)
        verification_files.remove(file_to_delete)
        property_instance.verification_files = verification_files
        # If no files left, unverify and remove the folder
        if not verification_files:
            property_instance.is_verified = False
            # Remove the property verification folder
            folder = os.path.dirname(abs_path)
            if os.path.exists(folder):
                shutil.rmtree(folder)
        property_instance.save()
        return True
    return False

def toggle_like(property_obj, user):
    """Like or unlike a property for a user. Returns True if liked, False if unliked."""
    like, created = PropertyLike.objects.get_or_create(property=property_obj, user=user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    # Update like_count
    property_obj.like_count = property_obj.likes.count()
    property_obj.save(update_fields=['like_count'])
    return liked

def add_comment(property_obj, user, text):
    """Add a comment to a property and update comment_count."""
    comment = Comment.objects.create(property=property_obj, user=user, text=text)
    property_obj.comment_count = property_obj.comments.count()
    property_obj.save(update_fields=['comment_count'])
    return comment

def create_notification(user, message):
    Notification.objects.create(user=user, message=message)