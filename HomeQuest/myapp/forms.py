from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'required'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'required'}))

    user_type = forms.ChoiceField(
        choices=[('buyer', 'Buyer'), ('seller', 'Seller')],
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'consent_to_share_location', 'full_name',
            'date_of_birth', 'email', 'password', 'confirm_password', 
            'phone_number', 'profile_photo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add 'required' attribute to mandatory fields
        self.fields['username'].widget.attrs.update({'required': 'required'})
        self.fields['consent_to_share_location'].widget.attrs.update({'required': 'required'})
        self.fields['full_name'].widget.attrs.update({'required': 'required'})
        self.fields['date_of_birth'].widget.attrs.update({'required': 'required'})
        self.fields['email'].widget.attrs.update({'required': 'required'})
        # Non-mandatory fields do not need 'required' attributes
        self.fields['phone_number'].widget.attrs.update({'placeholder': 'Optional'})
        self.fields['profile_photo'].widget.attrs.update({'placeholder': 'Optional'})

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
        
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone_number', 'profile_photo', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields.values():
            field.required = False