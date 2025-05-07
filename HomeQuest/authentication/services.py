import random
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.messages import get_messages
from django_otp.plugins.otp_email.models import EmailDevice

def clear_messages(request):
    """
    Clears all messages from the session.
    """
    storage = get_messages(request)
    for _ in storage:
        pass  

def ensure_user_has_2fa(user):
    device, created = EmailDevice.objects.get_or_create(
        user=user,
        name='default',
        defaults={'confirmed': True}  
    )
    
    
    if not device.confirmed:
        device.confirmed = True
        device.save()
        
    return device

def generate_2fa(user, target_email=None):
    device = ensure_user_has_2fa(user) 
    if target_email and target_email != user.email:
        token = str(random.randint(100000, 999999))  
        send_mail(
            subject=settings.OTP_EMAIL_SUBJECT,
            message=f"Your verification code is: {token}\nUse this code to verify your new email address.",
            from_email=settings.OTP_EMAIL_SENDER,
            recipient_list=[target_email],
            fail_silently=False,
        )
        return token
    else:
        device.generate_challenge()
        return True

def verify_2fa_token(user, token):
    device = EmailDevice.objects.filter(user=user, name='default').first()
    if device and device.verify_token(token):
        return True
    return False