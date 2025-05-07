#Test file for property_management
# To run : python3 manage.py test property_management
#There are 5 tests in this file, each test a certain function from the property management section
# Each test is named and explained below

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from .models import Property, Comment, PropertyLike
from user_management.models import Seller, User
from .forms import PropertyForm, CommentForm

class PropertyManagementTests(TestCase):
    def setUp(self):
        self.seller = Seller.objects.create(
            email='seller@test.com',
            password='TestPass123!',
            full_name='Test Seller',
            date_of_birth='1990-01-01',
            consent_to_share_location=True
        )
        
        self.user = User.objects.create(
            email='user@test.com',
            password='TestPass123!',
            full_name='Test User',
            date_of_birth='1990-01-01',
            consent_to_share_location=True
        )

        self.property_data = {
            'seller': self.seller,
            'location': 'Test Location',
            'map_location': '123,456',
            'price': Decimal('100000.00'),
            'size': Decimal('150.00'),
            'room_num': 3,
            'property_type': 'residential',
            'listing_type': 'for_sale',
            'duration': 0,
        }

    # Tests the function of creating a property
    def test_create_property(self):
        property = Property.objects.create(**self.property_data)
        self.assertEqual(property.location, 'Test Location')
        self.assertEqual(property.price, Decimal('100000.00'))
        self.assertEqual(property.seller, self.seller)
        self.assertFalse(property.is_verified)

    # Tests if the property data is valid
    def test_property_form_validation(self):
        form = PropertyForm(data={
            'location': 'Test Location',
            'map_location': '123,456',
            'price': '100000.00',
            'size': '150.00',
            'room_num': 3,
            'property_type': 'residential',
            'listing_type': 'for_sale',
            'duration': 0
        })
        self.assertTrue(form.is_valid())

        # Test rental property requires duration
        form = PropertyForm(data={
            'location': 'Test Location',
            'map_location': '123,456',
            'price': '100000.00',
            'size': '150.00',
            'room_num': 3,
            'property_type': 'residential',
            'listing_type': 'for_rent',
            'duration': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)

    # Tests the comment on property function
    def test_property_comments(self):
        property = Property.objects.create(**self.property_data)
        
        comment = Comment.objects.create(
            property=property,
            user=self.user,
            text='Test comment'
        )
        
        self.assertEqual(comment.text, 'Test comment')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.property, property)
    
    # Tests the like a property function
    def test_property_likes(self):
        property = Property.objects.create(**self.property_data)
        
        like = PropertyLike.objects.create(
            property=property,
            user=self.user
        )
        
        self.assertEqual(PropertyLike.objects.count(), 1)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.property, property)

        # Test unique constraint
        with self.assertRaises(Exception):
            PropertyLike.objects.create(
                property=property,
                user=self.user
            )

class PropertyFormTests(TestCase):

    # Checks if the comments are valid and accepted, verifies empty comments
    def test_comment_form(self):
        form = CommentForm(data={
            'text': 'Test comment'
        })
        self.assertTrue(form.is_valid())

        form = CommentForm(data={
            'text': ''
        })
        self.assertFalse(form.is_valid())


