from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'required'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'required'}))

    class Meta:
        model = User
        fields = [
            'username', 'account_type', 'consent_to_share_location', 'full_name',
            'date_of_birth', 'email', 'password', 'confirm_password', 
            'phone_number', 'profile_photo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add 'required' attribute to mandatory fields
        self.fields['username'].widget.attrs.update({'required': 'required'})
        self.fields['account_type'].widget.attrs.update({'required': 'required'})
        self.fields['consent_to_share_location'].widget.attrs.update({'required': 'required'})
        self.fields['full_name'].widget.attrs.update({'required': 'required'})
        self.fields['date_of_birth'].widget.attrs.update({'required': 'required'})
        self.fields['email'].widget.attrs.update({'required': 'required'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")