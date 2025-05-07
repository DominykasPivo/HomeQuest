from django.db import models
from .payment_strategies import PaymentStrategy

class PaymentProcessor:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._strategy = None
        return cls._instance
  
    def set_strategy(self, strategy):
        self._strategy = strategy
    
    def process_payment(self, amount, **kwargs):
        if not self._strategy:
            raise Exception("Payment strategy not set.")
        return self._strategy.process_payment(amount, **kwargs)