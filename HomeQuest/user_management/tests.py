# Test file for user managment
# To run : python3 manage.py test user_management
# There are 10 tests in this file. Each tests certain functions from user management section
# each test is named and explained belows


from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from datetime import date
from .models import Buyer, Seller
from .forms import UserRegistrationForm, UserEditForm
from PIL import Image
import io

User = get_user_model()

def create_test_image():
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), 'white')
    image.save(file, 'PNG')
    file.name = 'test.png'
    file.seek(0)
    return file

class UserManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.profile_url = reverse('profile')
        self.edit_profile_url = reverse('edit_profile')
        
        self.user_data = {
            'email': 'test@example.com',
            'full_name': 'Test User',
            'date_of_birth': '1990-01-01',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'consent_to_share_location': True,
            'user_type': 'buyer',
            'phone_number': '+1234567890'
        }

    # Test Registration for buyer (Unit Test)
    def test_register_buyer(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        self.assertTrue(Buyer.objects.filter(email='test@example.com').exists())
        
    # Test Registration for seller (Unit Test)
    def test_register_seller(self):
        self.user_data['user_type'] = 'seller'
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Seller.objects.filter(email='test@example.com').exists())

    # Tests the input validation during registration
    def test_register_validation(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='invalid-email').exists())

        invalid_data = self.user_data.copy()
        invalid_data['confirm_password'] = 'DifferentPass123!'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())
   
    # Tests profile page access and control (Unit Test)
    def test_profile_access(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User',
            date_of_birth='1990-01-01'
        )
        self.client.login(email='test@example.com', password='TestPass123!')
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)

    # Tests the entire profile updating process (Integration test)
    def test_edit_profile(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User',
            date_of_birth='1990-01-01',
            consent_to_share_location=True
        )
        self.client.login(email='test@example.com', password='TestPass123!')

        update_data = {
            'full_name': 'Updated Name',
            'phone_number': '+9876543210',
            'date_of_birth': '1991-01-01',
            'blur_profile_photo': 'true'
        }

        image_file = create_test_image()
        files_data = {
            'profile_photo': SimpleUploadedFile('test.png', image_file.getvalue())
        }

        response = self.client.post(self.edit_profile_url, data=update_data, files=files_data)
        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()
        self.assertEqual(user.full_name, 'Updated Name')
        self.assertEqual(user.phone_number, '+9876543210')
        self.assertTrue(user.blur_profile_photo)

    # Tests the complete email change process (Integration test)
    def test_edit_profile_with_email_change(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User',
            date_of_birth='1990-01-01',
            consent_to_share_location=True
        )
        self.client.login(email='test@example.com', password='TestPass123!')

        update_data = {
            'email': 'newemail@example.com',
        }

        response = self.client.post(self.edit_profile_url, data=update_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/2fa/')

    #Tests error where user cannot register with an email thats already being used (Unit Test)
    def test_duplicate_email_registration(self):
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='test@example.com').count(), 1)

    # Tests password strength and requirements (Unit Test)
    def test_password_validation(self):
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'short'
        invalid_data['confirm_password'] = 'short'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

        invalid_data['password'] = 'password123'
        invalid_data['confirm_password'] = 'password123'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

    # Tests phone number format validation
    def test_phone_number_validation(self):
        invalid_data = self.user_data.copy()
        invalid_data['phone_number'] = 'invalid-phone'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

# Tests the registration from validation
class UserRegistrationFormTests(TestCase):
    def test_form_validation(self):
        valid_data = {
            'email': 'test@example.com',
            'full_name': 'Test User',
            'date_of_birth': '1990-01-01',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'consent_to_share_location': True,
            'user_type': 'buyer',
            'phone_number': '+1234567890'
        }
        
        form = UserRegistrationForm(data=valid_data)
        self.assertTrue(form.is_valid())

        invalid_data = valid_data.copy()
        invalid_data['email'] = 'invalid-email'
        form = UserRegistrationForm(data=invalid_data)
        self.assertFalse(form.is_valid())

        invalid_data = valid_data.copy()
        invalid_data['confirm_password'] = 'DifferentPass123!'
        form = UserRegistrationForm(data=invalid_data)
        self.assertFalse(form.is_valid())

# Tests the profile editing form
class UserEditFormTests(TestCase):
    def test_edit_form_validation(self):
        User.objects.create_user(
            email='existing@example.com',
            password='TestPass123!',
            full_name='Existing User',
            date_of_birth='1990-01-01'
        )

        valid_data = {
            'full_name': 'Updated Name',
            'email': 'new@example.com',
            'date_of_birth': '1991-01-01',
            'phone_number': '+9876543210',
            'blur_profile_photo': True
        }

        form = UserEditForm(data=valid_data)
        self.assertTrue(form.is_valid())

        invalid_data = valid_data.copy()
        invalid_data['email'] = 'existing@example.com'
        form = UserEditForm(data=invalid_data)
        self.assertFalse(form.is_valid())

        invalid_data = valid_data.copy()
        invalid_data['phone_number'] = 'invalid-phone'
        form = UserEditForm(data=invalid_data)
        self.assertFalse(form.is_valid())
