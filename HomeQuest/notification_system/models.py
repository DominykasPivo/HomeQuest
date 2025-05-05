from django.db import models
from django.utils import timezone
from user_management.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.message[:30]}... for {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']