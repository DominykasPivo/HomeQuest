from django.db import models
from django.contrib.auth.models import AbstractUser

class ToDoItem(models.Model):   #needs to be deleted later
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

class User(AbstractUser):
    ACCOUNT_TYPE_CHOICES = [
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
    ]

    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    consent_to_share_location = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)  # Ensure email is unique
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)  # Ensure phone number is unique
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.username


class UserInput(models.Model):  #needs to be deleted later
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text