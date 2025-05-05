from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from user_management.models import Buyer, Seller
from subscription_management.models import GoldSeller
from django.core.files.uploadedfile import UploadedFile
import os
from django.conf import settings
User = get_user_model()

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
            gold_seller = GoldSeller.objects.create(
                email=kwargs.get('email'),
                full_name=kwargs.get('full_name'),
                date_of_birth=kwargs.get('date_of_birth'),
                consent_to_share_location=kwargs.get('consent_to_share_location'),
                phone_number=kwargs.get('phone_number'),
                profile_photo=kwargs.get('profile_photo'),
                blur_profile_photo=kwargs.get('blur_profile_photo'),
                subscription_type='basic',      
                subscription_plan='basic',      
                subscription_end_date=None
            )
            user = gold_seller
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
        return {'status': 'verify_email',
                'new_email': new_email,
                'other_data': kwargs  # Store other form data for later update
                }

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
    return {'status': 'updated'}
