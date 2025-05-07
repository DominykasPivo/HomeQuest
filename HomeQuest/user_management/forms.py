from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': ''}),
        label="Full Name",
        help_text=""  # Remove the default help text
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date of Birth"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'required': 'required'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'required': 'required'}),
        label="Confirm Password"
    )

    user_type = forms.ChoiceField(
        choices=[('buyer', 'Buyer'), ('seller', 'Seller')],
        widget=forms.RadioSelect,
        required=True
    )
    blur_profile_photo = forms.BooleanField(
        required=False,
        label="Blur my profile photo",
        help_text="If checked, your profile photo will be blurred for privacy."
    )

    class Meta:
        model = User
        fields = [
            'full_name', 'consent_to_share_location',
            'date_of_birth', 'email', 'password', 'confirm_password',
            'phone_number', 'profile_photo', 'blur_profile_photo'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError ("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            if not re.match(r'^\+?[\d\s\-\(\)]{8,15}$', phone_number):
                raise forms.ValidationError("Enter a valid phone number (8-15 characters, digits, spaces, +, -, () allowed).")
            if phone_number and User.objects.filter(phone_number=phone_number).exists():
                raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)
        return cleaned_data

class UserEditForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        label="Full Name",
        help_text=""  
    )
    blur_profile_photo = forms.BooleanField(
        required=False,
        label="Blur my profile photo",
        help_text="If checked, your profile photo will be blurred for privacy."
    )
    class Meta:
        model = User
        fields = ['full_name', 'email', 'date_of_birth',  'phone_number', 'profile_photo', 'blur_profile_photo', 'password']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Optional'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields.values():
            field.required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = User.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            if not re.match(r'^\+?[\d\s\-\(\)]{8,15}$', phone_number):
                raise forms.ValidationError("Enter a valid phone number (8-15 characters, digits, spaces, +, -, () allowed).")
            qs = User.objects.filter(phone_number=phone_number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)
        return cleaned_data