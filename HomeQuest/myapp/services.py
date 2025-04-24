from .models import User, Buyer, Seller, GoldSeller
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils.timezone import now
import os
from django.conf import settings

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
    user = User.objects.create(
        username=kwargs.get('username'),
        email=kwargs.get('email'),
        full_name=kwargs.get('full_name'),
        date_of_birth=kwargs.get('date_of_birth'),
        consent_to_share_location=kwargs.get('consent_to_share_location'),
        phone_number=kwargs.get('phone_number'),
        profile_photo=kwargs.get('profile_photo'),
    )
    user.set_password(kwargs.get('password'))  # Set the hashed password
    user.save()

    # Assign role-specific profiles
    if user_type == 'buyer':
        Buyer.objects.create(user=user)
    elif user_type == 'seller':
        Seller.objects.create(user=user)

    return user

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
    if kwargs.get('username'):
        user.username = kwargs['username']
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


def get_or_create_gold_seller(user):
    """
    Get or create a GoldSeller instance for the given user.
    """
    gold_seller, created = GoldSeller.objects.get_or_create(
        user=user,
        defaults={
            'subscription_plan': 'basic',
            'subscription_end_date': None,  # Default to None for "Basic" plan
        }
    )
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