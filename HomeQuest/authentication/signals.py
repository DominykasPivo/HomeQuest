from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .services import ensure_user_has_2fa

User = get_user_model()

@receiver(post_save, sender=User)
def post_save_generate_code(sender, instance, created, **kwargs):
    if created:
        ensure_user_has_2fa(instance)