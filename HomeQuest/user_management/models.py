from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, date_of_birth, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, date_of_birth=date_of_birth, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, date_of_birth, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, full_name, date_of_birth, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = 'user'
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    consent_to_share_location = models.BooleanField(default=False)
    
    
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        default='profile_photos/default-profile.png'
    )
    blur_profile_photo = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'date_of_birth', 'consent_to_share_location']

    def is_seller(self):
        return Seller.objects.filter(pk=self.pk).exists()

    def __str__(self):
        return self.email


class Buyer(User):
    class Meta:
        db_table = 'buyer'
    def __str__(self):
        return f"Buyer: {self.email}"

class Seller(User):
    class Meta:
        db_table = 'seller'
    def __str__(self):
        return f"Seller: {self.email}"