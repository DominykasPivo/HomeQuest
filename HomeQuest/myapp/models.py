from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):  
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
        default=f'profile_photos/default-profile.png'  # Use MEDIA_URL for the default path
    )
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)  # Non-mandatory

    def __str__(self):
        return self.username


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')

    def __str__(self):
        return f"Buyer: {self.user.username}"
    
class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')

    def __str__(self):
        return f"Seller: {self.user.username}"
    

class GoldSeller(models.Model):
    SUBSCRIPTION_PLANS = [
        ('basic', 'Basic'),
        ('gold', 'Gold'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gold_seller_profile')
    subscription_end_date = models.DateField(blank=True, null=True)
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLANS)

    def __str__(self):
        return f"GoldSeller: {self.user.username} ({self.subscription_plan})"