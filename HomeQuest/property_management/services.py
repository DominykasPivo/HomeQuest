import os
import shutil
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Property, PropertyLike, Comment
from user_management.models import User, Seller
from notification_system.services import create_notification
from subscription_management.models import GoldSeller
import difflib
from authentication.real_auth import RealAuthenticationSystem
from authentication.proxy import AuthenticationProxy

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
    # Check if seller can add more property (Gold sellers can add unlimited, basic sellers are limited to 2)
    property_count = Property.objects.filter(seller=seller).count()
    
    gold_seller = GoldSeller.objects.filter(pk=seller.pk).first()
    if not gold_seller or not (gold_seller.subscription_type == 'gold' and gold_seller.is_subscription_active()):
        if property_count >= 2:
            raise ValidationError("Basic sellers can list a maximum of 2 properties. Upgrade to Gold for unlimited listings.")

    # Create the property instance
    property_instance = Property.objects.create(
        seller=seller,
        location=property_data.get('location'),
        map_location=property_data.get('map_location'),
        price=property_data.get('price'),
        size=property_data.get('size'),
        room_num=property_data.get('room_num'),
        property_type=property_data.get('property_type'),
        listing_type=property_data.get('listing_type'),
        duration=property_data.get('duration', 0),
        image_paths=[],
    )

    # If image was provided, save it and update the property
    if image:
        image_paths = save_property_image(property_instance, image)
        try:
            property_instance.image_paths = image_paths
            property_instance.save()
        except Exception as e:
            raise

    return property_instance

def delete_property_image(property_instance, image_path):
    """Delete a property image file and remove it from the property's image_paths"""
    try:
        # Get the absolute path
        abs_path = os.path.join(settings.MEDIA_ROOT, image_path)
        
        # Check if the file exists and delete it
        if os.path.exists(abs_path):
            os.remove(abs_path)
            
        # Remove the path from the property's image_paths
        if image_path in property_instance.image_paths:
            property_instance.image_paths.remove(image_path)
            property_instance.save()
            
        return True, True  # Success, deleted
    except Exception as e:
        return False, False  # Error

def replace_property_image(property_instance, old_image_path, new_image, save_image_func):
    """Replace a property image with a new one"""
    try:
        # First delete the old image
        delete_success, _ = delete_property_image(property_instance, old_image_path)
        
        if delete_success and new_image:
            # Save the new image
            new_paths = save_image_func(property_instance, new_image)
            
            # Update the property's image_paths
            if old_image_path in property_instance.image_paths:
                idx = property_instance.image_paths.index(old_image_path)
                property_instance.image_paths[idx] = new_paths[0]
            else:
                property_instance.image_paths.extend(new_paths)
                
            property_instance.save()
            return True
        
        return False
    except Exception as e:
        return False

def add_property_image(property_instance, image):
    """Add an additional image to a property"""
    if not image:
        return False
    
    try:
        new_paths = save_property_image(property_instance, image)
        property_instance.image_paths.extend(new_paths)
        property_instance.save()
        return True
    except Exception:
        return False

def delete_property(property_instance):
    """Delete a property and all its associated files"""
    try:
        # Delete all images
        for image_path in property_instance.image_paths:
            abs_path = os.path.join(settings.MEDIA_ROOT, image_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)
        
        # Delete property folder
        property_folder = f'property_images/property_{property_instance.property_id}'
        abs_folder = os.path.join(settings.MEDIA_ROOT, property_folder)
        if os.path.exists(abs_folder):
            shutil.rmtree(abs_folder)
        
        # Delete verification files
        for file_path in property_instance.verification_files:
            abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)
        
        # Delete the property from database
        property_instance.delete()
        return True
    except Exception as e:
        raise

