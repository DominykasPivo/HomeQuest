from django.db import models
from user_management.models import User, Seller

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
    class Meta:
        db_table = 'comment'

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class PropertyLike(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'propertylike'
        unique_together = ('property', 'user')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.user} likes {self.property}"