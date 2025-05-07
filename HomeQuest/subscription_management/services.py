from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import GoldSeller
from user_management.models import Seller
from django.core.exceptions import ValidationError
from django.utils.timezone import now
import os

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

def update_subscription(gold_seller, action, plan_key=None):
    """
    Update the subscription plan and end date for a GoldSeller.
    """
    if action == 'buy_gold' and plan_key:
        gold_seller.subscription_type = 'gold'
        gold_seller.subscription_plan = plan_key
        days = {
            'weekly': 7,
            'monthly': 30,
            'quarterly': 90,
            'yearly': 365,
        }.get(plan_key, 30)
        gold_seller.subscription_end_date = now().date() + timedelta(days=days)
    elif action == 'cancel_gold':
        gold_seller.subscription_type = 'basic'
        gold_seller.subscription_plan = 'basic'
        gold_seller.subscription_end_date = None
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

def auto_downgrade_if_expired(gold_seller):
    if not gold_seller.is_subscription_active():
        gold_seller.subscription_type = 'basic'
        gold_seller.subscription_plan = 'basic'
        gold_seller.subscription_end_date = None
        gold_seller.save()

def cancel_subscription(gold_seller):
    gold_seller.subscription_plan = 'basic'
    gold_seller.subscription_type = 'basic'
    gold_seller.subscription_end_date = None
    gold_seller.save()