from .interfaces import IAuthenticationSystem

class AuthenticationProxy(IAuthenticationSystem):
    def __init__(self, real_auth_system):
        self.real_auth_system = real_auth_system

    def email_authenticate_user(self, request, email, password):
        return self.real_auth_system.email_authenticate_user(request, email, password)

    def phone_num_authenticate_user(self, request, phone_number, password):
        return self.real_auth_system.phone_num_authenticate_user(request, phone_number, password)

    def send_email_authentication_code(self, user, email):
        return self.real_auth_system.send_email_authentication_code(user, email)

    def send_phone_num_authentication_code(self, phone_number):
        return self.real_auth_system.send_phone_num_authentication_code(phone_number)

    def verify_code(self, user, code):
        return self.real_auth_system.verify_code(user, code)

    def verify_property(self, property_obj):
        return self.real_auth_system.verify_property(property_obj)