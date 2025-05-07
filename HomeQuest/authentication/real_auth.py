from .interfaces import IAuthenticationSystem
from django.contrib.auth import authenticate
from authentication.services import generate_2fa, verify_2fa_token
from user_management.models import User

class RealAuthenticationSystem(IAuthenticationSystem):
    _instance = None

    def new(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RealAuthenticationSystem, cls).new(cls)
        return cls._instance
    
    def email_authenticate_user(self, request, email, password):
        return authenticate(request, email=email, password=password)

    def phone_num_authenticate_user(self, request, phone_number, password):
        try:
            user = User.objects.get(phone_number=phone_number)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def send_email_authentication_code(self, user, email):
        generate_2fa(user, target_email=email)
        return True

    def send_phone_num_authentication_code(self, phone_number):
        # Cant implement SMS logic since we have to pay for it
        pass

    def verify_code(self, user, code):
        return verify_2fa_token(user, code)

    def verify_property(self, property_obj):
        property_obj.is_verified = True
        property_obj.save()