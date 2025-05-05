from django.db import models
from django.utils import timezone
from user_management.models import Seller

# Keep the original inheritance structure
class GoldSeller(Seller):
    class Meta:
        db_table = 'goldseller'


    SUBSCRIPTION_TYPES = [
        ('basic', 'Basic'),
        ('gold', 'Gold'),
    ]
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES, default='basic')
    subscription_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    subscription_end_date = models.DateField(blank=True, null=True)

    def is_subscription_active(self):
        if self.subscription_plan == 'basic':
            return False
        if self.subscription_end_date and self.subscription_end_date >= timezone.now().date():
            return True
        return False

    def __str__(self):
        return f"GoldSeller: {self.email} ({self.subscription_type}, {self.subscription_plan})"