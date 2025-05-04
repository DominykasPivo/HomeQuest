from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from myapp.services import ensure_user_has_2fa

User = get_user_model()

class Command(BaseCommand):
    help = 'Enables 2FA for all existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        count = 0
        
        for user in users:
            ensure_user_has_2fa(user)
            count += 1
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully enabled 2FA for {count} users')
        )