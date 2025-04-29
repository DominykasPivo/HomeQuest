from .models import User, Buyer, Seller, GoldSeller, Property
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils.timezone import now
import os
from django.conf import settings
import logging
from django.contrib.messages import get_messages
import shutil # for deleting directories

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
                subscription_plan='basic',  # Default to basic
                subscription_end_date=None  # No subscription end date for basic
            )
            user = gold_seller  # The GoldSeller is also a User
        else:
            raise ValidationError("Invalid user type. Must be 'buyer' or 'seller'.")
        
        # elif user_type == 'seller':
        #     seller = Seller.objects.create(
        #         email=kwargs.get('email'),
        #         full_name=kwargs.get('full_name'),
        #         date_of_birth=kwargs.get('date_of_birth'),
        #         consent_to_share_location=kwargs.get('consent_to_share_location'),
        #         phone_number=kwargs.get('phone_number'),
        #         profile_photo=kwargs.get('profile_photo'),
        #     )
        #     # Automatically create a GoldSeller with default subscription plan
        #     gold_seller = GoldSeller.objects.create(
        #         seller_ptr=seller,  # Link to the existing Seller
        #         subscription_plan='basic',  # Default to basic
        #         subscription_end_date=None  # No subscription end date for basic
        #     )
        #     gold_seller.save(force_insert=False)  # Avoid creating a new parent row
        #     user = seller
        # else:
        #     user = User.objects.create(
        #         email=kwargs.get('email'),
        #         full_name=kwargs.get('full_name'),
        #         date_of_birth=kwargs.get('date_of_birth'),
        #         consent_to_share_location=kwargs.get('consent_to_share_location'),
        #         phone_number=kwargs.get('phone_number'),
        #         profile_photo=kwargs.get('profile_photo'),
        #     )
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
    new_profile_photo = kwargs.get('profile_photo')
    if new_profile_photo and new_profile_photo != user.profile_photo:
        old_photo_path = os.path.join(settings.MEDIA_ROOT, user.profile_photo.name)
        if os.path.exists(old_photo_path) and user.profile_photo.name != 'profile_photos/default-profile.png':
            os.remove(old_photo_path)

    # Update fields only if new values are provided and not empty
    if kwargs.get('full_name'):
        user.full_name = kwargs['full_name']
    if new_email:
        user.email = new_email
    if new_phone_number:
        user.phone_number = new_phone_number
    if new_profile_photo:
        user.profile_photo = new_profile_photo
    if kwargs.get('password'): 
        user.password = user.set_password(kwargs['password'])  # Hash the new password

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
        is_verified=property_data.get('is_verified', False),
    )
    property_instance.save()  # Save the property to generate an ID
    print("DEBUG: Property instance saved")

    if image:
        print("DEBUG: Image is present, calling save_property_image")
        image_paths = save_property_image(property_instance, image)
        print(f"DEBUG: Image paths: {image_paths}")
        # Convert backslashes to forward slashes for JSON compatibility
        image_paths = [p.replace('\\', '/') for p in image_paths]
        print(f"DEBUG: About to assign images: {image_paths} (type: {type(image_paths)})")
        try:
            property_instance.image_paths = image_paths
            property_instance.save()
            print("DEBUG: Image saved and property_instance updated")
        except Exception as e:
            print(f"DEBUG: Exception on property_instance.save(): {e}")
            raise
        print("asd")


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