from django import forms
from .models import User, Property

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

    class Meta:
        model = User
        fields = [
            'full_name', 'consent_to_share_location',
            'date_of_birth', 'email', 'password', 'confirm_password',
            'phone_number', 'profile_photo'
        ]

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
        return cleaned_data
        
class UserEditForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        label="Full Name",
        help_text=""  
    )
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'profile_photo', 'password']
        widgets = {
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


class PropertyForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        label="Property Image",
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )

    class Meta:
        model = Property
        fields = [
            'location', 'map_location', 'price', 'size', 'room_num',
            'property_type', 'is_verified'
        ]