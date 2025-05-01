from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the custom user model.
    """
    def create_user(self, email, full_name, date_of_birth, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, date_of_birth=date_of_birth, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, date_of_birth, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, full_name, date_of_birth, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):  
    #Mandatory fields
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    consent_to_share_location = models.BooleanField(default=False)

    #Optional fields
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        default='profile_photos/default-profile.png'  # Use MEDIA_URL for the default path
    )
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)  


    objects = CustomUserManager()
    USERNAME_FIELD = 'email' # The field used for authentication is always unique
    REQUIRED_FIELDS = ['full_name', 'date_of_birth', 'consent_to_share_location']

    def is_seller(self):
        return Seller.objects.filter(pk=self.pk).exists()

    def __str__(self):
        return self.email


class Buyer(User):
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')

    def __str__(self):
        return f"Buyer: {self.email}"
    
class Seller(User):
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')

    def __str__(self):
        return f"Seller: {self.email}"
    

class GoldSeller(Seller):
    SUBSCRIPTION_PLANS = [
        ('basic', 'Basic'),
        ('gold', 'Gold'),
    ]

    #seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name='gold_seller_profile')
    subscription_end_date = models.DateField(blank=True, null=True)
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLANS, default='basic')

    def __str__(self):
        return f"GoldSeller: {self.email} ({self.subscription_plan})"
    

class Property(models.Model):
    PROPERTY_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ]
    LISTING_TYPES = [
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    ]

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='properties')
    property_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=255)
    map_location = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.DecimalField(max_digits=10, decimal_places=2)
    room_num = models.PositiveIntegerField()
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    listing_type = models.CharField(max_length=50, choices=LISTING_TYPES)
    duration = models.PositiveIntegerField(default=0)  # Duration in days
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    image_paths = models.JSONField(default=list, blank=True)
    verification_files = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Property {self.property_id} - {self.location}"
    
class Comment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments') # on_delete=models.CASCADE = it deletes the comment if the property is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class PropertyLike(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('property', 'user')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.user} likes {self.property}"