def add_verification_file(property_instance, file):
    """Add a verification file to a property"""
    if not file:
        return False
    
    try:
        folder = f'verification_files/property_{property_instance.property_id}'
        abs_folder = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(abs_folder, exist_ok=True)
        
        filename = file.name
        rel_path = os.path.join(folder, filename)
        abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
        
        with open(abs_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        property_instance.verification_files.append(rel_path)
        property_instance.save()
        return True
    except Exception:
        return False

def delete_verification_file(property_instance, file_path):
    """Delete a verification file"""
    try:
        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(abs_path):
            os.remove(abs_path)
        
        if file_path in property_instance.verification_files:
            property_instance.verification_files.remove(file_path)
            property_instance.save()
        
        return True
    except Exception:
        return False

def toggle_like(property_instance, user):
    """Toggle like/unlike for a property"""
    try:
        like, created = PropertyLike.objects.get_or_create(property=property_instance, user=user)
        
        if created:
            # User liked the property
            property_instance.like_count += 1
            property_instance.save(update_fields=['like_count'])
            
            # Notify the seller about the like
            notification_message = f"Someone liked your property at {property_instance.location}"
            create_notification(property_instance.seller.user, notification_message)
            
            return True
        else:
            # User already liked the property, so unlike it
            like.delete()
            property_instance.like_count = max(0, property_instance.like_count - 1)
            property_instance.save(update_fields=['like_count'])
            return False
    except Exception as e:
        raise

def add_comment(property_instance, user, text):
    """Add a comment to a property"""
    try:
        comment = Comment.objects.create(
            property=property_instance,
            user=user,
            text=text
        )
        
        # Update comment count
        property_instance.comment_count += 1
        property_instance.save(update_fields=['comment_count'])
        
        # Notify the seller about the comment
        notification_message = f"Someone commented on your property at {property_instance.location}"
        create_notification(property_instance.seller.user, notification_message)
        
        return comment
    except Exception as e:
        raise


def filter_properties(
    search_type=None, query=None, min_price=None, max_price=None,
    property_type=None, min_rooms=None, max_rooms=None, min_size=None, max_size=None,
    is_verified=None, seller_id=None, min_duration=None, max_duration=None, limit=None, sort_by=None
):
    properties = Property.objects.all()

    # Apply sorting first
    if sort_by:
        if sort_by == 'most_viewed':
            properties = properties.order_by('-view_count')
        elif sort_by == 'most_commented':
            properties = properties.order_by('-comment_count')
        elif sort_by == 'most_liked':
            properties = properties.order_by('-like_count')

    # Apply other filters only if they have actual values
    if search_type and search_type != '':
        if search_type == 'for_rent':
            properties = properties.filter(listing_type='for_rent')
        elif search_type == 'for_sale':
            properties = properties.filter(listing_type='for_sale')
        elif search_type == 'recommended':
            if not sort_by:  # Only apply recommended sorting if no explicit sort is specified
                properties = properties.order_by('-like_count', '-view_count', '-comment_count')

    if property_type and property_type != '':
        properties = properties.filter(property_type=property_type)
    if min_rooms and str(min_rooms).strip():
        properties = properties.filter(room_num__gte=min_rooms)
    if max_rooms and str(max_rooms).strip():
        properties = properties.filter(room_num__lte=max_rooms)
    if min_size and str(min_size).strip():
        properties = properties.filter(size__gte=min_size)
    if max_size and str(max_size).strip():
        properties = properties.filter(size__lte=max_size)
    if is_verified:
        properties = properties.filter(is_verified=True)
    if seller_id:
        properties = properties.filter(seller__pk=seller_id)
    if min_duration and str(min_duration).strip():
        properties = properties.filter(duration__gte=min_duration)
    if max_duration and str(max_duration).strip():
        properties = properties.filter(duration__lte=max_duration)
    if min_price and str(min_price).strip():
        properties = properties.filter(price__gte=min_price)
    if max_price and str(max_price).strip():
        properties = properties.filter(price__lte=max_price)

    # Fuzzy location search (after all filters)
    if query and query.strip():
        locations = list(properties.values_list('location', flat=True))
        map_locations = list(properties.values_list('map_location', flat=True))
        all_locations = list(set(locations + map_locations))
        
        closest = difflib.get_close_matches(query, all_locations, n=5, cutoff=0.5)
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

    if limit is not None:
        if isinstance(properties, list):
            return properties[:limit]
        return properties[:limit]
    return properties

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

    
    if len(image_paths) <= 1:
        return property_instance, False
    
    if image_to_delete in image_paths:
        image_full_path = os.path.join(settings.MEDIA_ROOT, image_to_delete)
        if os.path.exists(image_full_path):
            os.remove(image_full_path)
        image_paths.remove(image_to_delete)
        property_instance.image_paths = image_paths
        property_instance.save()
        return property_instance, True
    return property_instance, False

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

    # Apply sorting first
    if sort_by:
        if sort_by == 'most_viewed':
            properties = properties.order_by('-view_count')
        elif sort_by == 'most_commented':
            properties = properties.order_by('-comment_count')
        elif sort_by == 'most_liked':
            properties = properties.order_by('-like_count')

    # Apply other filters only if they have actual values
    if search_type and search_type != '':
        if search_type == 'for_rent':
            properties = properties.filter(listing_type='for_rent')
        elif search_type == 'for_sale':
            properties = properties.filter(listing_type='for_sale')
        elif search_type == 'recommended':
            if not sort_by:  # Only apply recommended sorting if no explicit sort is specified
                properties = properties.order_by('-like_count', '-view_count', '-comment_count')

    if property_type and property_type != '':
        properties = properties.filter(property_type=property_type)
    if min_rooms and str(min_rooms).strip():
        properties = properties.filter(room_num__gte=min_rooms)
    if max_rooms and str(max_rooms).strip():
        properties = properties.filter(room_num__lte=max_rooms)
    if min_size and str(min_size).strip():
        properties = properties.filter(size__gte=min_size)
    if max_size and str(max_size).strip():
        properties = properties.filter(size__lte=max_size)
    if is_verified:
        properties = properties.filter(is_verified=True)
    if seller_id:
        properties = properties.filter(seller__pk=seller_id)
    if min_duration and str(min_duration).strip():
        properties = properties.filter(duration__gte=min_duration)
    if max_duration and str(max_duration).strip():
        properties = properties.filter(duration__lte=max_duration)
    if min_price and str(min_price).strip():
        properties = properties.filter(price__gte=min_price)
    if max_price and str(max_price).strip():
        properties = properties.filter(price__lte=max_price)

    # Fuzzy location search (after all filters)
    if query and query.strip():
        locations = list(properties.values_list('location', flat=True))
        map_locations = list(properties.values_list('map_location', flat=True))
        all_locations = list(set(locations + map_locations))
        closest = difflib.get_close_matches(query, all_locations, n=5, cutoff=0.5)
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
        auth_system = AuthenticationProxy(RealAuthenticationSystem())
        auth_system.verify_property(property_instance)
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
