from django import forms

class SubscriptionPurchaseForm(forms.Form):
    PAYMENT_METHODS = [
        ('card', 'Card'),
        ('iban', 'IBAN'),
        ('paypal', 'PayPal'),
    ]
    plan = forms.ChoiceField(label="Select Plan")
    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, label="Payment Method")

    def __init__(self, *args, plans=None, **kwargs):
        super().__init__(*args, **kwargs)
        if plans is not None:
            self.fields['plan'].choices = plans