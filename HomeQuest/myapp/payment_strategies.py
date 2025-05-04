from abc import ABC, abstractmethod
class PaymentStrategy(ABC): # This is an abstract base class for payment strategies // ABC stands for Abstract Base Class
    @abstractmethod
    def pay(self, amount, **kwargs):
        pass

class CardPayment(PaymentStrategy):
    def pay(self, amount, **kwargs):
        card_number = kwargs.get('card_number')
        full_name = kwargs.get('full_name')
        expiration_date = kwargs.get('expiration_date')
        cvv = kwargs.get('cvv')
        # Validate fields and process payment
        print(f"Processing card payment of {amount} for {full_name} with card {card_number}")
        return True

class IBANPayment(PaymentStrategy):
    def pay(self, amount, **kwargs):
        iban = kwargs.get('iban')
        full_name = kwargs.get('full_name')
        bank_name = kwargs.get('bank_name')
        bic = kwargs.get('bic')
        # Validate fields and process payment
        print(f"Processing IBAN payment of {amount} for {full_name} at {bank_name} (IBAN: {iban}, BIC: {bic})")
        return True

class PayPalPayment(PaymentStrategy):
    def pay(self, amount, **kwargs):
        paypal_email = kwargs.get('paypal_email')
        paypal_password = kwargs.get('paypal_password')
        # Validate fields and process payment
        print(f"Processing PayPal payment of {amount} for {paypal_email}")
        return True