from abc import ABC, abstractmethod

class IAuthenticationSystem(ABC):
    @abstractmethod
    def email_authenticate_user(self, request, email, password):
        pass

    @abstractmethod
    def phone_num_authenticate_user(self, request, phone_number, password):
        pass

    @abstractmethod
    def send_email_authentication_code(self, user, email):
        pass

    @abstractmethod
    def send_phone_num_authentication_code(self, phone_number):
        pass

    @abstractmethod
    def verify_code(self, user, code):
        pass

    @abstractmethod
    def verify_property(self, property_obj):
        pass